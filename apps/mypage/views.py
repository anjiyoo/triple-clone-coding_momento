from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from apps.accommodation.models import AccommodationLike,Review
from apps.flights.models import Reservation,BookerInfo
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from apps.accommodation.models import Reservation as AccommodationReservation,GuestInfo
from apps.flights.models import Reservation as FlightReservation ,BookerInfo
from django.views.generic import ListView
from apps.accommodation.models import Reservation as AccommodationReservation, GuestInfo
from apps.flights.models import Reservation as FlightReservation, BookerInfo

from django.views.generic import ListView
from apps.accommodation.models import Reservation as AccommodationReservation, GuestInfo
from apps.flights.models import Reservation as FlightReservation, BookerInfo

class ReservationListView(ListView):
    template_name = 'mypage/reservation_list.html'
    context_object_name = 'reservations'

    def get_queryset(self):
        flight_reservations = FlightReservation.objects.filter(user=self.request.user)
        accommodation_reservations = AccommodationReservation.objects.filter(user=self.request.user)

        for reservation in flight_reservations:
            reservation.reservation_type = 'flight'
        
        for reservation in accommodation_reservations:
            reservation.reservation_type = 'accommodation'

        return list(flight_reservations) + list(accommodation_reservations)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reservations = context['reservations']
        for reservation in reservations:
            if reservation.reservation_type == 'flight':
                booker_info = BookerInfo.objects.filter(reservation=reservation).first()
                reservation.booker_name = booker_info.name if booker_info else ''
            elif reservation.reservation_type == 'accommodation':
                guest_info = GuestInfo.objects.filter(id=reservation.guest_info_id).first()
                reservation.guest_name = guest_info.name if guest_info else ''
                reservation.accommodation_name = reservation.accommodation.name
                reservation.room_name = reservation.room.name
        context['reservations'] = reservations
        return context

class SaveListView(ListView):
    template_name = 'mypage/save_list.html'
    context_object_name = 'likes'

    def get_queryset(self):
        return AccommodationLike.objects.filter(user=self.request.user).select_related('accommodation')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        likes = context['likes']
        for like in likes:
            accommodation = like.accommodation
            first_image = accommodation.images.first()
            # 첫 번째 이미지 URL을 추가
            like.first_image_url = first_image.images.url if first_image else ''
            # 숙소의 좋아요 수를 계산하여 추가
            like.likes_count = accommodation.likes.count()
            # 각 숙소의 리뷰 수를 추가
            like.reviews_count = Review.objects.filter(accommodation=accommodation).count()
        
        return context

class ReviewListView(ListView):
    template_name = 'mypage/review_list.html'
    context_object_name = 'reviews'

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reviews = context['reviews']
        
        for review in reviews:
            accommodation = review.accommodation
            first_image = accommodation.images.first()
            # 첫 번째 이미지 URL을 추가
            review.first_image_url = first_image.images.url if first_image else ''
        return context
