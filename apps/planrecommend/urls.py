from django.urls import path
from .views import *
from . import views

app_name = 'planrecommend'

urlpatterns = [
    path('', SelectCityListView.as_view(), name='select_city'),
    path('select_date/', SelectDateListView.as_view(), name='select_date'),
    path('select_who/', SelectWhoListView.as_view(), name='select_who'),

    path('recommend', views.recommend, name='recommend'),  # 질문
    path('response/', views.response, name='response'),  # 응답

    path('preparing/', PreparingListView.as_view(), name='preparing'),  # 준비중
]