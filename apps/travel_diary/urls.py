from django.urls import path
from . import views
app_name= 'travel_diary'
urlpatterns = [
 path('create/<int:trip_id>/',views.DiaryCreateView.as_view(),name='create'),
 path('diary_list/',views.DiaryList.as_view(),name='diary_list'),
 path('diary_detail/<int:pk>',views.DiaryDetail.as_view(),name='diary_detail'),
 path('update/<int:diary_id>/<int:trip_id>',views.DiaryUpdate.as_view(),name='update'),
 path('delete/<int:pk>/',views.DiaryDelete.as_view(),name='delete'),
 # 댓글 좋아요&취소
 path('com/like/<int:comment_id>/', views.com_like, name='com_like'),  
 path('com/unlike/<int:comment_id>/', views.com_unlike, name='com_unlike'), 
 # 댓글
 path('com/edit/<int:comment_id>/', views.com_edit, name='com_edit'),
 path('com/delete/<int:comment_id>/', views.com_delete, name='com_delete'),  
]