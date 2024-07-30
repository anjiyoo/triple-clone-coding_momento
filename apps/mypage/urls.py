from django.urls import path
from .views import ReservationListView,SaveListView,ReviewListView
app_name = 'mypage'
urlpatterns = [
    path('my_reservations/', ReservationListView.as_view(), name='my_reservations'),
    path('save_list/', SaveListView.as_view(), name='save_list'),
    path('review_list/', ReviewListView.as_view(), name='review_list'),


]
