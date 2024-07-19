from django.urls import path
from .views import *

app_name = 'planrecommend'

urlpatterns = [
    path('', SelectCityListView.as_view(), name='select_city'),
    path('select_date/', SelectDateListView.as_view(), name='select_date'),
    path('select_who/', SelectWhoListView.as_view(), name='select_who'),
    path('select_style/', SelectStyleListView.as_view(), name='select_style'),
    path('select_plan/', SelectPlanListView.as_view(), name='select_plan'),

]