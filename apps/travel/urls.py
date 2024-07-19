from django.urls import path
from .views import *

app_name='travel'

urlpatterns = [
    path('', HomeListView.as_view(), name='home'),  # 홈페이지
    path('travel/', TravelListView.as_view(), name='travel'),  # 여행시작 메인페이지
]