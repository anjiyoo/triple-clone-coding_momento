from django.db import models

# 도시
class County(models.Model):
    city_name = models.CharField('도시그룹', max_length=10)  # 도시그룹
    first_town_name = models.CharField('첫번째 도시명', max_length=10)  # 첫번째 도시
    second_town_name = models.CharField('두번쨰 도시명', max_length=10, null=True, blank=True)  # 두번째 도시
    third_town_name = models.CharField('세번째 도시명', max_length=10, null=True, blank=True)  # 세번째 도시

    def __str__(self):
        return self.city_name

# 도시 이미지
class CountyImg(models.Model):
    image = models.ImageField(upload_to='travel/%Y/%m',verbose_name='도시이미지')  # 이미지 경로 : travel/연도/월
    city_name = models.ForeignKey(County, on_delete=models.CASCADE)  # 도시명

    def __str__(self):
        return self.image.name  