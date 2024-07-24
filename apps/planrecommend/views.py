from django.shortcuts import render
from .models import *
from django.views.generic import *
from django.http import JsonResponse
import os, json, requests, openai, sqlite3, logging
from apps.travel.models import County
from dotenv import load_dotenv
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
from rest_framework.decorators import api_view
from rest_framework.response import Response

# main(city)
class SelectCityListView(View):
    template_name = 'select_city.html'
    
# date
class SelectDateListView(View):
    template_name = 'select_date.html'

    def get(self, request, *args, **kwargs):
        selected_city = request.GET.get('city')  # URL 쿼리 파라미터에서 도시를 추출
        
        context = {
            'selected_city': selected_city,  # 선택된 도시
            'counties': County.objects.all(),
            'dates': TripDate.objects.all()
        }
        return render(request, self.template_name, context)
    
# who
class SelectWhoListView(View):
    template_name = 'select_who.html'

    def get(self, request, *args, **kwargs):
        context = {
            'counties': County.objects.all(),
            'dates': TripDate.objects.all(),
            'whose': TripWho.objects.all() 
        } 
        return render(request, self.template_name, context)

# style
class SelectStyleListView(View):
    template_name = 'select_style.html'

    def get(self, request, *args, **kwargs):
        context = {
            'counties': County.objects.all(),
            'dates': TripDate.objects.all(),
            'whose': TripWho.objects.all(),
            'styles': TripStyle.objects.all() 
        } 
        return render(request, self.template_name, context)
    
# plan
class SelectPlanListView(View):
    template_name = 'select_plan.html'

    def get(self, request, *args, **kwargs):
        context = {
            'counties': County.objects.all(),
            'dates': TripDate.objects.all(),
            'whose': TripWho.objects.all(),
            'styles': TripStyle.objects.all(), 
            'plans': TripPlan.objects.all() 
        } 
        return render(request, self.template_name, context)


# preparing
class PreparingListView(View):
    template_name = 'preparing.html'
    city = County.city_name

    recommend = TripRecommend.objects.get_or_create(
        city=city,
    )


# 관광지 API 호출 ######################################################################

# API 요청
def get_tour_data():
    load_dotenv()
    url = 'http://apis.data.go.kr/B551011/KorService1/areaBasedList1'  # 관광지 API URL (지역기반)
    AI_API_KEY = 'hfoOe068Vlj8Ikt91+xwEM5kDPK3NCkLGH9s6LdQ1yVetzxRw2yAQFyKv1eSy6mGK/EeCBfUDPq7dIEW5r+MxQ==' # 관광지 API
    # https://velog.io/@yeahg_dev/%EA%B3%B5%EA%B3%B5%EB%8D%B0%EC%9D%B4%ED%84%B0%ED%8F%AC%ED%84%B8-SERVICEKEYISNOTREGISTEREDERROR-%EC%9B%90%EC%9D%B8-%ED%8C%8C%ED%97%A4%EC%B9%98%EA%B8%B0

    area_code = {
        "서울": 1,
        "부산": 6,
        "인천": 2,
        "경기": 31,
        "강원": 32,
        "충북": 33,
        "충남": 34,
        "경북": 35,
        "경남": 36,
        "전북": 37,
        "전남": 38,
        "제주": 39
    }

    sigungu_code = {
        
    }
    
    # API 요청 url 파라미터
    base_params = {
    "serviceKey": AI_API_KEY,  # 인증키(필수)
    "MobileOS": "ETC",  # OS구분(필수)
    "MobileApp": "AppTest",  # 서비스명(필수)
    "arrange": "R",  # 생성일순
    "contentTypeId": 12,  # 관광타입(관광지)
    "_type": "json",  # 응답메세지 형식
    "areaCode": area_code,  # 지역코드
    "sigunguCode": sigungu_code  # 시군구코드
    
    # 지역코드 (서울:1, 부산:6, 대구:4, 인천:2, 광주:5, 대전:3, 울산:7, 세종:8, 경기:31, 강원:32, 충북:33, 충남:34, 경북:35, 견남:36, 전북:37, 전남:38, 제주:39)
    # "sigunguCode": 4,  # 시군구코드
    }

    all_data = []

    response = requests.get(url, params=base_params)
    try:
        data = response.json()
        if 'items' in data['response']['body']:
            all_data.extend(data['response']['body']['items']['item'])
    except ValueError:
        print("JSON 디코딩 오류: 응답 내용을 확인하세요.")
        print(response.text)  # 응답 내용 출력
        return []
    except KeyError:
        print("응답에 'items' 키가 없습니다.")
        return []

    return all_data
        

# 관광지 데이터를 DB에 저장
# def save_tour_data(items, city_name):
#     try:
#         county_instance = County.objects.get(name=city_name)
#     except County.DoesNotExist:
#         raise ValueError(f"County 모델에 '{city_name}' 값이 없습니다.")

#     for item in items:
#         CitySpotRecommend.objects.update_or_create(
#             content_id=item['contentid'],
#             defaults={
#                 'city_name': county_instance,  # 여기에서 County 인스턴스를 사용
#                 'title': item['title'],
#                 'address': item.get('addr1', ''),
#                 'img': item.get('firstimage', ''),
#                 'map_x': item['mapx'],
#                 'map_y': item['mapy']
#             }
#         )

def save_tour_data(self, items, city_name):
        county_instance = get_object_or_404(County, name=city_name)
        
        for item in items:
            if city_name in item.get('addr1', ''):
                CitySpotRecommend.objects.update_or_create(
                    content_id=item['contentid'],
                    defaults={
                        'city_name': county_instance,  # 여기에서 County 인스턴스를 사용
                        'title': item['title'],
                        'address': item.get('addr1', ''),
                        'img': item.get('firstimage', ''),
                        'map_x': item['mapx'],
                        'map_y': item['mapy']
                    }
                )

# 일정추천 gpt ######################################################################

# GPT_MODEL = "gpt-4-turbo"

# # OpenAI API 호출 함수
# def get_openai_response(messages):
#     try:
#         # ChatGPT API 호출
#         response = openai.ChatCompletion.create(
#             model=GPT_MODEL,
#             messages=messages
#         )
#         return response.choices[0].message['content']
#     except Exception as e:
#         print(f"Error calling OpenAI API: {str(e)}")
#         return "추천을 생성하는데 오류가 발생했습니다."
    
    
# 추천 결과 itinerary ######################################################################

@csrf_exempt
def itinerary(request):
#     # GET 요청만 처리
#     if request.method != 'GET':
#         return JsonResponse({'error': '잘못된 요청입니다.'}, status=400)

#     # URL 파라미터에서 쿼리 추출
#     city = request.GET.get('city')
#     date = request.GET.get('date')
#     who = request.GET.get('who')
#     style = request.GET.get('style')
#     plan = request.GET.get('plan')

#     if not city or not date or not who or not style or not plan:
#         return JsonResponse({'error': '매개변수를 찾을 수 없습니다.'}, status=400)
    

#     trip_recommendation = request.session.get('trip_recommendation', '추천 결과가 없습니다.')

#     # 데이터가 없을 경우, 400 Bad Request 응답
#     if trip_recommendation == '추천 결과가 없습니다.':
#         return JsonResponse({'error': '추천 결과가 없습니다.'}, status=400)

    
#     # DB에서 지역 정보 가져오기 (region, cigungu1, cigungu2, cigungu3)
#     region = trip_recommendation.get('region')
#     cigungu1 = trip_recommendation.get('cigungu1')
#     cigungu2 = trip_recommendation.get('cigungu2')
#     cigungu3 = trip_recommendation.get('cigungu3')

#     # DB에서 관광지 데이터 가져오기
#     if cigungu1:
#         city = County.objects.get(
#             area_code=region,
#             cigungu1=cigungu1
#         )
#     else:
#         city = County.objects.get(
#             area_code=region
#         )
    
#     tour_data = CitySpotRecommend.objects.filter(city_name=city)

#     # 관광지 데이터를 리스트로 변환
#     city_data = list(tour_data.values('content_id', 'title', 'address', 'img', 'map_x', 'map_y'))

#     # OpenAI API에 전달할 메시지 구성
#     messages = [
#         {
#             "role": "system",
#             "content": "너는 관광지 데이터를 기반으로 여행 일정을 추천해주는 로봇이야."
#         },
#         {
#             "role": "user",
#             "content": f"다음 관광지 정보를 바탕으로 여행 일정을 추천해줘: {city_data}"
#         }
#     ]

#     # OpenAI API 호출하여 응답 받기
#     openai_response = get_openai_response(messages)

#     # 추천 결과에 OpenAI 응답 추가
#     trip_recommendation['itinerary'] = openai_response

#     return render(request, 'itinerary.html', {'recommendation': trip_recommendation})

    return render(request, 'itinerary.html')

# 일정추천 gpt ######################################################################

# OPENAI_API_KEY = os.getenv('OPENAI_KEY')
# client = OpenAI(api_key=OPENAI_API_KEY)

# KAKAO_API_KEY = os.getenv('KAKAO_API_KEY')
# REST_API_KEY = os.getenv('REST_API_KEY')

# # sqlite 데이터베이스 연결
# conn = sqlite3.connect("chatbottravelinfo.db")
# print("AI일정추천 DB 성공적으로 실행했습니다")

# postgresql 데이터베이스 연결
# # pg_uri = f"postgresql+psycopg2://{DATABASES['USER']}:{DATABASES['PASSWORD']}@{DATABASES['HOST']}:{DATABASES['PORT']}/{DATABASES['NAME']}"  # DB 정보
# # db = SQLDatabase.from_uri(pg_uri)

# cursor = conn.cursor()  # 커서 생성

# # 테이블 생성 (초기 생성하고 주석처리)
# cursor.execute('''
#         CREATE TABLE IF NOT EXISTS CitySpotRecommend (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             city_name INTEGER,
#             content_id INTEGER,
#             title CHAR,
#             address TEXT,
#             img TEXT,
#             map_x Float,
#             map_y Float,
#             FOREIGN KEY (city_name) REFERENCES County(id)
# );
# ''')
# print("테이블 CitySpotRecommend 생성 완료")







    
# kakao map ######################################################################

# def kakao_map(request):
#     """지도와 관광지 정보를 렌더링하는 뷰"""
#     user_query = request.GET.get('user_query', '')  # URL 파라미터에서 쿼리 추출

#     if not user_query:
#         return JsonResponse({'error': 'Missing user_query parameter'}, status=400)

#     try:
#         # 관광지 데이터 가져오기
#         tour_data = get_tour_data(user_query)
#         # 관광지 데이터에서 위치 정보를 추출
#         places = tour_data.get('response', {}).get('body', {}).get('items', {}).get('item', [])

#         # 위치 정보를 포맷하여 템플릿으로 전달
#         locations = []
#         for place in places:
#             locations.append({
#                 'name': place.get('title'),
#                 'lat': place.get('mapx'),
#                 'lng': place.get('mapy'),
#             })

#         context = {
#             'kakao_api_key': KAKAO_API_KEY,
#             'locations': locations
#         }
#         return render(request, 'itinerary.html', context)
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return JsonResponse({'error': str(e)}, status=500)
    

