from django.db import models
from django.conf import settings
from apps.plan.models import Trip
# Create your models here.

class tag(models.Model):
    name = models.CharField(max_length=50)
    registered_date = models.DateTimeField(auto_now_add=True, verbose_name="등록시간")

    def __str__(self):
        return self.name
    
class diary(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    trip = models.OneToOneField(Trip,on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    content = models.TextField()
    image = models.ImageField(upload_to='diary/%Y/%m/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(tag,blank=True)

# 여행기 댓글
class DiaryComment(models.Model):
    diary = models.ForeignKey(diary, on_delete=models.CASCADE)  # 여행기 모델 외부키
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # 유저 모델 외부키
    diary_com_content = models.CharField(max_length=100)  # 댓글내용
    diary_com_like = models.IntegerField('좋아요', default=0)  # 좋아요
    diary_com_like_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='diary_liked_comments')  # 좋아요를 누른 회원 
    diary_com_date = models.DateTimeField('작성일', auto_now_add=True)  # 작성일 

    def __str__(self):
        return self.diary_com_content