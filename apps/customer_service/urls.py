from django.urls import path
from apps.customer_service import views
from .views import *


urlpatterns = [
    path('',InquiryListView.as_view(),name='customer_service'),
]