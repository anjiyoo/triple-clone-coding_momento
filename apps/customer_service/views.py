from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
import requests
from django.db.models import Q
# Create your views here.
from django.views.generic import ListView, DetailView, CreateView
from .forms import InquiryForm,CommentcreateForm,FaqcreateForm,InquiryImageForm,SearchForm,NoticecreateForm
from .models import InquiryImage,Inquiry,InquiryComment,Faq,Notice
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin




class InquiryCreateView(CreateView):
    template_name = 'customer_service/inquiry_create.html'

    def get(self, request):
        form = InquiryForm()  # 폼 인스턴스 생성
        imageform = InquiryImageForm()
        return render(request, self.template_name, {'form': form, 'imageform': imageform})

    def post(self, request):
        form = InquiryForm(request.POST, request.FILES)  # POST 데이터와 파일 데이터를 받아 폼 인스턴스 생성
        imageform = InquiryImageForm(request.POST, request.FILES)

        if form.is_valid():
            # 폼이 유효하면 데이터 저장
            inquiry = form.save(commit=False)  # 데이터베이스에 바로 저장하지 않고 인스턴스 생성
            inquiry.user = request.user  # 현재 사용자를 작성자로 설정 
            inquiry.created_by = request.user  # 현재 사용자를 작성자로 설정
            inquiry.save()  # 데이터베이스에 저장

            # 이미지 저장
            images = request.FILES.getlist('image')
            for image in images:
                InquiryImage.objects.create(inquiry=inquiry, image=image)

            # 게시글 작성 완료 후 리다이렉트
            return redirect('customer_service:my_inquiry_list') 


        return render(request, self.template_name, {'form': form, 'imageform': imageform})

    
# views.py

# class InquiryListView(ListView):
#     template_name = 'customer_service/customer_service.html'
#     context_object_name = 'inquirys'
#     model = Inquiry

#     def get_queryset(self):
#         return Inquiry.objects.order_by('-created_at')[:10]

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         user_inquiries = [inquiry.inquiries_id for inquiry in Inquiry.objects.all() if inquiry.created_by == self.request.user]
#         context['user_inquiries'] = user_inquiries
#         context['is_admin'] = self.request.user.is_staff 
#         return context

    

    
class InquiryDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    template_name = 'customer_service/inquiry_detail.html'
    model = Inquiry
    context_object_name = 'inquiry'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inquiry = self.get_object()
        context['profile'] = inquiry.created_by.profile
        context['inquiry_image'] = InquiryImage.objects.filter(inquiry=inquiry).first()
        context['comments'] = InquiryComment.objects.filter(post=inquiry)
        context['form'] = CommentcreateForm()
        return context

    def test_func(self):
        inquiry = self.get_object()
        return self.request.user == inquiry.created_by or self.request.user.is_staff

    def handle_no_permission(self):
        return redirect('customer_service:customer_service')

    def post(self, request, *args, **kwargs):
        inquiry = self.get_object()
        form = CommentcreateForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = inquiry
            comment.created_by = request.user
            comment.save()
            inquiry.answer_status = True
            inquiry.save()
            return redirect('customer_service:my_inquiry_list')
        context = self.get_context_data()
        context['form'] = form
        return render(request, self.template_name, context)
    

class MyInquiryListView(ListView):
    template_name = 'customer_service/my_inquiry_list.html'
    context_object_name = 'my_inquiries'
    paginate_by = 10  # 한 페이지에 표시할 객체 수

    def get_queryset(self):
        return Inquiry.objects.filter(created_by=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_numbers_range = 100
        paginator = context['paginator']
        page_obj = context['page_obj']
        max_index = len(paginator.page_range)
        current_page = page_obj.number

        start_index = int((current_page - 1) / page_numbers_range) * page_numbers_range
        end_index = start_index + page_numbers_range
        if end_index >= max_index:
            end_index = max_index

        page_range = paginator.page_range[start_index:end_index]
        context['page_range'] = page_range
        return context


class FaqCreateView(CreateView):
    template_name = "customer_service/faq_create.html"

    def get(self, request):
        form = FaqcreateForm()  # 폼 인스턴스 생성
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = FaqcreateForm(request.POST)  # POST 데이터와 파일 데이터를 받아 폼 인스턴스 생성

        if form.is_valid():
            # 폼이 유효하면 데이터 저장
            faq = form.save(commit=False)  # 데이터베이스에 바로 저장하지 않고 인스턴스 생성
            faq.save()  # 데이터베이스에 저장

            # 게시글 작성 완료 후 리다이렉트
            return redirect('customer_service:customer_service')



# class FaqBestAnswerView(ListView):
#     template_name = "customer_service/customer_service.html"
#     context_object_name = 'faq'  # main query context name
#     model = Faq  # main query model

#     def get_queryset(self):
#         return Faq.objects.all()

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['faq_flight'] = Faq.objects.filter(faq_category_id='1').order_by('id')[:4]
#         context['faq_accommodations'] = Faq.objects.filter(faq_category_id='2').order_by('id')[:4]
#         context['faq_tourticket'] = Faq.objects.filter(faq_category_id='3').order_by('id')[:4]
#         context['faq_service'] = Faq.objects.filter(faq_category_id='4').order_by('id')[:4]
#         context['faq_common'] = Faq.objects.filter(faq_category_id='5').order_by('id')[:4]
#         return context



class CustomerServiceView(ListView):
    template_name = "customer_service/customer_service.html"
    context_object_name = 'inquirys'
    model = Inquiry
    def get_queryset(self):
        queryset = Inquiry.objects.order_by('-created_at')[:10]
        for inquiry in queryset:
            if inquiry.created_by and inquiry.created_by.username:
                inquiry.created_by_masked = inquiry.created_by.username[:2] + "***"
            else:
                inquiry.created_by_masked = "xxx"
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_inquiries = Inquiry.objects.filter(created_by=self.request.user).values_list('inquiries_id', flat=True)
        context['user_inquiries'] = list(user_inquiries)
        context['is_admin'] = self.request.user.is_staff 
        context['faq_best'] = Faq.objects.order_by('id')[:4]
        context['faq_flight'] = Faq.objects.filter(faq_category_id='1').order_by('id')[:4]
        context['faq_accommodations'] = Faq.objects.filter(faq_category_id='2').order_by('id')[:4]
        context['faq_tourticket'] = Faq.objects.filter(faq_category_id='3').order_by('id')[:4]
        context['faq_service'] = Faq.objects.filter(faq_category_id='4').order_by('id')[:4]
        context['faq_common'] = Faq.objects.filter(faq_category_id='5').order_by('id')[:4]
        return context

# class InquiryListView(ListView):
#     template_name = 'customer_service/customer_service.html'
#     context_object_name = 'inquirys'
#     model = Inquiry

#     def get_queryset(self):
#         return Inquiry.objects.order_by('-created_at')[:10]

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         user_inquiries = [inquiry.inquiries_id for inquiry in Inquiry.objects.all() if inquiry.created_by == self.request.user]
#         context['user_inquiries'] = user_inquiries
#         context['is_admin'] = self.request.user.is_staff 
#         return context

class FaqDetailView(DetailView):
    template_name = 'customer_service/faq_detail.html'
    model = Faq
    context_object_name = 'faq'


class FaqListView(ListView):
    template_name = 'customer_service/faq_list.html'
    model = Faq
    context_object_name = 'faq'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('query')

        if query:
            context['faq_flight'] = Faq.objects.filter(
                Q(faq_category_id='1') & (Q(faq_title__icontains=query) | Q(faq_answer__icontains=query))
            )
            context['faq_accommodations'] = Faq.objects.filter(
                Q(faq_category_id='2') & (Q(faq_title__icontains=query) | Q(faq_answer__icontains=query))
            )
            context['faq_tourticket'] = Faq.objects.filter(
                Q(faq_category_id='3') & (Q(faq_title__icontains=query) | Q(faq_answer__icontains=query))
            )
            context['faq_service'] = Faq.objects.filter(
                Q(faq_category_id='4') & (Q(faq_title__icontains=query) | Q(faq_answer__icontains=query))
            )
            context['faq_common'] = Faq.objects.filter(
                Q(faq_category_id='5') & (Q(faq_title__icontains=query) | Q(faq_answer__icontains=query))
            )
        else:
            context['faq_flight'] = Faq.objects.filter(faq_category_id='1')
            context['faq_accommodations'] = Faq.objects.filter(faq_category_id='2')
            context['faq_tourticket'] = Faq.objects.filter(faq_category_id='3')
            context['faq_service'] = Faq.objects.filter(faq_category_id='4')
            context['faq_common'] = Faq.objects.filter(faq_category_id='5')

        context['form'] = SearchForm()
        return context
    

class AdminInquiryListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'customer_service/admin_inquiry_list.html'
    context_object_name = 'inquirys'
    model = Inquiry
    paginate_by = 10

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return redirect('customer_service:customer_service')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_inquiries = Inquiry.objects.filter(created_by=self.request.user).values_list('inquiries_id', flat=True)
        context['user_inquiries'] = user_inquiries
        context['is_admin'] = self.request.user.is_staff 
        page_numbers_range = 100
        paginator = context['paginator']
        page_obj = context['page_obj']
        max_index = len(paginator.page_range)
        current_page = page_obj.number

        start_index = int((current_page - 1) / page_numbers_range) * page_numbers_range
        end_index = start_index + page_numbers_range
        if end_index >= max_index:
            end_index = max_index

        page_range = paginator.page_range[start_index:end_index]
        context['page_range'] = page_range
        return context
    
class NoticeCreateView(LoginRequiredMixin, UserPassesTestMixin,CreateView):
    template_name = 'customer_service/notice_create.html'

    def get(self, request):
        form = NoticecreateForm()  # 폼 인스턴스 생성
        return render(request, self.template_name, {'form': form})
    
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return redirect('customer_service:customer_service')        

    def post(self, request):
        form = NoticecreateForm(request.POST)  # POST 데이터와 파일 데이터를 받아 폼 인스턴스 생성

        if form.is_valid():
            # 폼이 유효하면 데이터 저장
            notice = form.save(commit=False)  # 데이터베이스에 바로 저장하지 않고 인스턴스 생성
            notice.save()  # 데이터베이스에 저장

            # 게시글 작성 완료 후 리다이렉트
            return redirect('customer_service:notice_list')

class NoticeListView(ListView):
    template_name = 'customer_service/notice_list.html'
    context_object_name = 'notice'
    paginate_by = 10  # 한 페이지에 표시할 객체 수

    def get_queryset(self):
        return Notice.objects.filter().order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_numbers_range = 100
        paginator = context['paginator']
        page_obj = context['page_obj']
        max_index = len(paginator.page_range)
        current_page = page_obj.number

        start_index = int((current_page - 1) / page_numbers_range) * page_numbers_range
        end_index = start_index + page_numbers_range
        if end_index >= max_index:
            end_index = max_index

        page_range = paginator.page_range[start_index:end_index]
        context['page_range'] = page_range
        return context
    
class NoticeDetailView(DetailView):
    template_name = 'customer_service/notice_detail.html'
    model = Notice
    context_object_name = 'notice'