from django import forms 
from django.db import models

from .models import diary

class DiaryForm(forms.ModelForm):
    class Meta :
        model = diary
        fields = ['title','content','image']

    widgets = {
            "title": forms.Textarea(attrs={"class": "form-control mt-2", "rows": 10}),
            'content': forms.Textarea(attrs={"class": "textarea","id":"diary-title"}),
            'image': forms.ClearableFileInput(attrs={"class":"image-form"})
        }