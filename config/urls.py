"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from apps.userinfo.views import profile  # profile 뷰를 임포트합니다.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("apps.travel.urls")),

    path('mypage/', profile, name='mypage'),
    path('accounts/', include('allauth.urls')),
    # path('  /', login_required(TemplateView.as_view(template_name='profile.html')), name='profile'),

    path('baenangtalk/', include("apps.baenangtalk.urls")),
    path('flights/',include('apps.flights.urls',namespace='flights')),
    path('chatbot/', include('apps.chatbot.urls')),
    path('plan/', include('apps.plan.urls')),
    path('planrecommend/', include('apps.planrecommend.urls')),
    path('tour/', include('apps.tour.urls')),
    path('customer_service/', include('apps.customer_service.urls')),
    path('travel_diary/',include('apps.travel_diary.urls')),
    path('test_mypage/', include('apps.mypage.urls')),
    path('test_mypage/', include(('apps.mypage.urls', 'mypage'), namespace='mypage')),
    path('accommodation/', include("apps.accommodation.urls")),
    path('guidepage/', include("apps.guidepage.urls")),
    path('search/', include("apps.search.urls")),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)