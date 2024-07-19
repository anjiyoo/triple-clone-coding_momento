from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chatbot_main, name='chatbot_main'),
    path('response/', views.chatbot_response, name='chatbot_response'),
]