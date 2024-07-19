from django.db import models
from apps.travel.models import County
from django.conf import settings
# Create your models here.

class Trip(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    city_name = models.ForeignKey(County,on_delete=models.SET_NULL, null=True)
    who = models.CharField(max_length=20,default='혼자')
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

class Trip_style(models.Model):
    trip = models.ForeignKey(Trip,on_delete=models.CASCADE)
    style = models.CharField(max_length=30)

class CitySpot(models.Model):
    city_name = models.ForeignKey(County, on_delete=models.CASCADE, related_name='tour_spots')
    title = models.CharField(max_length=50)
    address = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    content_id = models.IntegerField(unique=True)
    map_x = models.FloatField(default=0.0)
    map_y = models.FloatField(default=0.0)
    def __str__(self):
        return self.title
    
# class TripDay(models.Model):
#     trip = models.ForeignKey(Trip,on_delete=models.CASCADE)
#     date = models.DateField()
#     day_number = models.IntegerField()

class DayPlan(models.Model):
    trip = models.ForeignKey(Trip,on_delete=models.CASCADE)
    spot = models.ForeignKey(CitySpot,on_delete=models.CASCADE)
    memo = models.TextField()
    day = models.DateField()