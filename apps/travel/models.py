from django.db import models

# 도시
class County(models.Model):
    city_name = models.CharField('도시명', max_length=10)  # 도시명
    first_town_name = models.CharField('첫번째 하위도시명', max_length=15)  # 첫번째 하위도시
    second_town_name = models.CharField('두번쨰 하위도시명', max_length=10, null=True, blank=True)  # 두번째 하위도시
    third_town_name = models.CharField('세번째 하위도시명', max_length=10, null=True, blank=True)  # 세번째 하위도시
    title_image = models.ImageField(upload_to='travel_title/%Y/%m',verbose_name='도시메인이미지',default='travel_title/default.jpg')
    area_code = models.IntegerField(null=True)
    cigungu1 = models.IntegerField(null=True,blank=True,default=0)
    cigungu2 = models.IntegerField(null=True,blank=True,default=0)
    cigungu3 = models.IntegerField(null=True,blank=True,default=0)
    def __str__(self):
        return self.city_name


# 도시 이미지
class CountyImg(models.Model):
    image = models.ImageField(upload_to='travel/%Y/%m',verbose_name='도시이미지')  # 이미지 경로 : travel/연도/월
    city_name = models.ForeignKey(County, on_delete=models.CASCADE)  # 도시명

    def __str__(self):
        return self.image.name   