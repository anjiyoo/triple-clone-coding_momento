from django.db import models
from apps.travel.models import County

# 챗봇
class ChatbotTravelInfo(models.Model):
    county = models.ForeignKey(County, on_delete=models.CASCADE, verbose_name='도시')  # 도시 모델 외부키
    info_location = models.TextField('지역위치')  
    info_weather = models.TextField('지역날씨')  
    info_tourist = models.TextField('지역관광지') 
    info_cultural = models.TextField('지역문화')  
    info_food = models.TextField('지역음식')  
    info_traffic = models.TextField('지역교통')  
    info_date = models.DateTimeField('작성일', auto_now_add=True)  # 작성일
    
    def __str__(self):
        return self.info_location 
        