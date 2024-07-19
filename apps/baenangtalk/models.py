from django.db import models
from apps.travel.models import County
from apps.userinfo.models import User

# 배낭톡 주제
class BaenangtalkSubject(models.Model):
    bae_sub_name = models.CharField('주제명', max_length=10)  # 배낭톡 주제

    def __str__(self):
        return self.bae_sub_name
    

# 배낭톡 여행시기
class BaenangtalkPeriod(models.Model):
    bae_month = models.DateField('월')  # 배낭톡 여행시기

    def __str__(self):
        return self.bae_month.strftime('%m')
    

# 배낭톡
class Baenangtalk(models.Model):
    county = models.ForeignKey(County, on_delete=models.CASCADE, verbose_name='도시')  # 도시 모델 외부키
    period = models.ForeignKey(BaenangtalkPeriod, on_delete=models.CASCADE, verbose_name='여행시기')  # 여행시기 모델 외부키
    subject = models.ForeignKey(BaenangtalkSubject, on_delete=models.CASCADE, verbose_name='주제')  # 주제 모델 외부키
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 유저 모델 외부키
    bae_title = models.CharField('제목', max_length=100)  # 배낭톡 제목
    bae_content = models.TextField('내용')  # 배낭톡 본문
    bae_img = models.ImageField('이미지', upload_to='baenangtalk/img')  # 배낭톡 이미지
    bae_like = models.IntegerField('좋아요', default=0)  # 배낭톡 좋아요
    bae_like_by = models.ManyToManyField(User, related_name='liked_posts')  # 좋아요 누른 회원
    bae_date = models.DateTimeField('작성일', auto_now_add=True)  # 작성일

    def __str__(self):
        return self.bae_title


# 배낭톡 댓글
class BaenangtalkComment(models.Model):
    bae = models.ForeignKey(Baenangtalk, on_delete=models.CASCADE)  # 배낭톡 모델 외부키
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 유저 모델 외부키
    bae_com_content = models.CharField(max_length=100)  # 댓글내용
    bae_com_like = models.IntegerField('좋아요', default=0)  # 좋아요
    bae_com_like_by = models.ManyToManyField(User, related_name='liked_comments')  # 좋아요를 누른 회원 
    bae_com_date = models.DateTimeField('작성일', auto_now_add=True)  # 작성일 

    def __str__(self):
        return self.bae_com_content