from django.db import models
from django.conf import settings
from apps.plan.models import Trip
# Create your models here.

class tag(models.Model):
    name = models.CharField(max_length=50)
    registered_date = models.DateTimeField(auto_now_add=True, verbose_name="등록시간")

    def __str__(self):
        return self.name
    
class diary(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    trip = models.OneToOneField(Trip,on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    content = models.TextField()
    image = models.ImageField(upload_to='diary/%Y/%m/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(tag,blank=True)