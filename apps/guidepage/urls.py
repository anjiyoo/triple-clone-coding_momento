from django.urls import path
from . import views

urlpatterns = [
    path('', views.guidemain, name='index'),
    path('guide_plan', views.guide_plan, name='guide_plan'),
    path('guide_info', views.guide_info, name='guide_info'),
    path('guide_reservation', views.guide_reservation, name='guide_reservation'),
    path('guide_memory', views.guide_memory, name='guide_memory'),


]