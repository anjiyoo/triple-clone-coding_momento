from django.urls import path
from .views import ReservationListView

urlpatterns = [
    path('my_reservations/', ReservationListView.as_view(), name='my_reservations'),
]
