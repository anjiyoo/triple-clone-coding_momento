from django.shortcuts import render
from .models import *
from django.views.generic import *
from django.http import JsonResponse
import os, json, requests, openai, sqlite3
from apps.travel.models import County
from dotenv import load_dotenv
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta

# main(city)
class SelectCityListView(View):
    template_name = 'select_city.html'

    def get(self, request, *args, **kwargs):
        context = {
            'counties': County.objects.all()
            }
        return render(request, self.template_name, context)
    
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
    

# 일정추천 gpt ######################################################################
load_dotenv()  # 환경 변수 파일 로드

API_KEY = os.getenv('API_KEY')  # 관광지 API
API_URL = 'http://apis.data.go.kr/B551011/KorService1/areaBasedList1'  # 관광지 API URL (지역기반)

OPENAI_API_KEY = os.getenv('OPENAI_KEY')
GPT_MODEL = "gpt-4-turbo"
KAKAO_API_KEY = os.getenv('KAKAO_API_KEY')
REST_API_KEY = os.getenv('REST_API_KEY')

# 관광지 API 호출
def get_tour_data(region, cigungu1, cigungu2, cigungu3):
    url = API_URL
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

# sqlite 데이터베이스 연결
conn = sqlite3.connect("cityspotrecommend.db")
print("AI일정추천 DB 성공적으로 실행했습니다")

# postgresql 데이터베이스 연결
# # pg_uri = f"postgresql+psycopg2://{DATABASES['USER']}:{DATABASES['PASSWORD']}@{DATABASES['HOST']}:{DATABASES['PORT']}/{DATABASES['NAME']}"  # DB 정보
# # db = SQLDatabase.from_uri(pg_uri)

# cursor = conn.cursor()  # 커서 생성





# 관광지 데이터를 DB에 저장
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
        CitySpotRecommend.objects.update_or_create(
            content_id=item['contentid'],
            defaults={
                'city_name': city,
                'title': item['title'],
                'address': item.get('addr1', ''),
                'img': item.get('firstimage', ''),
                'map_x': item['mapx'],
                'map_y': item['mapy']
            }
        )


# 추천 결과 itinerary ######################################################################

def itinerary(request):
    """추천 결과 페이지를 렌더링하는 뷰"""
    trip_recommendation = request.session.get('trip_recommendation', '추천 결과가 없습니다.')
    
    # 데이터가 없을 경우, 400 Bad Request 응답
    if trip_recommendation == '추천 결과가 없습니다.':
        return JsonResponse({'error': '추천 결과가 없습니다.'}, status=400)
    
    return render(request, 'itinerary.html', {'recommendation': trip_recommendation})


# 입력된 데이터를 통한 응답 처리 ######################################################################

@csrf_exempt
def trip_recommend_response(request):
    # GET 요청만 처리
    if request.method != 'GET':
        return JsonResponse({'error': '잘못된 요청입니다.'}, status=400)

    # URL 파라미터에서 쿼리 추출
    city = request.GET.get('city')
    date = request.GET.get('date')
    who = request.GET.get('who')
    style = request.GET.get('style')
    plan = request.GET.get('plan')

    if not city or not date or not who or not style or not plan:
        return JsonResponse({'error': '매개변수를 찾을 수 없습니다.'}, status=400)

    # ChatGPT 채팅 실행 
    messages = [
        {
            "role": "system",
            "content": "너는 관광지 데이터를 기반으로 여행 일정을 추천해주는 로봇이야."
        },
        {
            "role": "user",
            "content": f"다음 관광지 정보를 바탕으로 여행 일정을 추천해줘: {city_data}"
        }
    ]

    try:
        # ChatGPT API 호출
        response = openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=messages
        )
        return response.choices[0].message['content']
    except Exception as e:
        print(f"Error calling OpenAI API: {str(e)}")
        return "추천을 생성하는데 오류가 발생했습니다."

    
# kakao map ######################################################################

def kakao_map(request):
    """지도와 관광지 정보를 렌더링하는 뷰"""
    user_query = request.GET.get('user_query', '')  # URL 파라미터에서 쿼리 추출

    if not user_query:
        return JsonResponse({'error': 'Missing user_query parameter'}, status=400)

    try:
        # 관광지 데이터 가져오기
        tour_data = get_tour_data(user_query)
        # 관광지 데이터에서 위치 정보를 추출
        places = tour_data.get('response', {}).get('body', {}).get('items', {}).get('item', [])

        # 위치 정보를 포맷하여 템플릿으로 전달
        locations = []
        for place in places:
            locations.append({
                'name': place.get('title'),
                'lat': place.get('mapx'),
                'lng': place.get('mapy'),
            })

        context = {
            'kakao_api_key': KAKAO_API_KEY,
            'locations': locations
        }
        return render(request, 'itinerary.html', context)
    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
    

