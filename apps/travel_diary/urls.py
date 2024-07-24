from django.urls import path
from . import views
app_name= 'travel_diary'
urlpatterns = [
 path('create/<int:trip_id>/',views.DiaryCreateView.as_view(),name='create')
]