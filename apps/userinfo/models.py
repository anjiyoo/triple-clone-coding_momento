from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    profile = models.ImageField(upload_to='profiles/', default='profiles/default.png', blank=False)
    nickname = models.CharField(max_length=30)
    email = models.EmailField(null=True, blank=True)
    google_profile = models.URLField(max_length=255,blank=True, null = True)

    def str(self):
        return self.username

    @property
    def profiles(self):
        if self.google_profile and self.google_profile.url: 
            return self.google_profile.url
        return self.profile.url