from django.db import models
from apps.plan.models import CitySpot
from django.conf import settings
from django.db import models

class CompanyTour(models.Model):
    company_id = models.AutoField(primary_key=True)  # 업체 id
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    city = models.ForeignKey(CitySpot, on_delete=models.CASCADE)  # 도시 id
    company_name = models.CharField(max_length=100)  # 업체명
    phone_number = models.CharField(max_length=15)  # 전화번호
    business_number = models.CharField(max_length=50)  # 사업자 번호
    registration_date = models.DateField()  # 가입일

    def __str__(self):
        return self.company_name

class TourInfo(models.Model):
    tour_id = models.AutoField(primary_key=True)  # 투어 id
    tour_name = models.CharField(max_length=100)  # 투어이름
    tour_description = models.TextField()  # 투어 설명
    representative_price = models.DecimalField(max_digits=10, decimal_places=2)  # 대표가격
    tour_type = models.CharField(max_length=50)  # 투어타입
    company = models.ForeignKey(CompanyTour, on_delete=models.CASCADE)  # 업체 id

    def __str__(self):
        return self.tour_name

class ReservationPersonTour(models.Model):
    representative_reservation_id = models.AutoField(primary_key=True)  # 대표예약자 id
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # 예약자이름
    name_english = models.CharField(max_length=100)  # 예약자이름(영문)
    email = models.EmailField()  # 예약자 email
    phone_number = models.CharField(max_length=15)  # 예약자 전화번호
    country_code = models.CharField(max_length=10)  # 예약자 국가번호

    def __str__(self):
        return self.name

class ReservationInfoTour(models.Model):
    reservation_id = models.AutoField(primary_key=True)  # 예약 id
    option = models.ForeignKey('OptionsTour', on_delete=models.CASCADE)  # 옵션 id
    representative_reservation_person = models.ForeignKey(ReservationPersonTour, on_delete=models.CASCADE, related_name='representative_reservations')  # 대표예약자 id
    reservation_person = models.ForeignKey(ReservationPersonTour, on_delete=models.CASCADE, related_name='reservations')  # 예약자 id
    start_date = models.DateField()  # 투어시작일
    end_date = models.DateField()  # 투어종료일
    number_of_people = models.IntegerField()  # 명수
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # 총 금액
    reservation_confirmation_date = models.DateField()  # 예약확정날짜
    terms_agreed = models.BooleanField()  # 이용약관 동의 여부
    cancellation_policy_agreed = models.BooleanField()  # 취소 약관 동의 여부

class OptionsTour(models.Model):
    option_id = models.AutoField(primary_key=True)  # 옵션 id
    tour = models.ForeignKey(TourInfo, on_delete=models.CASCADE)  # 투어 id
    option_name = models.CharField(max_length=100)  # 옵션 이름
    option_description = models.TextField()  # 옵션 설명
    option_price = models.DecimalField(max_digits=10, decimal_places=2)  # 옵션 가격
    max_sales_quantity = models.IntegerField()  # 최대 판매 갯수
    sales_start_date = models.DateField()  # 판매 시작일
    sales_end_date = models.DateField()  # 판매 종료일
    cancellation_possible = models.BooleanField()  # 취소 가능 여부

class ScheduleTour(models.Model):
    schedule_id = models.AutoField(primary_key=True)  # 일정 id
    tour = models.ForeignKey(TourInfo, on_delete=models.CASCADE)  # 투어 id
    sales_start_date = models.DateField()  # 판매 가능 일자(시작)
    sales_end_date = models.DateField()  # 판매 가능 일자(종료)
    tour_date = models.DateField()  # 투어 날짜

class PhotoTour(models.Model):
    photo_id = models.AutoField(primary_key=True)  # 사진 id
    tour = models.ForeignKey(TourInfo, on_delete=models.CASCADE)  # 투어 id
    photo = models.ImageField(upload_to='tour_photos/')  # 투어 사진

class ReviewTour(models.Model):
    review_id = models.AutoField(primary_key=True)  # 리뷰 id
    tour = models.ForeignKey(TourInfo, on_delete=models.CASCADE)  # 투어 id
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    review_title = models.CharField(max_length=100)  # 리뷰 제목
    review_content = models.TextField()  # 리뷰 내용
    review_rating = models.IntegerField()  # 리뷰 별점
    review_date = models.DateField()  # 리뷰 작성일
