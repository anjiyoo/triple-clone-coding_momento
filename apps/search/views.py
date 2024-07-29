# views.py
from django.shortcuts import render
from apps.accommodation.models import Accommodation
from apps.baenangtalk.models import Baenangtalk
from .forms import SearchForm
from django.db.models import Q,Count
from django.core.paginator import Paginator
# from apps.tour.models import
# from apps.plan.models import 


def search(request):
    form = SearchForm()
    query = None
    results1 = []
    results2 = []
    best_bae = []
    best_accommodation = []
    
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # 숙소 검색
            results1 = Accommodation.objects.filter(
                Q(name__icontains=query) | 
                Q(city__city_name__icontains=query) | 
                Q(location__icontains=query) | 
                Q(description__icontains=query)
            ).prefetch_related('images')
            # 배낭톡 검색
            results2 = Baenangtalk.objects.filter(
                Q(county__city_name__icontains=query) | 
                Q(subject__bae_sub_name__icontains=query) | 
                Q(bae_title__icontains=query) | 
                Q(bae_content__icontains=query)
            )
            # 추천 배낭톡
            best_bae = results2.order_by('-bae_like')[:5]
            # 추천 숙소 
            best_accommodation = results1.annotate(num_likes=Count('like')).order_by('-num_likes')[:5]

    

    return render(request, 'search/search.html', {'form': form, 'query': query, 'results1': results1, 'results2': results2,'best_bae': best_bae, 'best_accommodation': best_accommodation})


