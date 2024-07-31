from dotenv import load_dotenv
from openai import OpenAI
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os, sqlite3, json, requests
from django.db import connection
from django.views import View
from apps.travel.models import County, CountyImg
from apps.planrecommend.models import TripDate, TripWho
from django.conf import settings
import psycopg2

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
    
# preparing
class PreparingListView(View):
    """준비중 페이지를 렌더링하는 뷰"""
    template_name = 'preparing.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    

######################################################################

# GPT
load_dotenv()  # 환경 변수 파일 로드

OPENAI_API_KEY = os.getenv('OPENAI_KEY')
GPT_MODEL = "gpt-4-turbo"

client = OpenAI(api_key=OPENAI_API_KEY)

######################################################################

# sqlite 데이터베이스 연결
# conn = sqlite3.connect("triprecommend.db")
# print("AI일정추천 DB 성공적으로 실행했습니다")

# cursor = conn.cursor()  # 커서 생성

# # 기존 테이블 삭제
# cursor.execute('DROP TABLE IF EXISTS TripRecommend')

# 테이블 생성 (초기 생성하고 주석처리)
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS TripRecommend (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         city_name INTEGER,
#         date TEXT,
#         who TEXT,
#         concept_title TEXT,
#         concept_content TEXT,
#         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#         FOREIGN KEY (city_name) REFERENCES County(id),
#         FOREIGN KEY (date) REFERENCES TripDate(id),
#         FOREIGN KEY (who) REFERENCES TripWho(id)
#     );
# ''')
# print("테이블 TripRecommend 생성 완료")

# # 데이터 삽입 (초기 생성하고 주석처리)
# trip_recommend_data = [
#     (1, '가평﹒양평', '당일치기', '혼자', '자연속 힐링 여행', '아름다운 남이섬에서 낭만을 느껴보세요'),
#     (2, '가평﹒양평', '1박 2일', '친구와', '액티비티 중심 여행', '수상레저와 레일바이크 및 서바이벌 게임을 즐겨보세요'),
#     (3, '가평﹒양평', '2박 3일', '연인과', '문화와 예술 미식 여행', '프랑스 마을 테마파크인 쁘띠프랑스와 양평 세미원에서 알콩달콩한 데이트 추억을 남겨보세요'),

#     (4, '강릉﹒속초 ', '1박 2일', '친구와', '해변과 자연탐사 여행', '영랑호와 경포해변에서 여유로운 해변산책과 수영을 즐겨보세요.'),
#     (5, '강릉﹒속초', '2박 3일', '연인과', '힐링과 스파 여행', '강릉의 찜질방에서 휴식 및 스파 체험과 정동진 해변에서 일몰과 로맨틱한 저녁 식사를 추천드려요.'),
#     (6, '강릉﹒속초', '3박 4일', '아이와', '자연과 동물 체험 여행', '다양한 해양 생물을 볼 수 있는 강릉 아쿠아리움과 속초 테디베어 전시관 탐방을 추천드려요.'),

#     (7, '경주', '1박 2일', '혼자', '역사와 문화 탐방 여행', '경주의 역사와 문화를 느낄 수 있는 경주의 대표적인 사찰인 불국사와 석굴암을 추천드려요.'),
#     (8, '경주', '2박 3일', '연인과', '예술과 문화체험 여행', '황리단길에서 다양한 갤러리를 탐방하고 개성있는 카페와 상점들을 둘러보며 경주의 문화를 느껴보세요.'),
#     (9, '경주', '3박 4일', '아이와', '놀이와 체험 중심 여행', '경주 국립박물관과 키즈월드에서 다양한 놀이기구와 체험활동을 즐겨보세요.'),

#     (10, '부산', '2박 3일', '친구와', '쇼핑과 미식 여행', '부산에는 여러 특색있는 시장이 많아요. 시장에서 다양한 먹거리와 쇼핑을 즐겨보세요.'),
#     (11, '부산', '3박 4일', '연인과', '아기자기한 문화 여행', '다양한 예술작품과 벽화들을 자랑하는 감천문화마을과 아름다운 풍경을 자랑하는 동백섬, APEC 나루공원의 풍경을 눈에 담아보세요.'),
#     (12, '부산', '4박 5일', '부모님과', '힐링과 자연 여행', '바다 위의 절경을 자랑하는 해동 용궁사와 바다 위를 걸을 수 있는 오륙도 스카이월드에서 특별한 경험을 남겨보세요.'),

#     (13, '여수﹒순천', '2박 3일', '친구와', '역사와 문화 여행', '전통 한옥과 한식을 체험할 수 있는 순천 낙안읍성과 여수 항일암을 추천드려요.'),
#     (14, '여수﹒순천', '3박 4일', '연인과', '미식과 문화 여행', '여수에는 다양한 식물과 멋진 바다경치를 감상할 수 있는 오동도가 있어요 신선한 해산물 요리와 함께 여수 전경을 감상해보세요.'),
#     (15, '여수﹒순천', '4박 5일', '부모님과', '자연과 힐링 여행', '다양한 테마로 꾸며진 순천만 국가정원과 아름다운 아경을 자랑하는 돌산대교 야경을 보며 힐링 가득한 여행을 추천드려요.'),

#     (16, '인천', '당일치기', '친구와', '문화와 예술 미식 여행', '프랑스 마을 테마파크인 쁘띠프랑스와 양평 세미원에서 알콩달콩한 데이트 추억을 남겨보세요'),
#     (17, '인천', '1박 2일', '연인과', '문화와 예술 미식 여행', '프랑스 마을 테마파크인 쁘띠프랑스와 양평 세미원에서 알콩달콩한 데이트 추억을 남겨보세요'),
#     (18, '인천', '2박 3일', '아이와', '테마파크와 탐험 여행', '인천 차이나타운과 인천 대공원에서 다양한 색감과 독특한 문화를 아이와 함께 즐겨보세요.'),

#     (19, '전주', '1박 2일', '친구와', '미식과 쇼핑 여행', '송도 트리플 스트리트에서 쇼핑과 맛있는 음식을 즐겨보세요.'),
#     (20, '전주', '2박 3일', '연인과', '여유로운 힐링 여행', '송도 센트럴파크에서 수상택시를 타고 여유로운 힐링을 경험하세요 송도 센트럴 근처 식당에서 식사도 추천드려요.'),
#     (21, '전주', '3박 4일', '부모님과', '문화와 예술 미식 여행', '프랑스 마을 테마파크인 쁘띠프랑스와 양평 세미원에서 알콩달콩한 데이트 추억을 남겨보세요'),

#     (22, '제주', '2박 3일', '혼자', '문화와 미식 여행', '제주 돌문화공원과 서귀포 매일올레시장에서는 제주의 독특한 문화를 경험할 수 있어요.'),
#     (23, '제주', 3박 4일', '친구와', '힐링과 자연 체험 여행', '한라산에서 가벼운 트레킹을 즐겨보세요. 우도에서는 자전거를 이용해 섬을 둘러볼 수 있어요 제주의 아름다운 풍겸을 느껴보세요.'),
#     (24, '제주', 4박 5일', '연인과', '로맨틱한 해변과 일몰 여행', '협재 해수욕장과 한림공원, 애월 카페거리를 추천드려요. 투명한 바다와 하얀 모래사장에서 로맨틱한 추억을 만들어보세요.'),

#     (25, '춘천﹒홍천 ', '당일치기', '아이와', '물놀이 테마파크 여행', '비발디 파크 오션월드에서 다양한 물놀이 시설과 스파를 즐길 수 있어요 홍천강에서의 카누와 카약 경험도 놓치지 마세요.'),
#     (26, '춘천﹒홍천 ', '1박 2일', '친구와', '액티비티와 자연 여행', '춘천 의암호 자전거길을 따라 자연 속에서의 여유로운 시간을 보내보세요. 홍천강에서는 카누나 카약을 타며 물놀이를 즐길 수 있어요.'),
#     (27, '춘천﹒홍천 ', '2박 3일', '연인과', '여유로운 힐링 여행', '소양강댐과 홍천강 수목원에서 아름다운 자연경관을 감상해보세요.'),

#     (30, '태안﹒당진﹒서산', '1박 2일', '친구과', '자연 탐험 여행', '몽산포 해수욕장에서 물놀이를 즐기며 일몰에는 바베큐를 즐겨보세요'),
#     (31, '태안﹒당진﹒서산', '2박 3일', '연인과', '역사와 힐링 여행', '역사적인 장소인 서산 해미읍성과 용현계곡에서 서산 풍경을 느껴보세요.'),
#     (32, '태안﹒당진﹒서산', '3박 4일', '아이와', '자연과 체험 중심 여행', '태안 안면도의 쥬라기 박물관과 당진 아그로랜드 태신목장에서 아이의 호기심을 자극해보세요.'),

#     (33, '통영﹒거제﹒남해', '2박 3일', '연인과', '섬 탐험 여행', '거제의 바람의 언덕에서 멋진 바다 경치를 감상해보세요 외도 보타니아는 섬 하나가 정원으로 꾸며져 있어 여유로운 산책을 즐길 수 있어요.'),
#     (34, '통영﹒거제﹒남해', '3박 4일', '아이와', '힐링과 자연 체험 여행', '통영 중앙시장에서 다양한 해산물을 구경하고 한려수도 조망 케이블카를 타고 아름다운 풍경을 감상해보세요.'),
#     (35, '통영﹒거제﹒남해', '4박 5일', '부모님과', '역사와 미식 여행', '남해 보리암에서 아름다운 풍경과 전통 한식을 맛보세요.'),
# ]

# cursor.executemany('''
# INSERT INTO TripRecommend (id, city_name, date, who, concept_title, concept_content)
# VALUES (?, ?, ?, ?, ?, ?);
# ''', trip_recommend_data)

# # 변경사항 저장
# conn.commit()

# # 데이터베이스 연결 객체를 받아 테이블 이름 목록을 반환
# def get_table_names(conn):
#     table_names = []
#     tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
#     for table in tables.fetchall():
#         table_names.append(table[0])
#     return table_names

# # 데이터베이스 연결 객체와 테이블 이름을 받아 해당 테이블의 컬럼 이름 목록을 반환
# def get_column_names(conn, table_name):
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

# DB 조회 함수 정의
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
print("AI여행컨셉추천 DB 성공적으로 실행했습니다")

cursor = conn.cursor()  # 커서 생성

######################################################################

# 테이블 생성 (초기 생성하고 주석처리)
# County 테이블 생성
create_county_table_query = '''
    CREATE TABLE IF NOT EXISTS County (
        id SERIAL PRIMARY KEY,
        city_name TEXT,
        first_town_name TEXT,
        second_town_name TEXT,
        third_town_name TEXT,
        title_image TEXT,
        area_code INTEGER,
        cigungu1 INTEGER,
        cigungu2 INTEGER,
        cigungu3 INTEGER
    );
'''
cursor.execute(create_county_table_query)
conn.commit()  # 변경 사항을 커밋

# TripDate 테이블 생성
create_tripdate_table_query = '''
    CREATE TABLE IF NOT EXISTS TripDate (
        id SERIAL PRIMARY KEY,
        date TEXT
    );
'''
cursor.execute(create_tripdate_table_query)
conn.commit()  # 변경 사항을 커밋

# TripWho 테이블 생성
create_tripwho_table_query = '''
    CREATE TABLE IF NOT EXISTS TripWho (
        id SERIAL PRIMARY KEY,
        who TEXT
    );
'''
cursor.execute(create_tripwho_table_query)
conn.commit()  # 변경 사항을 커밋

# TripRecommend 테이블 생성
create_triprecommend_table_query = '''
    CREATE TABLE IF NOT EXISTS TripRecommend (
        id SERIAL PRIMARY KEY,
        city_name INTEGER,
        date INTEGER,
        who INTEGER,
        concept_title TEXT,
        concept_content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (city_name) REFERENCES County(id),
        FOREIGN KEY (date) REFERENCES TripDate(id),
        FOREIGN KEY (who) REFERENCES TripWho(id)
    );
'''
cursor.execute(create_triprecommend_table_query)
conn.commit()
print("테이블 TripRecommend 생성 완료")

######################################################################

# 기존 테이블 데이터 삭제
cursor.execute("DELETE FROM chatbottravelinfo")
cursor.execute("DELETE FROM TripRecommend")
cursor.execute("DELETE FROM TripDate")
cursor.execute("DELETE FROM TripWho")
conn.commit()

# County 테이블의 데이터를 삭제
cursor.execute("DELETE FROM County")
conn.commit()

# 데이터 삽입 (초기 생성하고 주석처리)
# County 데이터 삽입
county_data = [
    (1, '가평﹒양평', '가평', '양평', 'None', 'None', 123, 1, 2, 3),
    (2, '강릉﹒속초', '강릉', '속초', 'None', 'None', 124, 1, 2, 3),
    (3, '경주', '경주', 'None', 'None', 'None', 125, 1, 2, 3),
    (4, '부산', '부산', 'None', 'None', 'None', 126, 1, 2, 3),
    (5, '여수﹒순천', '여수', '순천', 'None', 'None', 127, 1, 2, 3),
    (6, '인천', '인천', 'None', 'None', 'None', 128, 1, 2, 3),
    (7, '전주', '전주', 'None', 'None', 'None', 129, 1, 2, 3),
    (8, '제주', '제주', 'None', 'None', 'None', 130, 1, 2, 3),
    (9, '춘천﹒홍천', '춘천', '홍천', 'None', 'None', 131, 1, 2, 3),
    (10, '태안﹒당진﹒서산', '태안', '당진', '서산', 'None', 132, 1, 2, 3),
    (11, '통영﹒거제﹒남해', '통영', '거제', '남해', 'None', 133, 1, 2, 3)
]
insert_county_query = '''
    INSERT INTO County (id, city_name, first_town_name, second_town_name, third_town_name, title_image, area_code, cigungu1, cigungu2, cigungu3)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
'''
cursor.executemany(insert_county_query, county_data)
conn.commit()

# TripDate 데이터 삽입
tripdate_data = [
    (1, '당일치기'),
    (2, '1박 2일'),
    (3, '2박 3일'),
    (4, '3박 4일'),
    (5, '4박 5일')
]
insert_tripdate_query = '''
    INSERT INTO TripDate (id, date)
    VALUES (%s, %s)
'''
cursor.executemany(insert_tripdate_query, tripdate_data)
conn.commit()

# TripWho 데이터 삽입
tripwho_data = [
    (1, '혼자'),
    (2, '친구와'),
    (3, '연인과'),
    (4, '아이와'),
    (5, '부모님과')
]
insert_tripwho_query = '''
    INSERT INTO TripWho (id, who)
    VALUES (%s, %s)
'''
cursor.executemany(insert_tripwho_query, tripwho_data)
conn.commit()

# TripRecommend 데이터 삽입
trip_recommend_data = [
    (1, 1, 1, 1, '자연속 힐링 여행', '아름다운 남이섬에서 낭만을 느껴보세요'),
    (2, 1, 2, 2, '액티비티 중심 여행', '수상레저와 레일바이크 및 서바이벌 게임을 즐겨보세요'),
    (3, 1, 3, 3, '문화와 예술 미식 여행', '프랑스 마을 테마파크인 쁘띠프랑스와 양평 세미원에서 알콩달콩한 데이트 추억을 남겨보세요'),
    (4, 2, 2, 2, '해변과 자연탐사 여행', '영랑호와 경포해변에서 여유로운 해변산책과 수영을 즐겨보세요.'),
    (5, 2, 3, 3, '힐링과 스파 여행', '강릉의 찜질방에서 휴식 및 스파 체험과 정동진 해변에서 일몰과 로맨틱한 저녁 식사를 추천드려요.'),
    (6, 2, 4, 4, '자연과 동물 체험 여행', '다양한 해양 생물을 볼 수 있는 강릉 아쿠아리움과 속초 테디베어 전시관 탐방을 추천드려요.'),
    (7, 3, 2, 1, '역사와 문화 탐방 여행', '경주의 역사와 문화를 느낄 수 있는 경주의 대표적인 사찰인 불국사와 석굴암을 추천드려요.'),
    (8, 3, 3, 3, '예술과 문화체험 여행', '황리단길에서 다양한 갤러리를 탐방하고 개성있는 카페와 상점들을 둘러보며 경주의 문화를 느껴보세요.'),
    (9, 3, 4, 4, '놀이와 체험 중심 여행', '경주 국립박물관과 키즈월드에서 다양한 놀이기구와 체험활동을 즐겨보세요.'),
    (10, 4, 3, 2, '쇼핑과 미식 여행', '부산에는 여러 특색있는 시장이 많아요. 시장에서 다양한 먹거리와 쇼핑을 즐겨보세요.'),
    (11, 4, 4, 3, '아기자기한 문화 여행', '다양한 예술작품과 벽화들을 자랑하는 감천문화마을과 아름다운 풍경을 자랑하는 동백섬, APEC 나루공원의 풍경을 눈에 담아보세요.'),
    (12, 4, 5, 5, '힐링과 자연 여행', '바다 위의 절경을 자랑하는 해동 용궁사와 바다 위를 걸을 수 있는 오륙도 스카이월드에서 특별한 경험을 남겨보세요.'),
    (13, 5, 3, 2, '역사와 문화 여행', '전통 한옥과 한식을 체험할 수 있는 순천 낙안읍성과 여수 항일암을 추천드려요.'),
    (14, 5, 4, 3, '미식과 문화 여행', '여수에는 다양한 식물과 멋진 바다경치를 감상할 수 있는 오동도가 있어요 신선한 해산물 요리와 함께 여수 전경을 감상해보세요.'),
    (15, 5, 5, 5, '자연과 힐링 여행', '다양한 테마로 꾸며진 순천만 국가정원과 아름다운 아경을 자랑하는 돌산대교 야경을 보며 힐링 가득한 여행을 추천드려요.'),
    (16, 6, 1, 2, '문화와 예술 미식 여행', '프랑스 마을 테마파크인 쁘띠프랑스와 양평 세미원에서 알콩달콩한 데이트 추억을 남겨보세요'),
    (17, 6, 2, 3, '문화와 예술 미식 여행', '프랑스 마을 테마파크인 쁘띠프랑스와 양평 세미원에서 알콩달콩한 데이트 추억을 남겨보세요'),
    (18, 6, 3, 4, '테마파크와 탐험 여행', '인천 차이나타운과 인천 대공원에서 다양한 색감과 독특한 문화를 아이와 함께 즐겨보세요.'),
    (19, 7, 2, 2, '미식과 쇼핑 여행', '송도 트리플 스트리트에서 쇼핑과 맛있는 음식을 즐겨보세요.'),
    (20, 7, 3, 3, '여유로운 힐링 여행', '송도 센트럴파크에서 수상택시를 타고 여유로운 힐링을 경험하세요 송도 센트럴 근처 식당에서 식사도 추천드려요.'),
    (21, 7, 4, 5, '문화와 예술 미식 여행', '프랑스 마을 테마파크인 쁘띠프랑스와 양평 세미원에서 알콩달콩한 데이트 추억을 남겨보세요'),
    (22, 8, 3, 1, '문화와 미식 여행', '제주 돌문화공원과 서귀포 매일올레시장에서는 제주의 독특한 문화를 경험할 수 있어요.'),
    (23, 8, 4, 2, '힐링과 자연 체험 여행', '한라산에서 가벼운 트레킹을 즐겨보세요. 우도에서는 자전거를 이용해 섬을 둘러볼 수 있어요 제주의 아름다운 풍경을 느껴보세요.'),
    (24, 8, 5, 3, '로맨틱한 해변과 일몰 여행', '협재 해수욕장과 한림공원, 애월 카페거리를 추천드려요. 투명한 바다와 하얀 모래사장에서 로맨틱한 추억을 만들어보세요.'),
    (25, 9, 1, 4, '물놀이 테마파크 여행', '비발디 파크 오션월드에서 다양한 물놀이 시설과 스파를 즐길 수 있어요 홍천강에서의 카누와 카약 경험도 놓치지 마세요.'),
    (26, 9, 2, 2, '액티비티와 자연 여행', '춘천 의암호 자전거길을 따라 자연 속에서의 여유로운 시간을 보내보세요. 홍천강에서는 카누나 카약을 타며 물놀이를 즐길 수 있어요.'),
    (27, 9, 3, 3, '여유로운 힐링 여행', '소양강댐과 홍천강 수목원에서 아름다운 자연경관을 감상해보세요.'),
    (30, 10, 2, 2, '자연 탐험 여행', '몽산포 해수욕장에서 물놀이를 즐기며 일몰에는 바베큐를 즐겨보세요'),
    (31, 10, 3, 3, '역사와 힐링 여행', '역사적인 장소인 서산 해미읍성과 용현계곡에서 서산 풍경을 느껴보세요.'),
    (32, 10, 4, 4, '자연과 체험 중심 여행', '태안 안면도의 쥬라기 박물관과 당진 아그로랜드 태신목장에서 아이의 호기심을 자극해보세요.'),
    (33, 11, 3, 3, '섬 탐험 여행', '거제의 바람의 언덕에서 멋진 바다 경치를 감상해보세요 외도 보타니아는 섬 하나가 정원으로 꾸며져 있어 여유로운 산책을 즐길 수 있어요.'),
    (34, 11, 4, 4, '힐링과 자연 체험 여행', '통영 중앙시장에서 다양한 해산물을 구경하고 한려수도 조망 케이블카를 타고 아름다운 풍경을 감상해보세요.'),
    (35, 11, 5, 5, '역사와 미식 여행', '남해 보리암에서 아름다운 풍경과 전통 한식을 맛보세요.')
]

# TripRecommend 테이블에 데이터 삽입
insert_query = '''
    INSERT INTO TripRecommend (id, city_name, date, who, concept_title, concept_content)
    VALUES (%s, %s, %s, %s, %s, %s);
'''
cursor.executemany(insert_query, trip_recommend_data)
conn.commit()

######################################################################

# 데이터베이스 연결 객체를 받아 테이블 이름 목록을 반환
def get_table_names(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('triprecommend');")
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
                이 함수를 사용하여 사용자가 질문한 동행자, 여행기간, 여행도시의 여행컨셉제목과 내용에 답하세요.
                입력은 완전히 형성된 SQL 쿼리여야 합니다.

                city_name는 다음과 같이 매핑됩니다:
                가평﹒양평=1, 강릉﹒속초=2, 경주=3, 부산=4, 여수=5, 인천=6, 전주=7, 제주=8, 춘천﹒홍천=9, 태안﹒당진﹒서산=10, 통영﹒거제﹒남해=11, 포함﹒안동=12

                SQL 쿼리는 다음 스키마를 사용합니다:
                {database_schema_string}

                예시 쿼리:
                SELECT city_name, date, who, concept_title, concept_content
                FROM TripRecommend 
                WHERE city_name = 4;
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

# 사용자가 선택한 값을 URL 파라미터로 받아옴
def recommend(request):
    city = request.GET.get('city', '')  
    date = request.GET.get('date', '') 
    who = request.GET.get('who', '')   

    county = get_object_or_404(County, city_name=city)
    county_img = CountyImg.objects.filter(city_name=county).first()

    context = {
        'city': city,
        'date': date,
        'who': who,
        'county_img': county_img.image.url if county_img else None, 
    }

    return render(request, 'recommend.html', context)

# 질문에 대한 응답 처리
@csrf_exempt
def response(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    try:
        print(request.body)
        data = json.loads(request.body)
        user_query = data.get('user_query')

        messages = [
            {
                "role": "system",
                "content": "DB에서 조회된 결과만을 이용하여 응답하는 로봇이야"
            },
            {
                "role": "user",
                "content": user_query
            }
        ]

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        messages.append(response.choices[0].message)

        if response.choices[0].message.tool_calls:
            tool_calls = response.choices[0].message.tool_calls
            for tool_call in tool_calls:
                tool_call_id = tool_call.id
                tool_function_name = tool_call.function.name
                tool_query_string = json.loads(tool_call.function.arguments)['query']

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
                messages=messages
            )
            response_message = model_response_with_function_call.choices[0].message.content
        else:
            response_message = response.choices[0].message.content

        return JsonResponse({'message': response_message})
    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

