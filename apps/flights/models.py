from django.db import models
from apps.userinfo.models import User
class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 유저 모델 외부키
    reservation_date = models.DateTimeField()
    number_of_people = models.IntegerField()
    departure_airport = models.CharField(max_length=50)
    arrival_airport = models.CharField(max_length=50)
    departure_time =models.CharField(max_length=50)
    arrival_time = models.CharField(max_length=50)
    flight_number = models.CharField(max_length=50)
    airline_code = models.CharField(max_length=10)
    flight_name = models.CharField(max_length=50)
    free_baggage_allowance = models.IntegerField()
    return_departure_airport = models.CharField(max_length=50, blank=True, null=True)
    return_arrival_airport = models.CharField(max_length=50, blank=True, null=True)
    return_depature_time = models.CharField(max_length=50, blank=True, null=True)
    return_arrival_time = models.CharField(max_length=50, blank=True, null=True)
    return_flight_number = models.CharField(max_length=50, blank=True, null=True)
    return_airline_code = models.CharField(max_length=10, blank=True, null=True)
    return_flight_name = models.CharField(max_length=50, blank=True, null=True)
    return_free_baggage_allowance = models.IntegerField(blank=True, null=True)
    

class BookerInfo(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()

class PassengerInfo(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=10)
    nationality = models.CharField(max_length=50, default="대한민국")
    one_way_price = models.IntegerField()  # 갈때가격
    return_price = models.IntegerField()   # 올때가격
    age_category = models.CharField(max_length=20)  # 어른, 소아, 유아
    birth_date = models.CharField(max_length=8)
