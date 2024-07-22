from django.db import models
# from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.userinfo.models import User
from apps.travel.models import County

DOMESTIC_ACCOMMODATION_TYPES = (
    ('pension_pool_vila', '펜션, 풀빌라'),
    ('camping_glamping', '캠핑, 글램핑'),
    ('boutique_motel', '부티크 모텔'),
)

# 숙소 정보를 저장할 모델
class Accommodation(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    city = models.ForeignKey(County, on_delete=models.CASCADE)  # 도시 정보 참조
    location = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    accommodation_type = models.CharField(max_length=100, choices=DOMESTIC_ACCOMMODATION_TYPES, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    like = models.ManyToManyField(User, related_name='like_accommodations', blank=True)

    DOMESTIC_ACCOMMODATION_TYPES = (
        ('pension_pool_vila', '펜션, 풀빌라'),
        ('camping_glamping', '캠핑, 글램핑'),
        ('boutique_motel', '부티크 모텔'),
    )



# 숙소 이미지를 저장할 모델
class AccommodationImage(models.Model):
    accommodation = models.ForeignKey(Accommodation, related_name='images', on_delete=models.CASCADE)
    images = models.ImageField(upload_to='accommodation')

# 숙소 객실 정보 저장할 모델
class Room(models.Model):
    accommodation = models.ForeignKey(Accommodation, related_name='rooms', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    capacity = models.IntegerField()
    is_free_cancellation = models.BooleanField(default=False)
    includes_breakfast = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    check_in_time = models.TimeField()
    check_out_time = models.TimeField()
    guide = models.TextField(null=True, blank=True)  # 이용안내 필드 추가

    def __str__(self):
        return f"{self.name} - {self.accommodation.name}"
class RoomImage(models.Model):
    room = models.ForeignKey(Room, related_name='images', on_delete=models.CASCADE)
    images = models.ImageField(upload_to='room')

# 예약자 정보 모델
class ReservationHolderInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.user.email}"

# 예약 페이지에서 작성할 투숙자 정보 모델
class GuestInfo(models.Model):
    name = models.CharField(max_length=100)
    birth_date = models.DateField()
    gender = models.CharField(max_length=10, choices=(('male', '남성'), ('female', '여성')))

    def __str__(self):
        return f"{self.name}"


# 예약 페이지에서 작성할 교통편 정보 모델
class TransportationInfo(models.Model):
    public_transport = models.BooleanField(default=False)
    walking = models.BooleanField(default=False)
    personal_car = models.BooleanField(default=False)


class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accommodation_reservations')
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in = models.DateField(blank=False, null=False) # 체크인 날짜
    check_out = models.DateField(blank=False, null=False)
    reservation_holder_info = models.OneToOneField(ReservationHolderInfo, on_delete=models.CASCADE)
    guest_info = models.OneToOneField(GuestInfo, on_delete=models.CASCADE)
    transportation_info = models.OneToOneField(TransportationInfo, on_delete=models.CASCADE)
    cancellation_policy_agreed = models.BooleanField(default=False)
    terms_and_conditions_agreed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True) 
    reservation_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    guests_adult = models.PositiveIntegerField(default=2)  # 성인 인원수 필드
    guests_child = models.PositiveIntegerField(default=0)  # 아동 인원수 필드
    telnum = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.accommodation.name}"


# 리뷰 작성하기 
class Review(models.Model):
    accommodation = models.ForeignKey(Accommodation, related_name='reviews', on_delete=models.CASCADE)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE,  null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')], default=5)
    image_url = models.ImageField(upload_to='review', blank=True)
    travel_date = models.CharField(max_length=10,null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.accommodation.name}"

# 취소 및 이용 규정 모델
class CancellationPolicy(models.Model):
    policy_text = models.TextField()
    agree_text = models.TextField(null=True, blank=True)

class AccommodationLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    accommodation = models.ForeignKey(Accommodation, related_name='likes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)