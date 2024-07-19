from django.shortcuts import get_object_or_404, render 
from django.views.generic import ListView
from .models import Trip,Trip_style,CitySpot,DayPlan
from apps.travel.models import County
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests, json, os
from datetime import datetime, timedelta
from django.shortcuts import redirect
from django.http import JsonResponse
from django.db.models import F
from dotenv import load_dotenv

# API_KEY = settings.API_KEY

load_dotenv()  # 환경 변수 파일 로드

API_KEY = os.getenv('API_KEY') 
KAKAO_API_KEY = os.getenv('KAKAO_API_KEY')

# @api_view(['GET'])
def get_tour_data(region,cigungu1,cigungu2,cigungu3):
    url = 'http://apis.data.go.kr/B551011/KorService1/areaBasedList1'
    base_params = {
        'serviceKey':API_KEY,
        "MobileOS": "WIN",
        "MobileApp": "AppTest",
        "arrange": "R",
        "contentTypeId":12,
        "_type": "json",
        "numOfRows": 20,  # 한 번에 가져올 데이터 수
        "pageNo": 1,
        "areaCode": region,
        
    }
    all_data = []
    for sigungu in [cigungu1, cigungu2, cigungu3]:
        if not cigungu1:
            response = requests.get(url, params=base_params)
            if response.status_code == 200:
                data = response.json()
                # 필요한 데이터 추출 및 all_data에 추가
                if 'items' in data['response']['body']:
                    all_data.extend(data['response']['body']['items']['item'])
                    break
        if sigungu:  # sigungu 값이 있는 경우에만 요청
            params = base_params.copy()
            params["sigunguCode"] = sigungu
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                # 필요한 데이터 추출 및 all_data에 추가
                if 'items' in data['response']['body']:
                    all_data.extend(data['response']['body']['items']['item'])

    return all_data
    # response = requests.get(url, params=params)
    
    
    # return response.json()
def save_tour_data(region,cigungu1,cigungu2,cigungu3):
    data = get_tour_data(region,cigungu1,cigungu2,cigungu3)
   
    
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
# def update_tour_data(request, region):
#     save_tour_data(region)
    
    
#     context = {
#         'region': region,
#         'tour_spots': tour_spots
#     }
#     return render(request, 'tour_spots.html', context)

class CityList(ListView):
    model = County
    template_name = 'county_list.html' 

def days(request):
    if request.method == 'POST':
        city = get_object_or_404(County, city_name=request.POST['city'])
    return render(
        request,
        'days.html',
        {
            'city':city
        }
    )

def day_plan(request,region,cigungu1=0,cigungu2=0,cigungu3=0):
    
    if request.method == 'POST':
        user = request.user
        city = get_object_or_404(County, city_name=request.POST['city'])
        date = request.POST['datefilter'].split(' - ')
        start_date = date[0]
        end_date = date[1]
        who = request.POST['who']
        style = request.POST.getlist('style')

        new_trip,tf = Trip.objects.get_or_create(
            user=user,
            city=city,
            start_date=start_date,
            end_date=end_date,
            who=who,
        )
        if tf : 
            new_trip = Trip.objects.get(
                user=user,
                city=city,
                start_date=start_date,
                end_date=end_date,
                who=who,
            )
        # new_trip.save()
        # 날짜 계산
        day_cnt = (new_trip.end_date - new_trip.start_date).days
        week = {0:'월', 1:'화', 2:'수', 3:'목', 4:'금', 5:'토', 6:'일'}
        day = new_trip.start_date.weekday()
        days = [new_trip.start_date.strftime("%m.%d/"+week[day])]
        for i in range(1,day_cnt+1):
            new = new_trip.start_date + timedelta(days=i)
            new_week = new.weekday()
            days.append(new.strftime("%m.%d/"+week[new_week]))
        #origin day
        origin_day = [new_trip.start_date.strftime("%Y-%m-%d")]
        for i in range(1,day_cnt+1):
            new = new_trip.start_date + timedelta(days=i)
            origin_day.append(new.strftime("%Y-%m-%d"))
        days = zip(days,origin_day)

        for i in style:
            new_style,tf = Trip_style.objects.get_or_create(
                trip = new_trip,
                style = i
            )
            # new_style.save()
        save_tour_data(region,cigungu1,cigungu2,cigungu3)
        tour_spots = CitySpot.objects.filter(city__area_code=region)
        plan = DayPlan.objects.filter(trip=new_trip.id)
    return render(
        request,
        'day_plan.html',
        {
            'new_trip':new_trip,
            'style':style,
            'tour_spots': tour_spots,
            'days':days,
            'plan':plan,
            'KAKAO_API_KEY':settings.KAKAO_API_KEY
         }
    )

def add_plan(request):
    
    new_trip =  get_object_or_404(Trip, id=request.GET['trip_id'])
    new_day = request.GET['day']
    for id in request.GET['spot_content'].split(','):
        new_spot = get_object_or_404(CitySpot,content_id=id)
        dayplan,tf = DayPlan.objects.get_or_create(
            trip = new_trip,
            day = new_day,
            spot = new_spot
    )
    plan=[]
    for id in request.GET['spot_content'].split(','):
        new_spot = get_object_or_404(CitySpot,content_id=id)
        plan.append(list(DayPlan.objects.filter(trip=new_trip.id,spot=new_spot).annotate(title=F('spot__title'),address=F('spot__address')).values('title','address','trip','spot','memo','day'))[0])
    region = new_trip.city.area_code
    cigungu1 = new_trip.city.cigungu1
    cigungu2 = new_trip.city.cigungu2
    cigungu3 = new_trip.city.cigungu3
    return JsonResponse(plan,safe=False)

def plan(request):
    new_trip =  get_object_or_404(Trip, id=request.GET['trip_id'])
    plan = list(DayPlan.objects.filter(trip=new_trip.id).annotate(title=F('spot__title'),address=F('spot__address')).values('title','address','trip','spot','memo','day'))
    return JsonResponse(plan,safe=False)

def del_plan(request):
    del_trip =  get_object_or_404(Trip, id=request.GET['trip_id'])
    del_spot = get_object_or_404(CitySpot,id=request.GET['spot_id'])
    DayPlan.objects.filter(trip=del_trip,spot=del_spot).delete()
    plan=list(DayPlan.objects.filter(trip=del_trip).annotate(title=F('spot__title'),address=F('spot__address')).values('title','address','trip','spot','memo','day'))
    return JsonResponse(plan,safe=False)