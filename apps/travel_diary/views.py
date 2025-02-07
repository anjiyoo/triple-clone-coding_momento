from typing import Any
from django.shortcuts import render
from django.views.generic import CreateView ,ListView, DetailView, UpdateView, DeleteView
from .forms import DiaryForm,CommentcreateForm, CommentEditForm
from apps.plan.models import Trip,DayPlan
from datetime import datetime, timedelta
from .models import tag,diary,DiaryComment
from django.shortcuts import redirect ,get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
import os
from django.contrib.auth.decorators import login_required
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
        try:
            if self.request.FILES['image']:
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
        except:
            # 적절한 오류 메시지와 함께 다른 페이지로 리다이렉트
            messages.error(self.request, "입력 정보를 확인해주세요.")
            # 폼이 유효하지 않으면 다시 폼을 보여줌
            return redirect('travel_diary:create', trip_id=self.kwargs['trip_id'])
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

        comments = DiaryComment.objects.filter(diary=self.kwargs['pk'])  
        form = CommentcreateForm()  # 댓글 폼 초기화

        context['day_list'] = origin_day
        context['trip_id'] = trip_id
        context['trip'] = trip
        context['days'] = days
        context['plan'] = plan
        context['form'] = form
        context['comments'] = comments
        context['KAKAO_API_KEY'] = KAKAO_API_KEY
        context['REST_API_KEY'] = REST_API_KEY
        return context
    
    
    
    # POST 요청 처리
    def post(self, request, pk):  
        form = CommentcreateForm(request.POST)
        # 입력된 데이터 유효성 검사
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user  # 요청을 보낸 사용자 = 댓글의 작성자
            comment.diary = diary.objects.get(pk=pk)  
            comment.save()  # DB 저장
            return redirect('travel_diary:diary_detail', pk=pk)

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
    
class DiaryDelete(DeleteView):
    model = diary
    template_name = 'diary_delete.html'
    success_url = reverse_lazy('travel_diary:diary_list')

# 댓글 좋아요
@login_required
def com_like(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(DiaryComment, id=comment_id)
        user = request.user  # 현재 로그인된 사용자


        if user not in comment.diary_com_like_by.all():
            comment.diary_com_like_by.add(user)
            comment.diary_com_like += 1
            comment.save()
        return redirect('travel_diary:diary_detail', pk=comment.diary.pk)

    return redirect('travel_diary:diary_detail', pk=comment.diary.pk)



# 댓글 좋아요 취소
@login_required
def com_unlike(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(DiaryComment, id=comment_id)
        user = request.user  # 현재 로그인된 사용자

        if user in comment.diary_com_like_by.all():
            comment.diary_com_like_by.remove(user)
            comment.diary_com_like -= 1
            comment.save()
        return redirect('travel_diary:diary_detail', pk=comment.diary.pk)

    return redirect('travel_diary:diary_detail', pk=comment.diary.pk)

# 댓글 수정
def com_edit(request, comment_id):
    comment = get_object_or_404(DiaryComment, id=comment_id)
    
    if request.method == 'POST':
        form = CommentEditForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('travel_diary:diary_detail', pk=comment.diary.pk) # 댓글이 수정된 후 게시글 상세페이지로 이동
    else:
        form = CommentEditForm(instance=comment)
    
    return render(request, 'diary_comment_edit.html', {'form': form})

# 댓글 삭제
@login_required
def com_delete(request, comment_id):
    comment = get_object_or_404(DiaryComment, id=comment_id)
    if request.method == 'GET':
        if comment.diary:  # comment.bae가 존재하는지 확인
            comment.delete()
            return redirect('travel_diary:diary_detail', pk=comment.diary.pk)