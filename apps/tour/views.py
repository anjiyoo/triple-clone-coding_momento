from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import TourInfo, OptionsTour

def tour_detail(request, tour_id):
    tour = get_object_or_404(TourInfo, pk=tour_id)
    date_prices = OptionsTour.objects.filter(tour=tour).order_by('date')[:5]
    context = {
        'tour': tour,
        'date_prices': date_prices,
    }
    return render(request, 'tour_detail.html', context)

def get_price_options(request):
    date = request.GET.get('date')
    tour_id = request.GET.get('tour_id')
    price_options = OptionsTour.objects.filter(tour_id=tour_id, date=date)
    data = [{'name': option.name, 'price': option.price} for option in price_options]
    return JsonResponse(data, safe=False)

def tour_main(request):
    tours = TourInfo.objects.all()
    context = {
        'tours': tours,
    }
    return render(request, 'tour_main.html', context)


def search_results(request):
    search_term = request.GET.get('title', '')  # 검색어 가져오기
    results = TourInfo.objects.filter(tour_name__icontains=search_term)  # 검색어로 필터링
    return render(request, 'search_results.html', {'results': results, 'search_term': search_term})
