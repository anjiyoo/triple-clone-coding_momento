# views.py
from rest_framework import status
from rest_framework.views import APIView
# from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Accommodation, Reservation, GuestInfo, TransportationInfo, Room, Review, AccommodationImage,  RoomImage, CancellationPolicy, ReservationHolderInfo,  DOMESTIC_ACCOMMODATION_TYPES, AccommodationLike
from apps.userinfo.models import User
from apps.travel.models import County, CountyImg
from .serializers import AccommodationSerializer, ReservationSerializer, ReviewSerializer, UserSerializer, ReservationHolderInfoSerializer
from django.shortcuts import render
from django.db.models import Avg, Q, F
from django.conf import settings  
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from .forms import ReviewForm, ReservationForm, ReservationHolderInfoForm, GuestInfoForm, TransportationInfoForm
from django.views.generic import ListView
from django.http import JsonResponse



# 숙소 조회
class ListAccommodations(APIView):
    def get(self, request):
        accommodation = Accommodation.objects.all()
        serializer = AccommodationSerializer(accommodation, many=True)
        return Response(serializer.data)

from datetime import datetime, date 

# 숙소 상세 페이지 조회
class AccomodationDetailView(APIView):
    def get(self, request, pk):
        # user = request.user
        accommodation = Accommodation.objects.get(pk=pk)

        room = Room.objects.filter(accommodation=accommodation)
        reviews = Review.objects.filter(accommodation=accommodation).order_by('-user', '-created_at')

        user_review = Review.objects.filter(accommodation=accommodation, user=request.user)
        reviews_count = reviews.count()
        likes_count = AccommodationLike.objects.filter(accommodation=accommodation).count()

        is_liked = AccommodationLike.objects.filter(user=request.user, accommodation=accommodation).exists()


        if reviews_count > 0:
            average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        else:
            average_rating = 0

        
        accommodation_images = AccommodationImage.objects.filter(accommodation=accommodation)  # Accommodation에 연결된 모든 이미지 가져오기
        room_images = RoomImage.objects.filter(room__in=room)

        min_price_room = room.order_by('price').first()
        min_price = min_price_room.price if min_price_room else None
        min_price_room_id = min_price_room.id if min_price_room else None

        user_has_reviewed = Review.objects.filter(accommodation=accommodation, user=request.user).exists()

        context = {
            'accommodation': accommodation,
            'room': room,
            'user_review': user_review,
            'MEDIA_URL': settings.MEDIA_URL,
            'images': accommodation_images,
            'room_images': room_images,
            'reviews_count': reviews_count,
            'likes_count': likes_count,
            'average_rating': average_rating,
            'min_price': min_price,
            'min_price_room_id': min_price_room_id,
            'user_has_reviewed': user_has_reviewed,
            'reviews': reviews,
            'is_liked': is_liked,
            

        }
        
        return render(request, 'accommodation/accommodation_detail.html', context)
    
    


def reservation_success(request):
    return render(request, 'accommodation/reservation_success.html')


@login_required
def make_reservation(request, accommodation_pk, room_pk):

    if request.method == 'POST':
        reservation_form = ReservationForm(request.POST)
        holder_form = ReservationHolderInfoForm(request.POST)
        guest_form = GuestInfoForm(request.POST)
        transportation_form = TransportationInfoForm(request.POST)
        reservation_amount = request.POST.get('reservation_amount')
        total_amount = request.POST.get('total_amount')

        if (reservation_form.is_valid() and holder_form.is_valid() and
            guest_form.is_valid() and transportation_form.is_valid()):
            
            # Save each form individually
            holder_info = holder_form.save(commit=False)
            holder_info.user = request.user  # Assuming user is logged in
            holder_info.save()

            guest_info = guest_form.save()
            transportation_info = transportation_form.save()

            reservation = reservation_form.save(commit=False)
            reservation.user = request.user
            reservation.reservation_holder_info = holder_info
            reservation.guest_info = guest_info
            reservation.transportation_info = transportation_info
            reservation.accommodation_id = accommodation_pk
            reservation.room_id = room_pk

            try:
                reservation.reservation_amount = float(reservation_amount.replace(',', '')) if reservation_amount else 0.0
                reservation.total_amount = float(total_amount.replace(',', '')) if total_amount else 0.0
            except ValueError:
                # 여기에 오류 처리 로직 추가
                pass
            reservation.save()

            return redirect('accommodation:reservation_success', reservation_id=reservation.id)  # Redirect to a success page
        else:
             # 폼 유효성 검사 실패 시 오류 메시지 출력
            print("Reservation Form Errors:", reservation_form.errors)
            print("Holder Form Errors:", holder_form.errors)
            print("Guest Form Errors:", guest_form.errors)
            print("Transportation Form Errors:", transportation_form.errors)


    else:
        reservation_form = ReservationForm()
        holder_form = ReservationHolderInfoForm(user=request.user)
        guest_form = GuestInfoForm()
        transportation_form = TransportationInfoForm()
        

    room = get_object_or_404(Room, pk=room_pk)
    accommodation = Accommodation.objects.get(pk=accommodation_pk)
    accommodation_image = AccommodationImage.objects.filter(accommodation=accommodation).first()  # Accommodation에 연결된 모든 이미지 가져오기


    context = {
        'reservation_form': reservation_form,
        'holder_form': holder_form,
        'guest_form': guest_form,
        'transportation_form': transportation_form,
        'room': room,
        'accommodation': accommodation,
        'accommodation_image': accommodation_image,
        'MEDIA_URL': settings.MEDIA_URL,

    }

    return render(request, 'accommodation/create_reservation.html', context)

from django.http import HttpResponse,HttpResponseRedirect
from django.views.decorators.http import require_POST

@require_POST
def delete_reservation(request, reservation_pk):
    # 예약 정보를 데이터베이스에서 가져옵니다.
    reservation = get_object_or_404(Reservation, pk=reservation_pk)
    if request.user != reservation.user:
        return HttpResponse("예약을 삭제할 권한이 없습니다.", status=403)
    # 예약을 데이터베이스에서 삭제합니다.
    reservation.delete()

    return HttpResponseRedirect(reverse('accommodation:accommodation_home'))


# 지도 띄우기
def my_view(request, pk):
    accommodation = Accommodation.objects.get(pk=pk)

    # 리뷰와 좋아요 갯수 가져오기
    reviews = Review.objects.filter(accommodation=accommodation)
    images = AccommodationImage.objects.filter(accommodation=accommodation)  # Accommodation에 연결된 모든 이미지 가져오기

    reviews_count = reviews.count()
    likes_count = accommodation.like.count()

    # 리뷰의 평균 별점 계산
    if reviews_count > 0:
        average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    else:
        average_rating = 0
    # 컨텍스트 딕셔너리에 GOOGLE_MAPS_API_KEY 추가
    context = {
        # 'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
        'accommodation': accommodation,
        'MEDIA_URL': settings.MEDIA_URL,
        'lat': accommodation.latitude,
        'lng': accommodation.longitude,
        'reviews': reviews,
        'reviews_count': reviews_count,
        'likes_count': likes_count,
        'average_rating': average_rating,
        'images': images if AccommodationImage.images else '',
        }
    # 컨텍스트와 함께 my_template.html 템플릿 렌더링
    return render(request, 'accommodation/accommodation_map.html', context)
  

class RoomDetailView(APIView):
    def get(self, request, accommodation_pk, room_pk):
        accommodation = Accommodation.objects.get(pk=accommodation_pk)
        room = Room.objects.get(pk=room_pk)
        room_images = RoomImage.objects.filter(room=room)
        
        context = {
            'MEDIA_URL': settings.MEDIA_URL,
            'accommodation': accommodation,
            'room': room,
            'room_images': room_images,
            'name': room.name,
            'description': room.description,
            'capacity': room.capacity,
            'is_free_cancellation': room.is_free_cancellation,
            'includes_breakfast': room.includes_breakfast,
            'price': room.price,
            'check_in_time': room.check_in_time,
            'check_out_time': room.check_out_time,
            'guide': room.guide,
        }
        return render(request, 'accommodation/room_detail.html', context)
    
class ListReviews(APIView):
    def get(self, request, format=None):
        reviews = Review.objects.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



@method_decorator(login_required, name='dispatch')
class CreateReview(View):
    def get(self, request, pk):
        accommodation = get_object_or_404(Accommodation, pk=pk)
        form = ReviewForm()
        return render(request, 'review/create_review.html', {'form': form, 'accommodation': accommodation})

    def post(self, request, pk):
        user = request.user
        accommodation = get_object_or_404(Accommodation, pk=pk)
        form = ReviewForm(request.POST, request.FILES)

        if form.is_valid():
            review = form.save(commit=False)
            review.accommodation = accommodation
            if request.user.is_authenticated:
                review.user = request.user
            # review.user=user
            review.save()
            redirect_url = reverse('accommodation:review_detail', kwargs={'accommodation_pk': accommodation.pk, 'review_pk': review.pk})
            return JsonResponse({'success': True, 'redirect_url': redirect_url})
        else:
            return JsonResponse({'success': False, 'error': form.errors})

class ReviewDetailView(APIView):
    def get(self, request, accommodation_pk, review_pk):
        user = request.user
        accommodation = get_object_or_404(Accommodation, pk=accommodation_pk)
        accommodation_images = AccommodationImage.objects.filter(accommodation=accommodation)
        is_liked = AccommodationLike.objects.filter(user=request.user, accommodation=accommodation).exists()

        review = get_object_or_404(Review, pk=review_pk)
        context = {
            'accommodation': accommodation,
            'review': review,
            'MEDIA_URL': settings.MEDIA_URL,
            'images': accommodation_images,
            'is_liked': is_liked,
        }
        return render(request, 'review/review_detail.html', context)


from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage


@method_decorator(login_required, name='dispatch')
class UpdateReview(View):
    def get(self, request, accommodation_pk, review_pk):
        accommodation = get_object_or_404(Accommodation, pk=accommodation_pk)
        review = get_object_or_404(Review, pk=review_pk, user=request.user)
        form = ReviewForm(instance=review)
        context = {
            'form': form,
            'accommodation': accommodation,
            'review': review,
            'MEDIA_URL': settings.MEDIA_URL,
        }
        return render(request, 'review/update_review.html', context)
        
    @method_decorator(csrf_exempt)
    def post(self, request, accommodation_pk, review_pk):
        accommodation = get_object_or_404(Accommodation, pk=accommodation_pk)
        review = get_object_or_404(Review, pk=review_pk, user=request.user)
        form = ReviewForm(request.POST, request.FILES, instance=review)
        
        if form.is_valid():
            # 이미지 삭제 처리
            if request.POST.get('image_deleted') == '1':
                if review.image_url:  # 기존 이미지가 있을 경우
                    if default_storage.exists(review.image_url.path):
                        default_storage.delete(review.image_url.path)
                    review.image_url = None

            # 새로운 이미지 추가 처리
            if 'image_url' in request.FILES:
                review.image_url = request.FILES['image_url']

            form.save()
            return redirect(reverse('accommodation:review_detail', kwargs={'accommodation_pk': accommodation.pk, 'review_pk': review.pk}))
        
        context = {
            'form': form,
            'accommodation': accommodation,
            'review': review,
            'MEDIA_URL': settings.MEDIA_URL,
        }
        return render(request, 'review/update_review.html', context)





from django.http import HttpResponseForbidden

@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class DeleteReview(View):
    def post(self, request, accommodation_pk, review_pk):
        accommodation = get_object_or_404(Accommodation, pk=accommodation_pk)
        review = get_object_or_404(Review, pk=review_pk)

        # 작성자가 현재 로그인한 사용자와 일치하는지 확인
        if review.user != request.user:
            return HttpResponseForbidden("You are not allowed to delete this review.")

        review.delete()
        return redirect(reverse('accommodation:accommodation_detail', kwargs={'pk': accommodation.pk}))



from django.views.generic import ListView, TemplateView
import random

class AccommodationHomeView(TemplateView):
    template_name = 'accommodation/accommodation_main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['counties'] = County.objects.all()
        county_images = []
        for county in County.objects.all():
            first_image = CountyImg.objects.filter(city_name=county).first()
            if first_image:
                county_images.append(first_image)
        context['county_images'] = county_images
        context['accommodation_types'] = dict(DOMESTIC_ACCOMMODATION_TYPES)

         # 랜덤으로 이미지를 선택하여 템플릿에 전달
        all_images = list(CountyImg.objects.all())
        random_images = random.sample(all_images, min(len(all_images), 5))  # 최대 5개의 랜덤 이미지 선택
        context['random_images'] = random_images
        context['MEDIA_URL'] = settings.MEDIA_URL
        
        return context

class AccommodationFilterView(ListView):
    model = Accommodation
    template_name = 'accommodation/accommodation_list.html'
    context_object_name = 'accommodations'

    def get_queryset(self):
        filter_type = self.kwargs['filter_type']
        filter_value = self.kwargs['filter_value']

        if filter_type == 'county':
            return Accommodation.objects.filter(city__id=filter_value)
        else:
            return Accommodation.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_type = self.kwargs['filter_type']
        filter_value = self.kwargs['filter_value']

        if filter_type == 'county':
            context['filter_name'] = County.objects.get(id=filter_value).city_name

        accommodations = self.get_queryset()
        for accommodation in accommodations:
            reviews = accommodation.reviews.all()
            accommodation.review_count = reviews.count()
            accommodation.like_count = accommodation.like.count()
            accommodation.avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

        context['accommodations'] = accommodations


        return context


from django.shortcuts import render
from .models import Accommodation, AccommodationImage

def region_select(request):
    cities = County.objects.values_list('city_name', flat=True).distinct()

    if request.method == 'POST':
        selected_city = request.POST.get('city_name', '')
        selected_town = request.POST.get('first_town_name', '')
    elif request.method == 'GET':
        selected_city = request.GET.get('city_name', '')
        selected_town = request.GET.get('first_town_name', '')
    
    towns = County.objects.filter(city_name=selected_city) if selected_city else []
    accommodations = Accommodation.objects.filter(city__city_name=selected_city, city__first_town_name=selected_town) if selected_town else []
    

    # 리뷰 가져오기
    reviews = Review.objects.filter(accommodation__in=accommodations)
        
    # 좋아요 수 계산
    likes_count = sum(accommodation.like.count() for accommodation in accommodations)
    reviews_count = reviews.count()
    # likes_count = accommodations.like.count()



    # 리뷰의 평균 별점 계산
    if reviews_count > 0:
        average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    else:
        average_rating = 0
    
    accommodation_images = []
    for accommodation in accommodations:

        first_image = AccommodationImage.objects.filter(accommodation=accommodation).first()
        if first_image:
            accommodation_images.append(first_image)

    context = {
        'cities': cities,
        'selected_city': selected_city,
        'towns': towns,
        'selected_town': selected_town,
        'accommodations': accommodations,
        'accommodation_images': accommodation_images,
        'MEDIA_URL': settings.MEDIA_URL,
        'reviews_count': reviews_count,
        'likes_count': likes_count,
        'average_rating': average_rating,
    }
    
    return render(request, 'accommodation/region_select.html', context)


# 숙소 유형 선택 후 지역 선택 페이지 (풀빌라, 글램핑, 부티끄 모텔 등등)
def accommodation_type_region_select(request, accommodation_type):
    accommodations = Accommodation.objects.filter(accommodation_type=accommodation_type)
    counties = County.objects.all()  # 모든 도시 정보 가져오기

    county_images = []
    for county in counties:
        # 각 도시에 해당하는 이미지 중 첫 번째 이미지만 가져오기
        county_image = CountyImg.objects.filter(city_name=county).first()
        if county_image:
            county_images.append(county_image)

    context = {
        'accommodations': accommodations,
        'county_images': county_images,
        'accommodation_type': accommodation_type,
    }

    return render(request, 'accommodation/accommodation_type_region_select.html', context)

# accommodation_type을 accommodation_type_name으로 변환
def get_accommodation_type_name(accommodation_type):
    for type_code, type_name in DOMESTIC_ACCOMMODATION_TYPES:
        if type_code == accommodation_type:
            return type_name
    return accommodation_type


# 숙소 유형 선택, 지역 선택 후 뜨는 페이지
def accommodation_region_list(request, accommodation_type, city_name):
    if city_name == 'all':
        accommodations = Accommodation.objects.filter(accommodation_type=accommodation_type)
    else:
        county = get_object_or_404(County, city_name=city_name)
        accommodations = Accommodation.objects.filter(accommodation_type=accommodation_type, city=county)

        # 리뷰 가져오기
        reviews = Review.objects.filter(accommodation__in=accommodations)
            
        # 좋아요 수 계산
        likes_count = sum(accommodation.like.count() for accommodation in accommodations)
        reviews_count = reviews.count()
       
        # 리뷰의 평균 별점 계산
        if reviews_count > 0:
            average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        else:
            average_rating = 0

        accommodation_images = []
        for accommodation in accommodations:
            first_image = AccommodationImage.objects.filter(accommodation=accommodation).first()
            if first_image:
                accommodation_images.append(first_image)

        accommodation_type_name = get_accommodation_type_name(accommodation_type)
    
    context = {
        'accommodations': accommodations,
        'accommodation_type': accommodation_type,
        'city_name': city_name,
        'accommodation_images': accommodation_images,
        'reviews_count': reviews_count,
        'likes_count': likes_count,
        'average_rating': average_rating,
        'accommodation_type_name': accommodation_type_name,

    }
    
    return render(request, 'accommodation/accommodation_region_list.html', context)

@login_required
@csrf_exempt
def like_accommodation(request, accommodation_pk):
    if request.method == 'POST':
        accommodation = get_object_or_404(Accommodation, pk=accommodation_pk)
        like, created = AccommodationLike.objects.get_or_create(accommodation=accommodation, user=request.user)
        if created:
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'status': 'already_liked'})
    return JsonResponse({'status': 'error'}, status=400)


@login_required
@csrf_exempt
def unlike_accommodation(request, accommodation_pk):
    if request.method == 'POST':
        accommodation = get_object_or_404(Accommodation, pk=accommodation_pk)
        AccommodationLike.objects.filter(accommodation=accommodation, user=request.user).delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)



def search_accommodations(request):
    query = request.GET.get('q', '').strip()

    # 사용자가 이전에 본 숙소 목록을 세션에서 가져오기
    viewed_accommodations = request.session.get('viewed_accommodations', [])

    if query:
        # 숙소 이름 또는 위치를 기반으로 검색
        accommodations = Accommodation.objects.filter(
            Q(name__icontains=query) | 
            Q(city__city_name__icontains=query) | 
            Q(city__first_town_name__icontains=query)
        )
        
        results = []
        for accommodation in accommodations:
            first_image = accommodation.images.first()  # 숙소에 연결된 첫 번째 이미지 가져오기
           
            if accommodation.city:
                location = f'{accommodation.city.city_name} {accommodation.city.first_town_name}'
            else:
                location = '위치 정보 없음'
            image_url = first_image.images.url if first_image else None
            results.append({
                'name': accommodation.name,
                'first_image_file': image_url,
                'location': location,
                'id': accommodation.pk,
    
            })
            # 현재 숙소를 리스트에 추가하고, 중복 제거 및 최신 5개만 유지
            if accommodation.pk not in viewed_accommodations:
                viewed_accommodations.append(accommodation.pk)
                viewed_accommodations = viewed_accommodations[-5:]
    else:
        results = []
          
    # 수정된 viewed_accommodations 리스트를 세션에 저장
    request.session['viewed_accommodations'] = viewed_accommodations
    
    return render(request, 'accommodation/search_accommodations.html', 
                  {'results': results,
                    'query': query,
                    'viewed_accommodations': viewed_accommodations,})

from datetime import datetime, timedelta
class CheckAvailabilityAPI(View):
    def get(self, request):
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        accommodation_id = request.GET.get('accommodation_id')
        room_pk = request.GET.get('room_pk')

        # 날짜 문자열을 datetime 객체로 변환
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        # 예약 가능 여부 확인
        available = check_availability(accommodation_id, start_date, end_date, room_pk)

        # JSON 응답 반환
        data = {'available': available}
        return JsonResponse(data)
    
def check_availability(accommodation_id, start_date, end_date, room_pk):
    # 예약 가능 여부를 판단할 날짜 범위
    reservation_start = start_date
    reservation_end = end_date 

    # 선택한 객실과 예약된 예약을 확인
    reserved_room = Reservation.objects.filter(
        accommodation_id=accommodation_id,
        room_id=room_pk,
        check_in__lte=reservation_end,  # 예약 시작일이 예약 종료일보다 작거나 같아야 함
        check_out__gte=reservation_start  # 예약 종료일이 예약 시작일보다 크거나 같아야 함
    )

    if reserved_room.exists():
        return False  # 예약 불가능: 이미 예약된 객실이 있는 경우
    else:
        return True   # 예약 가능: 예약된 객실이 없는 경우
    

def reservation_success(request, reservation_id):
    # 예약 정보를 데이터베이스에서 가져옵니다.
    # 예시로, reservation_id를 사용하여 예약 정보를 조회한다고 가정합니다.
    reservation = get_object_or_404(Reservation, pk=reservation_id)
     # 해당 숙소와 연결된 모든 이미지를 가져옵니다.
    accommodation_images = AccommodationImage.objects.filter(accommodation=reservation.accommodation)
    
    # 예약 정보를 템플릿에 전달합니다.
    context = {
        'reservation': reservation,
        'accommodation_images': accommodation_images}
    return render(request, 'accommodation/reservation_success.html', context)