from django.urls import path
from . import views

urlpatterns = [
    path('', views.tour_main, name='tour_main'),
    path('tour/<int:tour_id>/', views.tour_detail, name='tour_detail'),
    path('get-price-options/', views.get_price_options, name='get_price_options'),
    path('search/', views.search_results, name='search'),
]