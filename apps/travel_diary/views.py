from django.shortcuts import render
from django.views.generic import CreateView ,ListView, DetailView, UpdateView
from .forms import DiaryForm
from apps.plan.models import Trip,DayPlan
from datetime import datetime, timedelta
from .models import tag,diary
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy
import os
KAKAO_API_KEY = os.getenv('KAKAO_API_KEY')
REST_API_KEY = os.getenv('REST_API_KEY')
class DiaryCreateView(CreateView):
    template_name = 'create_form.html'
    success_url = '/'
    form_class = DiaryForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trip_id = self.kwargs['trip_id']
        trip = Trip.objects.get(id=trip_id)
        # 날짜 계산
        day_cnt = (trip.end_date - trip.start_date).days
        week = {0:'월', 1:'화', 2:'수', 3:'목', 4:'금', 5:'토', 6:'일'}
        day = trip.start_date.weekday()
        days = [trip.start_date.strftime("%m.%d/"+week[day])]
        for i in range(1, day_cnt+1):
            new = trip.start_date + timedelta(days=i) 
            new_week = new.weekday()
            days.append(new.strftime("%m.%d/"+week[new_week]))
        # origin day
        origin_day = [trip.start_date.strftime("%Y-%m-%d")]
        for i in range(1, day_cnt+1):
            new = trip.start_date + timedelta(days=i)
            origin_day.append(new.strftime("%Y-%m-%d"))
        days = zip(days, origin_day)
        # 일자별 게획
        plan = DayPlan.objects.filter(trip=trip)
        context['trip_id'] = trip_id
        context['trip'] = trip
        context['days'] = days
        context['plan'] = plan
        return context
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.trip_id = self.kwargs['trip_id']
        # 먼저 폼을 저장하여 self.object를 초기화합니다.
        response = super().form_valid(form)
        # 태그 처리
        tags = self.request.POST.getlist('tags')
        for tag_name in tags:
            Tag, created = tag.objects.get_or_create(name=tag_name)
            self.object.tags.add(Tag)
        return response
    
class DiaryList(ListView):
    model = diary
    template_name = 'diary_list.html'
    ordering = '-pk'
    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user).order_by(self.ordering)
class DiaryDetail(DetailView):
    model = diary
    template_name = 'diary_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trip_id = diary.objects.get(id=self.kwargs['pk']).trip_id
        trip=context['object'].trip
        # 날짜 계산
        day_cnt = (trip.end_date - trip.start_date).days
        week = {0:'월', 1:'화', 2:'수', 3:'목', 4:'금', 5:'토', 6:'일'}
        day = trip.start_date.weekday()
        days = [trip.start_date.strftime("%m.%d/"+week[day])]
        for i in range(1, day_cnt+1):
            new = trip.start_date + timedelta(days=i) 
            new_week = new.weekday()
            days.append(new.strftime("%m.%d/"+week[new_week]))
        # origin day
        origin_day = [trip.start_date.strftime("%Y-%m-%d")]
        for i in range(1, day_cnt+1):
            new = trip.start_date + timedelta(days=i)
            origin_day.append(new.strftime("%Y-%m-%d"))
        days = zip(days, origin_day)
        # 일자별 게획
        plan = DayPlan.objects.filter(trip=trip)
        context['day_list'] = origin_day
        context['trip_id'] = trip_id
        context['trip'] = trip
        context['days'] = days
        context['plan'] = plan
        context['KAKAO_API_KEY'] = KAKAO_API_KEY
        context['REST_API_KEY'] = REST_API_KEY
        return context

class DiaryUpdate(UpdateView):
    model = diary
    context_object_name = 'diary' #1
    form_class = DiaryForm
    template_name = 'update_form.html' #2
    success_url = '/' 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trip_id = self.kwargs.get('trip_id')
        trip=Trip.objects.get(id=trip_id)

        # 날짜 계산
        day_cnt = (trip.end_date - trip.start_date).days
        week = {0:'월', 1:'화', 2:'수', 3:'목', 4:'금', 5:'토', 6:'일'}
        day = trip.start_date.weekday()
        days = [trip.start_date.strftime("%m.%d/"+week[day])]
        for i in range(1, day_cnt+1):
            new = trip.start_date + timedelta(days=i) 
            new_week = new.weekday()
            days.append(new.strftime("%m.%d/"+week[new_week]))
        # origin day
        origin_day = [trip.start_date.strftime("%Y-%m-%d")]
        for i in range(1, day_cnt+1):
            new = trip.start_date + timedelta(days=i)
            origin_day.append(new.strftime("%Y-%m-%d"))
        days = zip(days, origin_day)
        # 일자별 게획
        plan = DayPlan.objects.filter(trip=trip)
        
        context['days'] = days
        context['plan'] = plan
        context['trip'] = trip
        return context
    def get_object(self, queryset=None):
        diary_id = self.kwargs.get('diary_id')
        return diary.objects.get(id=diary_id)