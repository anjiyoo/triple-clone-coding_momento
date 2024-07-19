from django.urls import path

from . import views

app_name = 'userinfo'
urlpatterns = [
    path('mypage/profile/', views.profile, name='profile'),
#    path('mypage/mytravel/', views.mytravel, name='mytravel'),
#    path('mypage/mywish/', views.mywish, name='mywish'),
#    path('mypage/myreview/', views.myreview, name='myreview'),
#    path('mypage/book/', views.book, name='book'),
#    path('mypage/myplan', views.myplan, name='myplan')
]