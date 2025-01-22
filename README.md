
![momento 시연영상(배속)](https://github.com/user-attachments/assets/1a2f4c49-fa73-4f3b-ba2b-7143f852ee68)


# MOMENTO 
**MOMENTO**는 나만의 여행일정을 공유하고 여행상품을 예약&구매 할 수 있는 플랫폼으로
앱 트리플을 클론코딩한 Django 프로젝트입니다.

[**Team Repositories**](https://github.com/Travel-Itinerary-Platform/momento) 를 보려면 클릭하세요.

<br>

## 주요 개발 사항

**1.AI여행컨셉 추천**
- **ChatGPT API**를 이용한 RAG 기술을 바탕으로 여행 컨셉을 추천해줍니다.
- 사용자가 도시&여행기간&동행자를 선택하면 선택된 정보를 기반으로 관련 데이터를 조합해 문맥에 맞춰 여행 컨셉을 제시합니다.

<br>

**2.배낭톡 (커뮤니티 게시판)**
- 사용자 간의 정보를 공유하며 상호작용할 수 있는 커뮤니티 게시판 입니다.
- 작성된 게시글을 최신 기준으로 조회할 수 있습니다.
- 도시, 주제, 여행시기(월별)에 따라 게시글을 조회할 수 있습니다.
- 도시, 주제, 여행시기를 선택하여 게시글을 작성할 수 있습니다.
- 게시글&댓글 수정은 작성자만 가능합니다.
- 게시글&댓글 좋아요 및 좋아요 취소는 작성자만 가능합니다.

<br>

**3.지역정보 Chatbot**
- **ChatGPT API**를 이용한 RAG 기술을 바탕으로 지역정보에 관한 질의응답을 받을 수 있습니다.
- 여행지에 대한 지역정보를 제공하는 챗봇 입니다.

<br>

**4.홈페이지 (메인페이지)**
- 국내여행&여행시작 탭 구분
- **국내여행 탭**
    - 항공권 & 숙소 & 배낭톡 페이지로 이동합니다.
    - AI여행추천 이미지 베너 클릭 시, AI여행추천 페이지로 이동할 수 있습니다.
    - 도시별 여행기 게시글을 볼 수 있습니다.
- **여행시작 탭**
    - 도시에 관한 통합검색(숙소,배낭톡) 기능을 사용할 수 있습니다.
    - 항공권 & 숙소 & 챗봇 페이지로 이동합니다.
    - 배낭톡 게시판을 볼 수 있습니다.
    - Chatbot 기능을 사용할 수 있습니다.
    - 모멘토사용설명서 & 배낭톡 & AI여행추천 & Chatbot 이미지 베너 클릭 시, 각 페이지로 이동할 수 있습니다.
    - 도시별 여행기 게시글을 볼 수 있습니다.
- **토글메뉴**
    - 마이페이지로 이동할 수 있습니다.
    - 여행일정 작성 페이지로 이동할 수 있습니다.
    - 내 예약 페이지로 이동할 수 있습니다.
- **로그인**
    - Google 소셜로그인을 통해 회원가입할 수 있습니다.
    - 로그인 시, 토글메뉴가 로그아웃으로 변경되어 로그아웃을 사용할 수 있습니다.

<br>

**ChatGPT 코드 리뷰 워크플로우 스크립트 작성**
- GitHub Action은 통해 워크플로우 스크립트 작성

<br>

## ERD
[**ERD**](https://www.erdcloud.com/d/YX97eTZJkmhHMu6Gc) 를 보려면 클릭하세요.

<br>

## 설치 및 실행 방법
**1.저장소 클론**
```
git clone https://github.com/Travel-Itinerary-Platform/momento.git
cd MOMENTO
```

**2.가상환경 설치 및 실행**
```
python -m venv momento
source momento/bin/activate  # mac
source momento\Scripts\activate  # window
```

**3.필요한 패키지 설치**
```
pip install -r requirements.txt
```

**4.데이터베이스 마이그레이션**
```
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic 
```

**5.서버실행**
```
python manage.py runserver
```

<br>

## 크레딧
이 프로젝트는 다음과 같은 오픈소스패키지를 사용합니다.
- python
- Django
- PostgreSQL
- Bootstrap5

<br>

## GitHub
`@anjiyoo`  ·  `@ansghltjd`  ·  `@nyeonseoioio`  ·  `@yangchanghun`  ·  `@HalalGuys1232`