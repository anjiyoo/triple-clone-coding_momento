from dotenv import load_dotenv
import os, sqlite3
from openai import OpenAI
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import connection

load_dotenv()  # 환경 변수 파일 로드

OPENAI_API_KEY = os.getenv('OPENAI_KEY')
GPT_MODEL = "gpt-4-turbo"
client = OpenAI(api_key=OPENAI_API_KEY)

# sqlite 데이터베이스 연결
conn = sqlite3.connect("chatbottravelinfo.db")
print("데이터베이스를 성공적으로 실행했습니다")

# postgresql 데이터베이스 연결
# # pg_uri = f"postgresql+psycopg2://{DATABASES['USER']}:{DATABASES['PASSWORD']}@{DATABASES['HOST']}:{DATABASES['PORT']}/{DATABASES['NAME']}"  # DB 정보
# # db = SQLDatabase.from_uri(pg_uri)

# cursor = conn.cursor()  # 커서 생성

# # 테이블 생성 (초기 생성하고 주석처리)
# cursor.execute('''
#         CREATE TABLE IF NOT EXISTS ChatbotTravelInfo (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             county_id INTEGER,
#             info_location TEXT,
#             info_weather TEXT,
#             info_tourist TEXT,
#             info_cultural TEXT,
#             info_food TEXT,
#             info_traffic TEXT,
#             info_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             FOREIGN KEY (county_id) REFERENCES County(id)
# );
# ''')
# print("테이블 ChatbotTravelInfo 생성 완료")

# # 데이터 삽입 (초기 생성하고 주석처리)
# travel_data = [
#     (1, '서울', '서울은 한반도 서남쪽에 위치합니다.', '서울 날씨는 봄과 가을에는 쾌적하고 맑은 날씨이며 여름에는 무더운 날이 많고 겨울에는 매우 추운 지역입니다.', '경복궁, 남산타워', '서울의 전통문화와 현대적인 매력을 동시에 느낄 수 있는 곳입니다.', '김치, 불고기', '지하철, 버스'),
#     (2, '부산', '부산은 대한민국 남동쪽에 위치한 대도시입니다.', '부산의 날씨는 서울보다 따뜻한 기후를 가지고 있으며, 해변가 지역으로 여름에는 서울보다 더울 수 있습니다 겨울은 비교적 따뜻합니다.', '해운대, 광안리 해수욕장', '부산의 해양 문화와 다양한 관광 명소를 즐길 수 있는 도시입니다.', '해물찜, 국밥', '지하철, 버스'),
#     (3, '제주', '제주는 대한민국 남서쪽 해상에 위치한 대한민국 최대의 섬입니다.', '제주의 날씨 일교차가 적고 온화한 기후를 가졌습니다 여름은 비가 많고 습도가 높을 수 있습니다.', '한라산, 성산일출봉', '제주의 자연 풍경과 독특한 문화를 체험할 수 있는 곳입니다.', '해산물, 흑돼지구이', '버스, 택시'),
#     (4, '경주', '대한민국 동남쪽에 위치합니다.', '경주의 날씨는 계절별로 온도 차이가 큽니다.', '불국사, 첨성대', '경주의 역사적인 유적지와 문화재를 탐방할 수 있는 도시입니다.', '떡갈비, 황남빵', '버스, 택시'),
#     (5, '전주', '전주는 대한민국 서북쪽에 위치한 전라북도의 중심 도시입니다.', '전주의 날씨 봄과 가을에는 따뜻하고 쾌적한 날씨가 많습니다.', '한옥마을, 전주한지공예촌', '전주의 전통 문화와 전통 음식을 맛볼 수 있는 곳입니다.', '비빔밥, 전주막걸리', '버스, 택시')
# ]

# cursor.executemany('''
# INSERT INTO ChatbotTravelInfo (id, county_id, info_location, info_weather, info_tourist, info_cultural, info_food, info_traffic) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
# ''', travel_data)

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

tools = [
    {
        "type": "function",
        "function": {
            "name": "ask_database",
            "description": "이 함수를 사용하여 사용자가 질문한 지역의 지역위치, 지역날씨, 지역관광지, 지역문화, 지역음식, 지역교통에 관한 질문에 답하세요. 입력은 완전히 형성된 SQL 쿼리여야 합니다.",
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

                                county_id 조회를 원하는 도시,
                                info_location 도시 위치,
                                info_weather 도시 날씨,
                                info_tourist 도시 관광지,
                                info_cultural 도시 지역문화,
                                info_food 도시 음식,
                                info_traffic 도시 교통 입니다.
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


    conn = sqlite3.connect("chatbottravelinfo.db")

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

# chatbot main
def chatbot_main(request):
    return render(request, 'chatbot_main.html')


# 질문에 대한 응답 처리
@csrf_exempt
def chatbot_response(request):
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