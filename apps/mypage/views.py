from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView


# Create your views here.
from django.views.generic import ListView
from apps.flights.models import Reservation

class ReservationListView(ListView):
    template_name = 'mypage/reservation_list.html'
    context_object_name = 'reservations'

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

