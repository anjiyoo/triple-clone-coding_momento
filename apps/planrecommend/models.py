from django.db import models

# Create your models here.
from django.db import models
from apps.travel.models import County
from apps.userinfo.models import User


# 여행기간
class TripDate(models.Model):
    date = models.CharField(max_length=30)  # 여행기간

    def __str__(self):
        return self.date

    
# 동행자
class TripWho(models.Model):
    who = models.CharField(max_length=30)  # 동행자

    def __str__(self):
        return self.who
    

# 여행스타일
class TripStyle(models.Model):
    style = models.CharField(max_length=30)  # 여행스타일

    def __str__(self):
        return self.style    


# 여행일정
class TripPlan(models.Model):
    plan = models.CharField(max_length=30)  # 여행일정

    def __str__(self):
        return self.plan    


# 일정추천
class TripRecommend(models.Model):
    city_name = models.ForeignKey(County, on_delete=models.SET_NULL, null=True)  # 도시 외부키 참조
    date = models.ForeignKey(TripDate, on_delete=models.CASCADE, null=True)  # 여행기간 외부키 참조
    who = models.ForeignKey(TripWho, on_delete=models.CASCADE, null=True)  # 동행자 외부키 참조
    style = models.ForeignKey(TripStyle, on_delete=models.CASCADE, null=True)  # 스타일 외부키 참조
    plan = models.ForeignKey(TripPlan, on_delete=models.CASCADE, null=True)  # 여행일정 외부키 참조
    created_at = models.DateTimeField(auto_now_add=True)  # 생성일

    def __str__(self):
        return self.city_name.name
    


# 관광지
class CitySpotRecommend(models.Model):
    city_name = models.ForeignKey(County, on_delete=models.CASCADE, related_name='rec_tour_spots')  # 도시 외부키 참조
    title = models.CharField(max_length=50)  # 관광지
    address = models.TextField()  # 주소
    img = models.ImageField(upload_to='planrecommend/img', blank=True, null=True)  # 이미지
    content_id = models.IntegerField(unique=True)  # 관광지 고유 id
    map_x = models.FloatField(default=0.0)  # 경도
    map_y = models.FloatField(default=0.0)  # 위도

    def __str__(self):
        return self.title


# 날짜별 여행일정
class DayPlanRecommend(models.Model):
    trip = models.ForeignKey(TripRecommend,on_delete=models.CASCADE)  # 여행일정 외부키 참조
    spot = models.ForeignKey(CitySpotRecommend,on_delete=models.CASCADE)  # 관광지 외부키 참조
    day = models.DateField()  # 일자

    def __str__(self):
        return self.day
