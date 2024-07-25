from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *

app_name = 'accommodation'

urlpatterns = [
    path('', AccommodationHomeView.as_view(), name='accommodation_home'),
    path('detail/<int:pk>/', AccomodationDetailView.as_view(), name='accommodation_detail'),
    path('detail/<int:accommodation_pk>/room/<int:room_pk>/', RoomDetailView.as_view(), name='room_detail'),
    path('detail/<int:pk>/map/', my_view, name='map'),
    path('reservation/<int:accommodation_pk>/room/<int:room_pk>/', make_reservation, name='create_reservation'),
    path('reservation/<int:reservation_pk>/delete', delete_reservation, name='delete_reservation'),
    # path('reservation/success/<int:reservation_id>/', reservation_success, name='reservation_success'),
    path('reservation/success/', reservation_success, name='reservation_success'),  # AJAX 요청을 처리하는 뷰
    path('reservation/success/<int:reservation_id>/', reservation_success_page, name='reservation_success_page'),  # 성공 페이지를 렌더링하는 뷰
    path('detail/<int:pk>/create_review/', CreateReview.as_view(), name='create_review'),
    path('detail/<int:accommodation_pk>/review/<int:review_pk>/', ReviewDetailView.as_view(), name='review_detail'),
    path('detail/<int:accommodation_pk>/review/<int:review_pk>/update/', UpdateReview.as_view(), name='update_review'),
    path('detail/<int:accommodation_pk>/review/<int:review_pk>/delete/', DeleteReview.as_view(), name='delete_review'),
    path('accommodations/<str:filter_type>/<str:filter_value>/', AccommodationFilterView.as_view(), name='accommodation_filter'),
    path('region_select/', region_select, name='region_select'),
    path('list/<str:accommodation_type>/',accommodation_type_region_select, name='accommodation_type_region_select'),
    path('list/<str:accommodation_type>/<str:city_name>/', accommodation_region_list, name='accommodation_region_list'),
    path('detail/<int:accommodation_pk>/like/', like_accommodation, name='like_accommodation'),
    path('detail/<int:accommodation_pk>/unlike/', unlike_accommodation, name='unlike_accommodation'),
    path('search_accommodations/', search_accommodations, name='search_accommodations'),
    

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)