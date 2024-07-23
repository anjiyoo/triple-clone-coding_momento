from django.contrib import admin
from .models import  GuestInfo, TransportationInfo, Accommodation, Room, Review, AccommodationImage, RoomImage, CancellationPolicy

class AccommodationImageInline(admin.TabularInline):
    model = AccommodationImage
    extra = 1  # 추가할 수 있는 빈 이미지 필드의 수

class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1  # 추가할 수 있는 빈 이미지 필드의 수
# Register your models here.
@admin.register(Accommodation)
class AccommodationAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'accommodation_type', 'price' , 'get_likes')
    list_filter = ('accommodation_type',)
    search_fields = ('name', 'location')
    inlines = [AccommodationImageInline]
    
    def get_likes(self, obj):
        # 'like' 필드가 many-to-many 관계일 경우, 관련 객체의 수를 반환합니다.
        # 예시는 'like' 필드가 ManyToManyField를 가정한 것이며, 실제 모델 구조에 따라 수정이 필요합니다.
        return obj.like.count()
    get_likes.short_description = 'Likes'  # 관리자 페이지에서 표시될 컬럼 제목

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'accommodation', 'capacity', 'description', 'price', 'is_free_cancellation', 'includes_breakfast')
    list_filter = ('accommodation',)
    search_fields = ('name', 'description')
    inlines = [RoomImageInline]


@admin.register(GuestInfo)
class GuestInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'birth_date','gender')
    search_fields = ('name', 'birth_date','gender')

@admin.register(TransportationInfo)
class TransportationInfoAdmin(admin.ModelAdmin):
    list_display = ('public_transport', 'walking', 'personal_car')
    search_fields = ('public_transport', 'walking', 'personal_car')

# @admin.register(PaymentDetail)
# class PaymentDetailAdmin(admin.ModelAdmin):
#     list_display = ('reservation_amount', 'total_amount')
#     search_fields = ('reservation_amount', 'total_amount')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('accommodation', 'rating', 'content')
    search_fields = ('accommodation', 'rating', 'content')

@admin.register(RoomImage)
class RoomImage(admin.ModelAdmin):
    list_display = ('room', 'images')
    search_fields = ('room', 'images')


@admin.register(AccommodationImage)
class AccommodationImage(admin.ModelAdmin):
    list_display = ('accommodation', 'images')
    search_fields = ('accommodation', 'images')

@admin.register(CancellationPolicy)
class CancellationPolicyAdmin(admin.ModelAdmin):
    list_display = ('policy_text', 'agree_text')
    search_fields = ('policy_text', 'agree_text')
