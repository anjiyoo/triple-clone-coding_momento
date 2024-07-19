from django.urls import path
from apps.baenangtalk import views
from .views import *

app_name='baenangtalk'

urlpatterns = [
    # 배낭톡
    path('', MainPostListView.as_view(), name='bae_main'), 
    path('detail/<int:pk>/', PostDetailView.as_view(), name='bae_detail'), 
    path('create/', PostCreateView.as_view(), name='bae_create'),  
    path('eidt/<int:pk>/', PostEditView.as_view(), name='bae_edit'),  
    path('delete/<int:pk>/', PostDeleteView.as_view(), name='bae_delete'),  
    
    path('city/<int:county_id>/', MainPostListView.as_view(), name='city_posts'),  # 도시 선택
    path('period/<int:period_id>/', MainPostListView.as_view(), name='period_posts'),  # 여행시기 선택
    path('subject/<int:subject_id>/', MainPostListView.as_view(), name='subject_posts'),  # 주제 선택
    
    # 좋아요&취소
    path('like/<int:pk>/', views.bae_post_like, name='bae_like'),  
    path('unlike/<int:pk>/', views.bae_post_unlike, name='bae_unlike'),  

    # 댓글
    path('com/eidt/<int:comment_id>/', views.com_edit, name='com_edit'),  
    path('com/delete/<int:comment_id>/', views.com_delete, name='com_delete'),  
    # 댓글 좋아요&취소
    path('com/like/<int:comment_id>/', views.com_like, name='com_like'),  
    path('com/unlike/<int:comment_id>/', views.com_unlike, name='com_unlike'), 
]