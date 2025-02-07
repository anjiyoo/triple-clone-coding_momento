from django.urls import path
from .views import Flights_Search, flight_search_view, flight_details_view,flight_booking_view,ReservationDetailView,payment_callback
app_name = 'flights'
urlpatterns = [
    path('flights_search/', Flights_Search.as_view(), name='flights_search'),
    path('', flight_search_view, name='flight_search'),
    path('flight_details/<str:flight_id>/', flight_details_view, name='flight_details'),
    path('booking/', flight_booking_view, name='book_flight'),  
    path('reservation/<int:pk>/', ReservationDetailView.as_view(), name='reservation_detail'),
    path('payment/callback/', payment_callback, name='payment_callback'),
]
