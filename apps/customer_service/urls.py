from django.urls import path
from .views import InquiryCreateView,InquiryDetailView,MyInquiryListView,FaqCreateView,CustomerServiceView,FaqDetailView,FaqListView,AdminInquiryListView,NoticeCreateView,NoticeListView,NoticeDetailView #,InquiryListView.

app_name='customer_service'

urlpatterns = [
    path('inquiry/create/', InquiryCreateView.as_view(), name='inquiry_create'),
    # path('',InquiryListView.as_view(),name='customer_service'),
    path('inquiry/<uuid:pk>/', InquiryDetailView.as_view(), name='post_detail'),
    path('inquiry/my_inuiqry_list',MyInquiryListView.as_view(),name = 'my_inquiry_list'),
    path('faq/create',FaqCreateView.as_view(),name = 'faq_create'),
    path('',CustomerServiceView.as_view(),name = 'customer_service'),
    path('faq/detail/<int:pk>',FaqDetailView.as_view(),name ='faq_detail'),
    path('faq/faq_list',FaqListView.as_view(),name ='faq_list'),
    path('inquiry/admin_inquiry_list',AdminInquiryListView.as_view(),name ='admin_inquiry_list'),
    path('notice/create',NoticeCreateView.as_view(),name = 'notice_create'),
    path('notice/list',NoticeListView.as_view(),name = 'notice_list'),
    path('notice/detail/<int:pk>', NoticeDetailView.as_view(), name='notice_detail'),






    

]

