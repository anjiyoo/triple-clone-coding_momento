from django.urls import path
from . import views
app_name= 'travel_diary'
urlpatterns = [
 path('create/<int:trip_id>/',views.DiaryCreateView.as_view(),name='create'),
 path('diary_list/',views.DiaryList.as_view(),name='diary_list'),
 path('diary_detail/<int:pk>',views.DiaryDetail.as_view(),name='diary_detail'),
 path('update/<int:diary_id>/<int:trip_id>',views.DiaryUpdate.as_view(),name='update')
]