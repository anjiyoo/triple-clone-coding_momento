from dotenv import load_dotenv
from openai import OpenAI
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os, sqlite3, json, requests
from django.db import connection
from django.views import View
from .models import *

# main(city)
class SelectCityListView(View):
    """도시를 선택하는 페이지를 렌더링하는 뷰"""
    template_name = 'select_city.html'

    def get(self, request, *args, **kwargs):
        context = {
            'counties': County.objects.all()
            }
        return render(request, self.template_name, context)
    
# date
class SelectDateListView(View):
    """날짜를 선택하는 페이지를 렌더링하는 뷰"""
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
    """동행자를 선택하는 페이지를 렌더링하는 뷰"""
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
    """여행 스타일을 선택하는 페이지를 렌더링하는 뷰"""
    template_name = 'select_style.html'

    def get(self, request, *args, **kwargs):
        context = {
            'counties': County.objects.all(),
            'dates': TripDate.objects.all(),
            'whose': TripWho.objects.all(),
            'styles': TripStyle.objects.all() 
        } 
        return render(request, self.template_name, context)
    
    
# itinerary
def itinerary(request):
    """추천 결과 페이지를 렌더링하는 뷰"""
    trip_recommendation = request.session.get('trip_recommendation', '추천 결과가 없습니다.')
    
    # 데이터가 없을 경우, 400 Bad Request 응답
    if trip_recommendation == '추천 결과가 없습니다.':
        return JsonResponse({'error': '추천 결과가 없습니다.'}, status=400)
    
    return render(request, 'itinerary.html', {'recommendation': trip_recommendation})

######################################################################

# GPT
load_dotenv()  # 환경 변수 파일 로드

OPENAI_API_KEY = os.getenv('OPENAI_KEY')
GPT_MODEL = "gpt-4-turbo"

client = OpenAI(api_key=OPENAI_API_KEY)

# sqlite 데이터베이스 연결
conn = sqlite3.connect("triprecommend.db")
print("AI일정추천 DB 성공적으로 실행했습니다")

# postgresql 데이터베이스 연결
# # pg_uri = f"postgresql+psycopg2://{DATABASES['USER']}:{DATABASES['PASSWORD']}@{DATABASES['HOST']}:{DATABASES['PORT']}/{DATABASES['NAME']}"  # DB 정보
# # db = SQLDatabase.from_uri(pg_uri)

# cursor = conn.cursor()  # 커서 생성

# # 테이블 생성 (초기 생성하고 주석처리)
# cursor.execute('''
#         CREATE TABLE IF NOT EXISTS TripRecommend (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             city_name INTEGER,
#             date INTEGER,
#             who INTEGER,
#             style INTEGER,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             FOREIGN KEY (city_name) REFERENCES County(id),
#             FOREIGN KEY (date) REFERENCES TripDate(id),
#             FOREIGN KEY (who) REFERENCES TripWho(id),
#             FOREIGN KEY (style) REFERENCES TripStyle(id),
# );
# ''')
# print("테이블 TripRecommend 생성 완료")

# # 데이터 삽입 (초기 생성하고 주석처리)
# trip_recommend_data = [
#     (1, '가평﹒양평 ', '당일치기.', '혼자', '자연'),
#     (2, '가평﹒양평 ', '1박2일.', '친구와', '레포츠'),
#     (3, '가평﹒양평 ', '2박3일.', '연인과', '음식'),

#     (4, '강릉﹒속초 ', '1박2일.', '혼자', '자연'),
#     (5, '강릉﹒속초 ', '2박3일.', '친구와', '음식'),

#     (6, '경주', '1박2일', '아이와', '자연'),
#     (7, '경주', '2박3일', '연인과', '문화'),

#     (8, '부산', '2박3일', '친구과', '자연'),
#     (9, '부산', '3박4일', '연인과', '문화'),
#     (10, '부산', '4박5일', '부모님과', '음식'),

#     (11, '여수﹒순천', '2박3일', '연인과.', '자연'),
#     (12, '여수﹒순천', '3박4일', '부모님과.', '음식'),

#     (13, '인천', '당일치기', '친구과', '문화'),
#     (14, '인천', '1박2일', '아이와', '음식'),

#     (15, '전주', '1박2일', '아이와', '문화'),
#     (16, '전주', '2박3일', '부모님과', '음식'),

#     (17, '제주', '2박3일', '친구와', '자연'),
#     (18, '제주', '3박4일', '연인과', '문화'),
#     (19, '제주', '4박5일', '부모님과', '쇼핑'),

#     (20, '춘천﹒홍천', '1박2일', '혼자', '자연'),
#     (21, '춘천﹒홍천', '2박3일', '친구', '레포츠'),

#     (22, '태안﹒당진﹒서산', '1박2일', '연인과', '자연'),
#     (22, '태안﹒당진﹒서산', '2박3일', '아이와', '문화'),

#     (23, '통영﹒거제﹒남해', '2박3일', '연인과 ', '자연')
#     (23, '통영﹒거제﹒남해', '3박4일', '부모님과 ', '음식')
# ]

# cursor.executemany('''
# INSERT INTO TripRecommend (id, city_name, date, who, style) VALUES (?, ?, ?, ?, ?);
# ''', trip_recommend_data)

# # 변경사항 저장
# conn.commit()

######################################################################

# 데이터베이스 연결 객체를 받아 테이블 이름 목록을 반환
def get_table_names(conn):
    """테이블 이름 목록 반환"""
    table_names = []
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
    for table in tables.fetchall():
        table_names.append(table[0])
    return table_names

# 데이터베이스 연결 객체와 테이블 이름을 받아 해당 테이블의 컬럼 이름 목록을 반환
def get_column_names(conn, table_name):
    """필드 이름 목록 반환"""
    column_names = []
    columns = conn.execute(f"PRAGMA table_info('{table_name}');").fetchall()
    for col in columns:
        column_names.append(col[1])
    return column_names

# 데이터베이스 연결 객체를 받아 데이터베이스의 모든 테이블과 각 테이블의 컬럼 정보를 포함하는 사전 목록을 반환
def get_database_info(conn):
    """데이터베이스의 각 테이블에 대한 테이블 이름과 열을 포함하는 사전 목록을 반환"""
    table_dicts = []
    for table_name in get_table_names(conn):
        columns_names = get_column_names(conn, table_name)
        table_dicts.append({"table_name": table_name, "column_names": columns_names})
    return table_dicts

# ######################################################################

# 데이터베이스 스키마 정보를 문자열로 변환하여 출력
database_schema_string = "\n".join(
    [
        f"Table: {table['table_name']}\nColumns: {', '.join(table['column_names'])}"
        for table in get_database_info(conn)
    ]
)
conn.close()
print(database_schema_string)

# ######################################################################

# function call
tools = [
    {
        "type": "function",
        "function": {
            "name": "ask_database",
            "description": "이 함수를 사용하여 사용자가 선택한 도시, 날짜, 동행자, 여행스타일, 여행일정타입에 따라 여행일정을 추천하세요. 입력은 완전히 형성된 SQL 쿼리여야 합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": f"""
                                사용자의 질문에 답하기 위해 정보를 추출하는 SQL 쿼리입니다.
                                SQL은 다음 데이터베이스 스키마를 사용하여 작성되어야 합니다:
                                {database_schema_string}
                                쿼리는 JSON이 아닌 일반 텍스트로 반환되어야 합니다.

                                city_name 조회를 원하는 도시,
                                date 여행 날짜,
                                who 여행 동행자,
                                style 여행 스타일,
                                plan 여행일정타입,
                                """,
                    }
                },
                "required": ["query"],
            },
        }
    }
]

# ######################################################################

# 데이터베이스에서 정보를 요청하고 결과를 처리하는 기능을 제공
# DB 조회 함수 정의
def ask_database(query):
    """제공된 SQL 쿼리로 SQLite 데이터베이스를 쿼리하는 기능"""


    conn = sqlite3.connect("triprecommend.db")

    try:
        results = str(conn.execute(query).fetchall())
        conn.close()
    except Exception as e:
        results = f"query failed with error: {e}"
    return results

# ######################################################################

# # DB 조회결과를 통해 응답 생성
# tool_calls = response_message.tool_calls  # 모델의 응답에 도구 호출이 포함되어 있는지 확인

# if tool_calls:
#     # true인 경우 모델은 호출할 도구/함수의 이름과 인수를 반환
#     tool_call_id = tool_calls[0].id
#     tool_function_name = tool_calls[0].function.name
#     tool_query_string = eval(tool_calls[0].function.arguments)['query']

#     # 함수를 호출하고 결과를 검색, 메시지 목록에 결과 추가
#     if tool_function_name == 'ask_database':
#         results = ask_database(conn, tool_query_string)

#         messages.append({
#             "role":"tool",
#             "tool_call_id":tool_call_id,
#             "name": tool_function_name,
#             "content":results
#         })

#         # 메시지 목록에 함수 응답이 추가된 채팅 완료 API를 호출
#         model_response_with_function_call = client.chat.completions.create(
#             model="gpt-4-turbo",
#             messages=messages,
#         )  # 함수 응답을 볼 수 있는 모델로부터 새로운 응답을 얻음
#         print(model_response_with_function_call.choices[0].message.content)
#     else:
#         print(f"Error: function {tool_function_name} does not exist")
# else:
#     # 모델이 호출할 함수를 식별하지 못했습니다. 결과가 사용자에게 반환될 수 있습니다
#     print(response_message.content)


###################################################################### 

# 사용자가 선택한 값을 URL 파라미터로 받아옴
def recommend(request):
    # URL 파라미터에서 값을 가져옴
    city = request.GET.get('city', '')  
    date = request.GET.get('date', '') 
    who = request.GET.get('who', '')   
    style = request.GET.get('style', '') 

    context = {
        'city': city,
        'date': date,
        'who': who,
        'style': style,
    }

    return render(request, 'recommend.html', context)

# 질문에 대한 응답 처리
@csrf_exempt
def response(request):
    # POST 요청만 처리
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    try:
        data = json.loads(request.body)  # JSON 형식의 클라이언트 요청 가져오기
        user_query = data.get('user_query')  # 사용자의 질문 추출

        # ChatGPT 채팅 실행 
        messages = [
            {
                "role":"system",
                "content": "DB에서 조회된 결과만을 이용하여 응답하는 로봇이야"
            },
            {
                "role":"user",
                "content": user_query
            }
        ]

        # ChatGPT API 호출
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            tools= tools,
            tool_choice="auto"
        )

        messages.append(response.choices[0].message)  # response 객체에서 choices 리스트의 첫 번째 항목의 message 속성 값을 추가

        # DB 조회 결과를 통해 응답 생성
        if response.choices[0].message.tool_calls:
            tool_calls = response.choices[0].message.tool_calls
            tool_call_id = tool_calls[0].id
            tool_function_name = tool_calls[0].function.name
            tool_query_string = eval(tool_calls[0].function.arguments)['query']

            # 함수를 호출하고 결과를 검색, 메시지 목록에 결과 추가
            if tool_function_name == 'ask_database':
                results = ask_database(tool_query_string)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "name": tool_function_name,
                    "content": results
                })
                
                # 메시지 목록에 함수 응답이 추가된 채팅 완료 API를 호출
                model_response_with_function_call = client.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=messages,
                )  # 함수 응답을 볼 수 있는 모델로부터 새로운 응답을 얻음
                response_message = model_response_with_function_call.choices[0].message.content
            else:
                print(f"Error: function {tool_function_name} does not exist")
                return JsonResponse({'error': f"Unsupported function: {tool_function_name}"}, status=500)
        else:
            response_message = response.choices[0].message.content

        return JsonResponse({'message': response_message})
    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

