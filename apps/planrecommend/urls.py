from django.urls import path
from .views import *
from . import views

app_name = 'planrecommend'

urlpatterns = [
    path('', SelectCityListView.as_view(), name='select_city'),
    path('select_date/', SelectDateListView.as_view(), name='select_date'),
    path('select_who/', SelectWhoListView.as_view(), name='select_who'),
    path('select_style/', SelectStyleListView.as_view(), name='select_style'),
    path('select_plan/', SelectPlanListView.as_view(), name='select_plan'),

    path('preparing/', PreparingListView.as_view(), name='preparing'),
    path('itinerary/', views.itinerary, name='itinerary'),
    
]