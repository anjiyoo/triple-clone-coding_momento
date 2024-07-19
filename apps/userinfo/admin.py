from django.contrib import admin
from .models import User  # User 모델을 import 해옵니다.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'nickname', 'profile')