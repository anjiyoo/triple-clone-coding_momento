from django.shortcuts import render

# Create your views here.
from .models import *
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect, get_object_or_404
from .forms import * 
from django.contrib.auth.decorators import login_required

# 배낭톡 main + post ##############################################################################

# 배낭톡 main
class MainPostListView(ListView):
    model = Baenangtalk
    template_name = 'bae_main.html'
    context_object_name = 'posts'

    def get_queryset(self):
        # 모든 객체 가져오기
        queryset = Baenangtalk.objects.all() 

        # URL에서 전달된 county_id, period_id, subject_id 가져오기
        county_id = self.request.GET.get('county_id')  
        period_id = self.request.GET.get('period_id') 
        subject_id = self.request.GET.get('subject_id') 

        # 필터링 조건 추가
        if county_id:
            queryset = queryset.filter(county_id=county_id)
        if period_id:
            queryset = queryset.filter(period_id=period_id)
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)

        # 내림차순 정렬
        return queryset.order_by('-bae_date')

    # 템플릿에 전달할 data
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # URL에서 전달된 county_id, period_id, subject_id 가져오기
        county_id = self.request.GET.get('county_id') 
        period_id = self.request.GET.get('period_id')  
        subject_id = self.request.GET.get('subject_id')  

        if county_id:
            context['selected_county'] = County.objects.get(pk=county_id)
        if period_id:
            context['selected_period'] = BaenangtalkPeriod.objects.get(pk=period_id)
        if subject_id:
            context['selected_subject'] = BaenangtalkSubject.objects.get(pk=subject_id)

        if county_id:
            context['county_id'] = int(county_id)
        if period_id:
            context['period_id'] = int(period_id)
        if subject_id:
            context['subject_id'] = int(subject_id)

        # 모든 county 가져오기
        context['counties'] = County.objects.all()
        # 모든 여행시기 가져오기
        context['periods'] = BaenangtalkPeriod.objects.all()
        # 모든 주제 가져오기
        context['subjects'] = BaenangtalkSubject.objects.all()

        return context
    

# 배낭톡 detail
class PostDetailView(DetailView):
    template_name = 'post/bae_detail.html'

    def get(self, request, pk):
        baenangtalk = get_object_or_404(Baenangtalk, pk=pk)  # Baenangtalk 객체 가져오기
        comments = BaenangtalkComment.objects.filter(bae=baenangtalk)  # BaenangtalkComment 객체 가져오기
        form = CommentcreateForm()  # 댓글 폼 초기화

        # 템플릿으로 전달할 data 
        context = {
            'profile': baenangtalk.user.profile,
            'nickname': baenangtalk.user.username,
            'period': baenangtalk.period.bae_month,
            'county': baenangtalk.county.city_name,
            'subject': baenangtalk.subject.bae_sub_name,
            'bae_title': baenangtalk.bae_title,
            'bae_img': baenangtalk.bae_img,
            'bae_content': baenangtalk.bae_content,
            'bae_date': baenangtalk.bae_date,
            'bae_like': baenangtalk.bae_like,
            'form': form,
            'comments': comments,
            'baenangtalk': baenangtalk 
        }

        return render(request, self.template_name, context)

    # POST 요청 처리
    def post(self, request, pk):
        baenangtalk = get_object_or_404(Baenangtalk, pk=pk)  
        form = CommentcreateForm(request.POST)
        # 입력된 데이터 유효성 검사
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user  # 요청을 보낸 사용자 = 댓글의 작성자
            comment.bae = baenangtalk  # 해당 댓글이 속한 게시글 설정
            comment.save()  # DB 저장
            return redirect('baenangtalk:bae_detail', pk=pk)
        else:
            comments = BaenangtalkComment.objects.filter(bae=baenangtalk)
            context = {
                'profile': baenangtalk.user.profile,
                'nickname': baenangtalk.user.username,
                'period': baenangtalk.period.bae_month,
                'county': baenangtalk.county.city_name,
                'subject': baenangtalk.subject.bae_sub_name,
                'bae_title': baenangtalk.bae_title,
                'bae_img': baenangtalk.bae_img,
                'bae_content': baenangtalk.bae_content,
                'bae_date': baenangtalk.bae_date,
                'bae_like': baenangtalk.bae_like,
                'form': form,
                'comments': comments,
                'baenangtalk': baenangtalk 
            }
            return render(request, self.template_name, context)
    

# 배낭톡 create
class PostCreateView(CreateView):
    template_name = 'post/bae_create.html'

    def get(self, request):
        form = BaenangtalkForm()  # 폼 인스턴스 생성
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = BaenangtalkForm(request.POST, request.FILES)  # POST 데이터와 파일 데이터를 받아 폼 인스턴스 생성

        if form.is_valid():
            # 폼이 유효하면 데이터 저장
            baenangtalk = form.save(commit=False)  # 데이터베이스에 바로 저장하지 않고 인스턴스 생성
            baenangtalk.user = request.user  # 현재 사용자를 작성자로 설정 
            baenangtalk.save()  # 데이터베이스에 저장

            # 게시글 작성 완료 후 리다이렉트
            return redirect('baenangtalk:bae_detail', pk=baenangtalk.pk)  # 작성된 게시글의 상세 페이지로 리다이렉트

        # 폼이 유효하지 않으면 다시 폼을 보여줌
        return render(request, self.template_name, {'form': form})


# 배낭톡 edit
class PostEditView(UpdateView):
    template_name = 'post/bae_edit.html'

    def get(self, request, pk):
        baenangtalk = get_object_or_404(Baenangtalk, pk=pk)

        # 현재 사용자가 작성자인지 확인
        if baenangtalk.user != request.user:
            return redirect('baenangtalk:bae_detail', pk=pk)

        form = BaenangtalkForm(instance=baenangtalk)
        return render(request, self.template_name, {'form': form, 'baenangtalk': baenangtalk})

    def post(self, request, pk):
        baenangtalk = get_object_or_404(Baenangtalk, pk=pk)

        # 현재 사용자가 작성자인지 확인
        if baenangtalk.user != request.user:
            return redirect('baenangtalk:bae_detail', pk=pk)

        form = BaenangtalkForm(request.POST, request.FILES, instance=baenangtalk)

        if form.is_valid():
            baenangtalk = form.save()

            # 수정 완료 후 리다이렉트
            return redirect('baenangtalk:bae_detail', pk=pk)

        # 폼이 유효하지 않으면 다시 폼을 보여줌
        return render(request, self.template_name, {'form': form, 'baenangtalk': baenangtalk})


# 배낭톡 delete
class PostDeleteView(DeleteView):
    model = Baenangtalk  # Baenangtalk 모델을 대상으로 한다고 명시
    template_name = 'post/bae_delete.html'

    def post(self, request, pk):
        baenangtalk = get_object_or_404(Baenangtalk, pk=pk)  # pk에 해당하는 Baenangtalk 객체 가져오기

        # 현재 사용자가 작성자인지 확인
        if baenangtalk.user == request.user:
            # 작성자일 경우 삭제
            baenangtalk.delete()

        # 삭제 후 리다이렉트할 URL 설정 
        return redirect('baenangtalk:bae_main') 


# 배낭톡 좋아요 ##############################################################################


# 배낭톡 게시글 좋아요
@login_required
def bae_post_like(request, pk):
    if request.method == 'POST':
        post = get_object_or_404(Baenangtalk, pk=pk)
        user = request.user  # 현재 로그인된 사용자

        if user not in post.bae_like_by.all():
            post.bae_like_by.add(user)
            post.bae_like += 1
            post.save()
        return redirect('baenangtalk:bae_detail', pk=pk)
        
    return redirect('baenangtalk:bae_detail', pk=pk)


# 배낭톡 게시글 좋아요 취소
@login_required
def bae_post_unlike(request, pk):
    if request.method == 'POST':
        post = get_object_or_404(Baenangtalk, pk=pk)
        user = request.user  # 현재 로그인된 사용자

        if user in post.bae_like_by.all():
            post.bae_like_by.remove(user)
            post.bae_like -= 1
            post.save()
        return redirect('baenangtalk:bae_detail', pk=pk)

    return redirect('baenangtalk:bae_detail', pk=pk)


# 댓글 ##############################################################################

# 댓글 수정
def com_edit(request, comment_id):
    comment = get_object_or_404(BaenangtalkComment, id=comment_id)
    
    if request.method == 'POST':
        form = CommentEditForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('baenangtalk:bae_detail', pk=comment.bae.pk) # 댓글이 수정된 후 게시글 상세페이지로 이동
    else:
        form = CommentEditForm(instance=comment)
    
    return render(request, 'comment/com_edit.html', {'form': form})



# 댓글 삭제
@login_required
def com_delete(request, comment_id):
    comment = get_object_or_404(BaenangtalkComment, id=comment_id)
    if request.method == 'POST':
        if comment.bae:  # comment.bae가 존재하는지 확인
            comment.delete()
            return redirect('baenangtalk:bae_detail', pk=comment.bae.pk)
        else:
            # 적절한 오류 메시지와 함께 다른 페이지로 리다이렉트
            messages.error(request, "관련 게시글이 존재하지 않습니다.")
            return redirect('baenangtalk:bae_main')  # 예를 들어 메인 페이지로 리다이렉트
    else:
        if comment.bae:
            return render(request, 'comment/com_delete.html', {'object': comment})
        else:
            messages.error(request, "관련 게시글이 존재하지 않습니다.")
            return redirect('baenangtalk:bae_main')



# 댓글 좋아요
@login_required
def com_like(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(BaenangtalkComment, id=comment_id)
        user = request.user  # 현재 로그인된 사용자


        if user not in comment.bae_com_like_by.all():
            comment.bae_com_like_by.add(user)
            comment.bae_com_like += 1
            comment.save()
        return redirect('baenangtalk:bae_detail', pk=comment.bae.pk)

    return redirect('baenangtalk:bae_detail', pk=comment.bae.pk)



# 댓글 좋아요 취소
@login_required
def com_unlike(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(BaenangtalkComment, id=comment_id)
        user = request.user  # 현재 로그인된 사용자

        if user in comment.bae_com_like_by.all():
            comment.bae_com_like_by.remove(user)
            comment.bae_com_like -= 1
            comment.save()
        return redirect('baenangtalk:bae_detail', pk=comment.bae.pk)

    return redirect('baenangtalk:bae_detail', pk=comment.bae.pk)
