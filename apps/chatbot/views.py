from dotenv import load_dotenv
import os, sqlite3
from openai import OpenAI
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import connection
from django.conf import settings
import psycopg2

load_dotenv()  # 환경 변수 파일 로드

OPENAI_API_KEY = os.getenv('OPENAI_KEY')
GPT_MODEL = "gpt-4-turbo"

client = OpenAI(api_key=OPENAI_API_KEY)

######################################################################

# # sqlite 데이터베이스 연결
# conn = sqlite3.connect("chatbottravelinfo.db")
# print("챗봇 DB 성공적으로 실행했습니다")


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
#     (1, '가평﹒양평 ', '가평과 양평은 경기도 북동부에 위치한 도시입니다.', '가평은 산간 지역에 위치해 있어 전반적으로 기온이 낮고 선선한 편입니다. 양평은 가평에 비해 상대적으로 기온이 높고 구름이 많은 편입니다.', '남이섬, 아침고요수목원, 쁘띠프랑스', '자연 친화적인 관광지로 유명하며 휴양지와 캠핑장이 많습니다.', '잣, 송어, 양평 두부, 산채비빔밥, 막국수', '경춘선 기차, 버스'),
#     (2, '강릉﹒속초', '강릉과 속초는 강원도 동해안 중부와 최북단에 위치한 도시입니다.', '강릉&속초 날씨는 동해안 지역의 온화한 기후롤 보이지만, 속초가 더 북쪽에 위치해 있어 기온가 강수량 등에 약간 차이가 있습니다.', '경포대, 정동진, 속초해수욕장, 설악산, 청초호, 영랑호', '동해안의 아름다운 자연경관과 다양한 문화유산과 행사를 체험할 수 있습니다.', '오징어순대, 물회, 장칼국수, 순두부', 'KTX, 버스'),
#     (3, '경주', '경주는 경상북도 동남부에 위치한 도시입니다.', '경주는 내륙에 위치하여 대륙성 기후의 특성을 보입니다. 사계절이 뚜렷하며, 여름은 덥고 겨울은 건조하고 춥습니다.', '불국사, 석굴암, 첨성대, 동궁과 월지, 황리단길', '경주는 신라의 수도였던 도시로, 신라시대의 역사적인 유적지와 문화재를 탐방할 수 있는 도시입니다.', '경주빵, 보문국밥, 불국사 떡, 오미자차', 'KTX, 버스, 항공'),
#     (4, '부산', '부산은 한반도 남동단에 위치하며, 한반도 가장 남쪽 지역에 위치한 대도시 입니다.', '부산의 날씨는 전반적으로 온화한 편이고 여름에는 고온 다습한 날씨, 겨울에는 건조하고 서늘한 날씨가 지속됩니다.', '해운대, 감천문화마을, 자갈치시장, 광안리, 태종대, 깡통시장', '부산은 대한민국 최대의 항구도시로 다양한 해양문화가 발달했으며 음식문화, 전통문화 둥 다양한 문화적 특색을 가지고 있습니다.', '활어회, 동래파전, 밀면, 돼지국밥, 양곱창, 낙곱새, 꼼장어', 'KTX, 지하철, 버스, 항공'),
#     (5, '여수﹒순천', '여수는 전라남도 남서부, 순천은 전라남도 중부에 위치한 도시입니다.', '여수는 온화한 해양성 기후를 보입니다. 연중 강수량이 많은 편이며, 특히 장마철과 태풍시기에 많은 비를 내립니다. 순천은 내륙에 위치한 도시로 대륙성 기후를 보입니다.', '여수 엑스포, 오동도, 낙안읍성, 순천만 습지, 돌산대교, 이순신대교', '여수와 순천은 전라남도 내에서도 자연경관이 뛰어난 지역으로 많은 관광객들이 찾는 주요 관광지 입니다.', '돌게장, 돌산갓김치, 낙지볶음, 꼬막정식, 쌈밥, 매실주', 'KTX, 버스, 항공'),
#     (6, '인천', '인천은 한반도 서쪽 해안에 있으며 서울의 서쪽에 위치한 도시입니다.', '인천은 기온의 변화가 큰 편이며 겨울에는 추운 날씨가 지속되는 특징이 있습니다.', '송도 센트럴파크, 인천 차이나타운, 월미도, 강화도, 인천대공원', '인천은 중국문화와 역사, 자연경관이 어우러진 다양성과 역동성이 공존하는 도시입니다.', '해산물, 짜장면, 순무김치, 바지락칼국수, 홍두께 순두부', '항공, 선박, 지하철'),
#     (7, '전주', '전주는 대한민국 서북쪽에 위치한 전라북도의 중심 도시입니다.', '전주의 날씨 봄과 가을에는 따뜻하고 쾌적한 날씨가 많습니다.', '한옥마을, 전동성당, 전주 향교, 경기전, 남부시장, 전주한지공예촌', '전주의 전통 문화와 전통 음식을 맛볼 수 있는 곳입니다.', '전주비빔밥, 전주막걸리, 한정식, 전병, 식혜, 콩나물국밥', 'KTX, 버스'),
#     (8, '제주', '제주는 한반도의 남쪽 끝에 위치한 대한민국 최대 섬 입니다.', '제주는 아열대 기후의 영향을 받아 사계절이 뚜렷한 편이며 섬 지형으로 인해 바람이 강한 편입니다.', '한라산, 성산일출봉, 김녕해변, 제주 올레길, 우도', '제주는 화산섬의 자연환경이 반영된 독특한 방언, 신화, 돌문화, 민속예술, 음식문화 등 다양한 전통문화를 가지고 있는 섬입니다.', '고기국수, 흑돼지, 해산물, 물회, 감귤, 오메기떡, 해장국', '항공, 선박'),
#     (9, '춘천﹒홍천', '춘천은 강원도 중부, 홍천은 강원도 영서 지역에 위치한 도시 입니다.', '춘천&홍천 날씨는 대륙성 기후의 영향을 받아 여름은 덥고 습하며 겨울은 춥고 눈이 많이 내립니다.', '소양강댐, 소양강 스카이워크, 닭갈비 골목, 홍천 자연휴양림, 평화의 댐', '홍천은 강원도 대표 농촌지역이며, 춘천은 강원도 중심지로 자연과 문화가 조화를 이루는 도시입니다.', '닭갈비, 토종 닭백숙, 막국수, 토마토, 산채비빔밥', '경춘선 기차, 버스'),
#     (10, '태안﹒당진﹒서산', '태안과 당진, 서산은 충청남도 서해안 중부 지역에 위치한 도시입니다.', '태안&당진&서산은 해양성 기후의 영향을 받아 연간 강수량이 많은 편이며 여름에는 고온 다습한 편이고 겨울철에는 기온이 낮고 눈이 많이 옵니다.', '안면도 국립공언, 신두리 해안사구, 당진 해미읍성, 당진 삽교호, 고대산 국립공원, 서산 갯벌, 부수산, 석림사', '태안&당진&서산은 자연경관, 역사문화유산, 향토 음식 등 다양한 문화적 자원을 보유하고 있습니다.', '해장국, 활어회, 장어구이, 보리밥, 해물탕, 생선구이', '버스, 자가용'),
#     (11, '통영﹒거제﹒남해', '통영과 거제, 남해는 경상남도 남부의 해안 지역에 위치한 도시입니다.', '통영&거제&남해는 온화한 해양성 기후를 보이며, 봄과 가을에는 맑고 선선한 날씨이며 여름에는 습하고 겨울에는 온화한 날씨입니다. ', '통영 해상케이블카, 통영 동피랑마을, 거제 해금강, 거제 자연휴양림, 거제 외도, 남해 독일마을, 남해 금산, 남해 미조항', '통영&거제&남해는 섬과 바다가 어우러진 아름다운 자연경관과 다양한 체험 활동을 할 수 있는 지역입니다.', '멸치회, 오징어회, 굴 구이, 해물파전, 꽃게탕, 멍게회, 장어구이, 멍게비빔밥', '버스, 선박')
# ]

# cursor.executemany('''
# INSERT INTO ChatbotTravelInfo (id, county_id, info_location, info_weather, info_tourist, info_cultural, info_food, info_traffic) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
# ''', travel_data)

# # 변경사항 저장
# conn.commit()

# # 데이터베이스 연결 객체를 받아 테이블 이름 목록을 반환
# def get_table_names(conn):
#     """테이블 이름 목록 반환"""
#     table_names = []
#     tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
#     for table in tables.fetchall():
#         table_names.append(table[0])
#     return table_names

# # 데이터베이스 연결 객체와 테이블 이름을 받아 해당 테이블의 컬럼 이름 목록을 반환
# def get_column_names(conn, table_name):
#     """필드 이름 목록 반환"""
#     column_names = []
#     columns = conn.execute(f"PRAGMA table_info('{table_name}');").fetchall()
#     for col in columns:
#         column_names.append(col[1])
#     return column_names

# # 데이터베이스 연결 객체를 받아 데이터베이스의 모든 테이블과 각 테이블의 컬럼 정보를 포함하는 사전 목록을 반환
# def get_database_info(conn):
#     """데이터베이스의 각 테이블에 대한 테이블 이름과 열을 포함하는 사전 목록을 반환"""
#     table_dicts = []
#     for table_name in get_table_names(conn):
#         columns_names = get_column_names(conn, table_name)
#         table_dicts.append({"table_name": table_name, "column_names": columns_names})
#     return table_dicts

# # DB 조회 함수 정의
# def ask_database(query):
#     conn = sqlite3.connect("triprecommend.db")
#     try:
#         results = str(conn.execute(query).fetchall())
#         conn.close()
#     except Exception as e:
#         results = f"query failed with error: {e}"
#     return results 

######################################################################

# postgresql 데이터베이스 연결
# 환경 변수에서 PostgreSQL 연결 정보 가져오기
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')

# 포트 값을 정수로 변환 
db_port = int(db_port)

# PostgreSQL 데이터베이스 연결
conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
)
print("Chatbot DB 성공적으로 실행했습니다")
print(conn)
cursor = conn.cursor()  # 커서 생성

######################################################################

# # 테이블 생성 (초기 생성하고 주석처리)
# # County 테이블 생성
# create_county_table_query = '''
#     CREATE TABLE IF NOT EXISTS County (
#         id SERIAL PRIMARY KEY,
#         city_name TEXT,
#         first_town_name TEXT,
#         second_town_name TEXT,
#         third_town_name TEXT,
#         title_image TEXT,
#         area_code INTEGER,
#         cigungu1 INTEGER,
#         cigungu2 INTEGER,
#         cigungu3 INTEGER
#     );
# '''
# cursor.execute(create_county_table_query)
# conn.commit()  # 변경 사항을 커밋

# # ChatbotTravelInfo 테이블 생성
# create_chatbottravelinfo_table_query = '''
#         CREATE TABLE IF NOT EXISTS ChatbotTravelInfo (
#             id SERIAL PRIMARY KEY,
#             county_id INTEGER,
#             info_location TEXT,
#             info_weather TEXT,
#             info_tourist TEXT,
#             info_cultural TEXT,
#             info_food TEXT,
#             info_traffic TEXT,
#             info_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             FOREIGN KEY (county_id) REFERENCES County(id)
#     );
# '''
# cursor.execute(create_chatbottravelinfo_table_query)
# conn.commit()
# print("테이블 ChatbotTravelInfo 생성 완료")

# ######################################################################

# # # 기존 테이블 데이터 삭제
# cursor.execute("DELETE FROM ChatbotTravelInfo")
# cursor.execute("DELETE FROM County")
# conn.commit()

# # 데이터 삽입 (초기 생성하고 주석처리)
# # County 데이터 삽입
# county_data = [
#     (1, '가평﹒양평', '가평', '양평', 'None', 'None', 123, 1, 2, 3),
#     (2, '강릉﹒속초', '강릉', '속초', 'None', 'None', 124, 1, 2, 3),
#     (3, '경주', '경주', 'None', 'None', 'None', 125, 1, 2, 3),
#     (4, '부산', '부산', 'None', 'None', 'None', 126, 1, 2, 3),
#     (5, '여수﹒순천', '여수', '순천', 'None', 'None', 127, 1, 2, 3),
#     (6, '인천', '인천', 'None', 'None', 'None', 128, 1, 2, 3),
#     (7, '전주', '전주', 'None', 'None', 'None', 129, 1, 2, 3),
#     (8, '제주', '제주', 'None', 'None', 'None', 130, 1, 2, 3),
#     (9, '춘천﹒홍천', '춘천', '홍천', 'None', 'None', 131, 1, 2, 3),
#     (10, '태안﹒당진﹒서산', '태안', '당진', '서산', 'None', 132, 1, 2, 3),
#     (11, '통영﹒거제﹒남해', '통영', '거제', '남해', 'None', 133, 1, 2, 3)
# ]
# insert_county_query = '''
#     INSERT INTO County (id, city_name, first_town_name, second_town_name, third_town_name, title_image, area_code, cigungu1, cigungu2, cigungu3)
#     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
# '''
# cursor.executemany(insert_county_query, county_data)
# conn.commit()

# # 데이터 삽입 (초기 생성하고 주석처리)
# # ChatbotTravelInfo 데이터 삽입
# travel_data = [
#     (1, 1, '가평과 양평은 경기도 북동부에 위치한 도시입니다.', '가평은 산간 지역에 위치해 있어 전반적으로 기온이 낮고 선선한 편입니다. 양평은 가평에 비해 상대적으로 기온이 높고 구름이 많은 편입니다.', '남이섬, 아침고요수목원, 쁘띠프랑스', '자연 친화적인 관광지로 유명하며 휴양지와 캠핑장이 많습니다.', '잣, 송어, 양평 두부, 산채비빔밥, 막국수', '경춘선 기차, 버스'),
#     (2, 2, '강릉과 속초는 강원도 동해안 중부와 최북단에 위치한 도시입니다.', '강릉&속초 날씨는 동해안 지역의 온화한 기후롤 보이지만, 속초가 더 북쪽에 위치해 있어 기온가 강수량 등에 약간 차이가 있습니다.', '경포대, 정동진, 속초해수욕장, 설악산, 청초호, 영랑호', '동해안의 아름다운 자연경관과 다양한 문화유산과 행사를 체험할 수 있습니다.', '오징어순대, 물회, 장칼국수, 순두부', 'KTX, 버스'),
#     (3, 3, '경주는 경상북도 동남부에 위치한 도시입니다.', '경주는 내륙에 위치하여 대륙성 기후의 특성을 보입니다. 사계절이 뚜렷하며, 여름은 덥고 겨울은 건조하고 춥습니다.', '불국사, 석굴암, 첨성대, 동궁과 월지, 황리단길', '경주는 신라의 수도였던 도시로, 신라시대의 역사적인 유적지와 문화재를 탐방할 수 있는 도시입니다.', '경주빵, 보문국밥, 불국사 떡, 오미자차', 'KTX, 버스, 항공'),
#     (4, 4, '부산은 한반도 남동단에 위치하며, 한반도 가장 남쪽 지역에 위치한 대도시 입니다.', '부산의 날씨는 전반적으로 온화한 편이고 여름에는 고온 다습한 날씨, 겨울에는 건조하고 서늘한 날씨가 지속됩니다.', '해운대, 감천문화마을, 자갈치시장, 광안리, 태종대, 깡통시장', '부산은 대한민국 최대의 항구도시로 다양한 해양문화가 발달했으며 음식문화, 전통문화 둥 다양한 문화적 특색을 가지고 있습니다.', '활어회, 동래파전, 밀면, 돼지국밥, 양곱창, 낙곱새, 꼼장어', 'KTX, 지하철, 버스, 항공'),
#     (5, 5, '여수는 전라남도 남서부, 순천은 전라남도 중부에 위치한 도시입니다.', '여수는 온화한 해양성 기후를 보입니다. 연중 강수량이 많은 편이며, 특히 장마철과 태풍시기에 많은 비를 내립니다. 순천은 내륙에 위치한 도시로 대륙성 기후를 보입니다.', '여수 엑스포, 오동도, 낙안읍성, 순천만 습지, 돌산대교, 이순신대교', '여수와 순천은 전라남도 내에서도 자연경관이 뛰어난 지역으로 많은 관광객들이 찾는 주요 관광지 입니다.', '돌게장, 돌산갓김치, 낙지볶음, 꼬막정식, 쌈밥, 매실주', 'KTX, 버스, 항공'),
#     (6, 6, '인천은 한반도 서쪽 해안에 있으며 서울의 서쪽에 위치한 도시입니다.', '인천은 기온의 변화가 큰 편이며 겨울에는 추운 날씨가 지속되는 특징이 있습니다.', '송도 센트럴파크, 인천 차이나타운, 월미도, 강화도, 인천대공원', '인천은 중국문화와 역사, 자연경관이 어우러진 다양성과 역동성이 공존하는 도시입니다.', '해산물, 짜장면, 순무김치, 바지락칼국수, 홍두께 순두부', '항공, 선박, 지하철'),
#     (7, 7, '전주는 대한민국 서북쪽에 위치한 전라북도의 중심 도시입니다.', '전주의 날씨 봄과 가을에는 따뜻하고 쾌적한 날씨가 많습니다.', '한옥마을, 전동성당, 전주 향교, 경기전, 남부시장, 전주한지공예촌', '전주의 전통 문화와 전통 음식을 맛볼 수 있는 곳입니다.', '전주비빔밥, 전주막걸리, 한정식, 전병, 식혜, 콩나물국밥', 'KTX, 버스'),
#     (8, 8, '제주는 한반도의 남쪽 끝에 위치한 대한민국 최대 섬 입니다.', '제주는 아열대 기후의 영향을 받아 사계절이 뚜렷한 편이며 섬 지형으로 인해 바람이 강한 편입니다.', '한라산, 성산일출봉, 김녕해변, 제주 올레길, 우도', '제주는 화산섬의 자연환경이 반영된 독특한 방언, 신화, 돌문화, 민속예술, 음식문화 등 다양한 전통문화를 가지고 있는 섬입니다.', '고기국수, 흑돼지, 해산물, 물회, 감귤, 오메기떡, 해장국', '항공, 선박'),
#     (9, 9, '춘천은 강원도 중부, 홍천은 강원도 영서 지역에 위치한 도시 입니다.', '춘천&홍천 날씨는 대륙성 기후의 영향을 받아 여름은 덥고 습하며 겨울은 춥고 눈이 많이 내립니다.', '소양강댐, 소양강 스카이워크, 닭갈비 골목, 홍천 자연휴양림, 평화의 댐', '홍천은 강원도 대표 농촌지역이며, 춘천은 강원도 중심지로 자연과 문화가 조화를 이루는 도시입니다.', '닭갈비, 토종 닭백숙, 막국수, 토마토, 산채비빔밥', '경춘선 기차, 버스'),
#     (10, 10, '태안과 당진, 서산은 충청남도 서해안 중부 지역에 위치한 도시입니다.', '태안&당진&서산은 해양성 기후의 영향을 받아 연간 강수량이 많은 편이며 여름에는 고온 다습한 편이고 겨울철에는 기온이 낮고 눈이 많이 옵니다.', '안면도 국립공언, 신두리 해안사구, 당진 해미읍성, 당진 삽교호, 고대산 국립공원, 서산 갯벌, 부수산, 석림사', '태안&당진&서산은 자연경관, 역사문화유산, 향토 음식 등 다양한 문화적 자원을 보유하고 있습니다.', '해장국, 활어회, 장어구이, 보리밥, 해물탕, 생선구이', '버스, 자가용'),
#     (11, 11, '통영과 거제, 남해는 경상남도 남부의 해안 지역에 위치한 도시입니다.', '통영&거제&남해는 온화한 해양성 기후를 보이며, 봄과 가을에는 맑고 선선한 날씨이며 여름에는 습하고 겨울에는 온화한 날씨입니다.', '통영 해상케이블카, 통영 동피랑마을, 거제 해금강, 거제 자연휴양림, 거제 외도, 남해 독일마을, 남해 금산, 남해 미조항', '통영&거제&남해는 섬과 바다가 어우러진 아름다운 자연경관과 다양한 체험 활동을 할 수 있는 지역입니다.', '멸치회, 오징어회, 굴 구이, 해물파전, 꽃게탕, 멍게회, 장어구이, 멍게비빔밥', '버스, 선박'),
#     # (12, 12, '포항과 안동, 포항는 경상남도 남부의 해안 지역에 위치한 도시입니다.', '포항&안동은 온화한 해양성 기후를 보이며, 봄과 가을에는 맑고 선선한 날씨이며 여름에는 습하고 겨울에는 온화한 날씨입니다.', '포항 호미곶, 안동 하회마을', '포항&안동은 바다가 아름다운 자연경관과 다양한 먹거리를 즐길 수 있는 지역입니다.', '고래고기, 상어고기, 안동소주, 한정식', '버스, 기차')
# ]

# # ChatbotTravelInfo 테이블에 데이터 삽입
# insert_query = '''
#     INSERT INTO ChatbotTravelInfo (id, county_id, info_location, info_weather, info_tourist, info_cultural, info_food, info_traffic)
#     VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
# '''
# cursor.executemany(insert_query, travel_data)
# conn.commit()

######################################################################

# 데이터베이스 연결 객체를 받아 테이블 이름 목록을 반환
def get_table_names(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('chatbottravelinfo');")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        print(table_names)
        return table_names


# # 데이터베이스 연결 객체와 테이블 이름을 받아 해당 테이블의 컬럼 이름 목록을 반환
def get_column_names(conn, table_name):
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';")
        columns = cursor.fetchall()
        if columns:
            return [column[0] for column in columns]
        else:
            return []

# 데이터베이스 연결 객체와 테이블 이름을 받아 해당 테이블의 컬럼 이름 목록을 반환
def get_database_info(conn):
    table_names = get_table_names(conn)
    table_dicts = []
    if table_names:  # table_names가 None이 아닌지 확인
        for table_name in table_names:
            columns = get_column_names(conn, table_name)
            table_info = {
                'table_name': table_name,
                'columns': columns
            }
            table_dicts.append(table_info)
            print(f"Table: {table_name}, Columns: {columns}")
    else:
        print("No tables found in the database.")
    print("table_dicts")
    print(table_dicts)
    return table_dicts

# ######################################################################

# 데이터베이스 스키마 정보를 문자열로 변환하여 출력
database_info = get_database_info(conn)
conn.close()

if database_info is not None:
    database_schema_string = "\n".join(
        [
            f"Table: {table['table_name']}\nColumns: {', '.join(table['columns'])}"
            for table in database_info
        ]
    )
    print("database_schema_string")
    print(database_schema_string)
else:
    database_schema_string = "No database info found."
    print(database_schema_string)

# ######################################################################

# function call
tools = [
    {
        "type": "function",
        "function": {
            "name": "ask_database",
            "description": f"""
                이 함수를 사용하여 사용자가 특정 지역에 대한 정보를 질문할 때 답변하세요. 
                SQL 쿼리를 사용하여 DB에서 위치, 날씨, 관광지, 문화, 음식, 교통 정보를 추출합니다.
                도시 이름은 고유한 county_id로 매핑됩니다.

                county_id 는 
                가평﹒양평=1, 강릉﹒속초=2, 경주=3, 부산=4, 여수=5, 인천=6, 전주=7, 제주=8, 춘천﹒홍천=9, 태안﹒당진﹒서산=10, 통영﹒거제﹒남해=11, 포함﹒안동=12

                info_location 는 위치
                info_weather 는 날씨
                info_tourist 는 관광지
                info_food 는 지역음식
                info_traffic 는 교통 정보

                SQL 쿼리는 다음 스키마를 사용합니다:
                {database_schema_string}


                예시 쿼리:
                SELECT county_id, info_location, info_weather, info_tourist, info_cultural, info_food, info_traffic 
                FROM ChatbotTravelInfo 
                WHERE county_id = 4;
                """,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "사용자의 질문에 답하기 위해 정보를 추출하는 SQL 쿼리입니다."
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
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = int(os.getenv('DB_PORT'))  # 포트 값을 정수로 변환
    
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )

    try:
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return str(results)
    except Exception as e:
        if conn:
            conn.close()
        return f"query failed with error: {e}"

# ######################################################################

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