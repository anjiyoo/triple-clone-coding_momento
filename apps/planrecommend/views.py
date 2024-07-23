from django.shortcuts import render
from .models import *
from django.views.generic import *
from django.http import JsonResponse
import os, json, requests, openai
from apps.travel.models import County
from dotenv import load_dotenv
from openai import OpenAI
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

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
    
# planrecommend main
def rec_itinerary(request):
    return render(request, 'itinerary.html')


# 일정추천 gpt ######################################################################

load_dotenv()  # 환경 변수 파일 로드

OPENAI_API_KEY = os.getenv('OPENAI_KEY')
GPT_MODEL = "gpt-4-turbo"
API_KEY = os.getenv('API_KEY')  # 관광지 API
API_URL = 'http://apis.data.go.kr/B551011/KorService1/areaBasedList1'  # 관광지 API URL
KAKAO_API_KEY = os.getenv('KAKAO_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)

# 관광지 API 호출
def get_tour_data(query):
    """관광지 API를 호출하여 데이터를 가져오는 함수"""
    headers = {'Authorization': f'Bearer {API_KEY}'}
    params = {'query': query}
    response = requests.get(API_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API request failed with status code {response.status_code}")


# 여행일정추천
def generate_trip_recommendation(tour_data):
    """관광지 데이터를 기반으로 ChatGPT에서 여행일정을 추천받는 함수"""

    # ChatGPT 채팅 실행 
    messages = [
        {
            "role": "system",
            "content": "너는 관광지 데이터를 기반으로 여행 일정을 추천해주는 로봇이야."
        },
        {
            "role": "user",
            "content": f"다음 관광지 정보를 바탕으로 여행 일정을 추천해줘: {tour_data}"
        }
    ]
    
    # ChatGPT API 호출
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=messages
    )
    
    return response.choices[0].message['content']


# ChatGPT API 호출 함수
@csrf_exempt
def trip_recommend_response(request):
    # POST 요청만 처리
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    try:
        user_query = request.GET.get('user_query')  # URL 파라미터에서 쿼리 추출

        if not user_query:
            return JsonResponse({'error': 'Missing user_query parameter'}, status=400)

        # 관광지 데이터 가져오기
        tour_data = get_tour_data(user_query)
        
        # 관광지 데이터를 기반으로 ChatGPT에 질문하기
        trip_recommendation = generate_trip_recommendation(tour_data)
        
        return JsonResponse({'message': trip_recommendation})
    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

