from django.dispatch import receiver
from allauth.account.signals import user_logged_in
from .models import User
import random

@receiver(user_logged_in)
def user_logged_in_handler(request, user, **kwargs):
    if not user.nickname or not user.google_profile:  # 닉네임 또는 구글 프로필이 없을 때만 설정
        socialaccount = user.socialaccount_set.filter(provider='google').first()
        if socialaccount:
            if not user.google_profile:
                user.google_profile = socialaccount.extra_data.get('picture')
            if not user.nickname:
                user.nickname = generate_nickname(user)
            user.save()

def generate_nickname(user):
    return f'user_{random.randint(1000, 9999)}'
