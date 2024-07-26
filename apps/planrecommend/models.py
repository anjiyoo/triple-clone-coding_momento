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
    

    
# 관광지
class CitySpotRecommend(models.Model):
    city_name = models.ForeignKey(County, on_delete=models.CASCADE, related_name='rec_tour_spots')  # 도시 외부키 참조
    content_id = models.IntegerField(unique=True)  # 관광지 고유 id
    title = models.CharField(max_length=50)  # 관광지
    address = models.TextField()  # 주소
    img = models.ImageField(upload_to='planrecommend/img', blank=True, null=True)  # 이미지
    map_x = models.FloatField(default=0.0)  # 경도
    map_y = models.FloatField(default=0.0)  # 위도

    def __str__(self):
        return self.title
    


# 일정추천
class TripRecommend(models.Model):
    city_name = models.ForeignKey(County, on_delete=models.SET_NULL, null=True)  # 도시 외부키 참조
    date = models.ForeignKey(TripDate, on_delete=models.CASCADE, null=True)  # 여행기간 외부키 참조
    who = models.ForeignKey(TripWho, on_delete=models.CASCADE, null=True)  # 동행자 외부키 참조
    spot = models.ForeignKey(CitySpotRecommend, on_delete=models.CASCADE, null=True)  # 관광지 외부키 참조
    concept_title = models.CharField(max_length=50, default="")  # 컨셉 제목
    concept_content = models.TextField(default="")  # 컨셉 내용
    created_at = models.DateTimeField(auto_now_add=True)  # 생성일

    def __str__(self):
        return self.city_name.name


