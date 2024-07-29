from django.urls import path
from .views import search

app_name='customer_service'

urlpatterns = [
    path('', search, name='search'),
]