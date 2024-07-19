from django.shortcuts import render
from .models import County
from django.views.generic import *

# 홈페이지 뷰 (국내여행)
class HomeListView(ListView):
    template_name = 'home.html'  # 템플릿 경로
    context_object_name = 'counties'  # 템플릿에서 사용할 객체 리스트 이름

    def get_queryset(self):
        return County.objects.all().prefetch_related('countyimg_set')  # County와 CountyImg를 한 번에 가져오기 위해 prefetch_related 사용
    

# 여행시작 메인페이지 뷰
class TravelListView(ListView):
    template_name = 'travel.html'  # 템플릿 경로
    context_object_name = 'travels'  # 템플릿에서 사용할 객체 리스트 이름

    def get_queryset(self):
        return County.objects.all().prefetch_related('countyimg_set')  # County와 CountyImg를 한 번에 가져오기 위해 prefetch_related 사용