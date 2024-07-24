from django import forms 
from django.db import models

from .models import diary

class DiaryForm(forms.ModelForm):
    class Meta :
        model = diary
        fields = ['title','content','image']