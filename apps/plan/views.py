from django.shortcuts import get_object_or_404, render 
from django.views.generic import ListView
from .models import Trip,Trip_style,CitySpot,DayPlan
from apps.travel.models import County
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests, json
from datetime import datetime, timedelta
from django.shortcuts import redirect
from django.http import JsonResponse
from django.db.models import F
import os
from dotenv import load_dotenv
load_dotenv()  # 환경 변수 파일 로드

API_KEY = os.getenv('API_KEY') 
KAKAO_API_KEY = os.getenv('KAKAO_API_KEY')
REST_API_KEY = os.getenv('REST_API_KEY')
# Create your views here.

class PlanList(ListView):
    model = Trip
    template_name = 'trip_list.html'
    ordering = '-pk'
# @api_view(['GET'])
# 특정 지역의 관광 데이터를 가져오는 함수
def get_tour_data(region, cigungu1, cigungu2, cigungu3):
    url = 'http://apis.data.go.kr/B551011/KorService1/areaBasedList1'
    # API 요청에 필요한 기본 매개변수 설정
    base_params = {
        'serviceKey': API_KEY,
        "MobileOS": "WIN",
        "MobileApp": "AppTest",
        "arrange": "R",
        "contentTypeId": 12,
        "_type": "json",
        "numOfRows": 20,  # 한 번에 가져올 데이터 수
        "pageNo": 1,
        "areaCode": region,
    }
    all_data = []
    # 각 시군구에 대해 데이터 요청
    for sigungu in [cigungu1, cigungu2, cigungu3]:
        if not cigungu1:
            # cigungu1이 없으면 전체 지역 데이터 요청
            response = requests.get(url, params=base_params)
            if response.status_code == 200:
                data = response.json()
                if 'items' in data['response']['body']:
                    all_data.extend(data['response']['body']['items']['item'])
                    break
        if sigungu:  # sigungu 값이 있는 경우에만 요청
            params = base_params.copy()
            params["sigunguCode"] = sigungu
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if 'items' in data['response']['body']:
                    all_data.extend(data['response']['body']['items']['item'])

    return all_data

# 관광 데이터를 데이터베이스에 저장하는 함수
def save_tour_data(region, cigungu1, cigungu2, cigungu3):
    data = get_tour_data(region, cigungu1, cigungu2, cigungu3)
    
    # 도시 정보 가져오기 또는 생성
    if cigungu1:
        city = County.objects.get(
            area_code=region,
            cigungu1=cigungu1
        )
    else:
        city = County.objects.get(
            area_code=region
        )
    # 각 관광지 데이터를 데이터베이스에 저장 또는 업데이트
    for item in data:
        CitySpot.objects.update_or_create(
            content_id=item['contentid'],
            defaults={
                'title': item['title'],
                'city': city,
                'address': item.get('addr1', ''),
                'image_url': item.get('firstimage', ''),
                'map_x': item['mapx'],
                'map_y': item['mapy']
            }
        )

# 도시 목록을 보여주는 ListView
class CityList(ListView):
    model = County
    template_name = 'county_list.html' 

# 여행 일정 설정 페이지를 렌더링하는 뷰 함수
def days(request):
    if request.method == 'POST':
        city = get_object_or_404(County, city_name=request.POST['city'])
        # 수정 버튼 경로
        try:
            trip = Trip.objects.get(id=request.POST['trip'])
        except:
            trip = None
    return render(
        request,
        'days.html',
        {
            'city': city,
            'trip': trip
        }
    )

# 일별 여행 계획을 생성하는 뷰 함수
def day_plan(request, region, cigungu1=0, cigungu2=0, cigungu3=0):
    if request.method == 'POST':
        user = request.user
        city = get_object_or_404(County, city_name=request.POST['city'])
        date = request.POST['datefilter'].split(' - ')
        start_date = date[0]
        end_date = date[1]
        who = request.POST['who']
        style = request.POST.getlist('style')
        
        # 수정 버튼 경로
        if request.POST['trip']:
            new_trip = Trip.objects.get(id=request.POST['trip'])
            new_trip.start_date = start_date
            new_trip.end_date = end_date
            who = who
            new_trip.save()
            new_trip = Trip.objects.get(id=request.POST['trip'])
        # 신규 생성
        else:
            new_trip, tf = Trip.objects.get_or_create(
                user=user,
                city=city,
                start_date=start_date,
                end_date=end_date,
                who=who,
            )
            if tf:
                new_trip = Trip.objects.get(
                    user=user,
                    city=city,
                    start_date=start_date,
                    end_date=end_date,
                    who=who,
                )

        # 날짜 계산
        day_cnt = (new_trip.end_date - new_trip.start_date).days
        week = {0:'월', 1:'화', 2:'수', 3:'목', 4:'금', 5:'토', 6:'일'}
        day = new_trip.start_date.weekday()
        days = [new_trip.start_date.strftime("%m.%d/"+week[day])]
        for i in range(1, day_cnt+1):
            new = new_trip.start_date + timedelta(days=i)
            new_week = new.weekday()
            days.append(new.strftime("%m.%d/"+week[new_week]))
        # origin day
        origin_day = [new_trip.start_date.strftime("%Y-%m-%d")]
        for i in range(1, day_cnt+1):
            new = new_trip.start_date + timedelta(days=i)
            origin_day.append(new.strftime("%Y-%m-%d"))
        days = zip(days, origin_day)
        
        # 기존 여행 스타일 삭제 후 새로 생성
        try:
            Trip_style.objects.get(trip=new_trip).delete()
        except:
            pass
        for i in style:
            new_style, tf = Trip_style.objects.get_or_create(
                trip=new_trip,
                style=i
            )
            if tf :
                style = Trip_style.objects.filter(trip=new_trip)
        
        # 관광 데이터 저장 및 조회
        save_tour_data(region, cigungu1, cigungu2, cigungu3)
        tour_spots = CitySpot.objects.filter(city__area_code=region)
        plan = DayPlan.objects.filter(trip=new_trip.id)

    if request.method == 'GET':
        new_trip = Trip.objects.get(id=request.GET['trip'])
        style = Trip_style.objects.filter(trip=request.GET['trip'])
        tour_spots = CitySpot.objects.filter(city__area_code=request.GET['area_code'])
        # 날짜 계산
        day_cnt = (new_trip.end_date - new_trip.start_date).days
        week = {0:'월', 1:'화', 2:'수', 3:'목', 4:'금', 5:'토', 6:'일'}
        day = new_trip.start_date.weekday()
        days = [new_trip.start_date.strftime("%m.%d/"+week[day])]
        for i in range(1, day_cnt+1):
            new = new_trip.start_date + timedelta(days=i)
            new_week = new.weekday()
            days.append(new.strftime("%m.%d/"+week[new_week]))
        # origin day
        origin_day = [new_trip.start_date.strftime("%Y-%m-%d")]
        for i in range(1, day_cnt+1):
            new = new_trip.start_date + timedelta(days=i)
            origin_day.append(new.strftime("%Y-%m-%d"))
        days = zip(days, origin_day)

        plan = DayPlan.objects.filter(trip=new_trip)
    return render(
        request,
        'day_plan.html',
        {
            'new_trip': new_trip,
            'style': style,
            'tour_spots': tour_spots,
            'days': days,
            'plan': plan,
            'KAKAO_API_KEY': KAKAO_API_KEY,
            'REST_API_KEY': REST_API_KEY
         }
    )

# 여행 계획에 관광지 추가하는 함수
def add_plan(request):
    new_trip = get_object_or_404(Trip, id=request.GET['trip_id'])
    new_day = request.GET['day']
    for id in request.GET['spot_content'].split(','):
        new_spot = get_object_or_404(CitySpot, content_id=id)
        dayplan, tf = DayPlan.objects.get_or_create(
            trip=new_trip,
            day=new_day,
            spot=new_spot
        )
   
    return JsonResponse({'success': True})

# 여행 계획에 메모 추가하는 함수
def add_memo(request):
    new_trip = get_object_or_404(Trip, id=request.POST['trip'])
    new_day = request.POST['add_day']
    new_memo = request.POST['memo']
    DayPlan.objects.create(trip=new_trip, day=new_day, memo=new_memo)
    return JsonResponse({'success': True})

# 여행 계획 조회 함수
def plan(request):
    new_trip = get_object_or_404(Trip, id=request.GET['trip_id'])
    if request.GET['day']:
        plan = list(DayPlan.objects.filter(trip=new_trip.id , day=request.GET['day']).annotate(
        title=F('spot__title'),
        address=F('spot__address')
    ).values('title', 'address', 'trip', 'spot', 'memo', 'day'))
    else:
        plan = list(DayPlan.objects.filter(trip=new_trip.id).annotate(
        title=F('spot__title'),
        address=F('spot__address')
    ).values('title', 'address', 'trip', 'spot', 'memo', 'day'))
    return JsonResponse(plan, safe=False)

# 여행 계획 삭제 함수
def del_plan(request):
    DayPlan.objects.filter(id=request.GET['dayPlan_id']).delete()
    return JsonResponse({'success': True})