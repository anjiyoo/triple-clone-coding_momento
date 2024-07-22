from django import forms
from .models import Inquiry, InquiryImage,InquiryComment,Faq,Notice

class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ['category', 'email', 'phone_number', 'inquiry_title', 'inquiry_body']
        labels = {
            'category': '카테고리',
            'email': '이메일',
            'phone_number': '전화번호',
            'inquiry_title': '제목',
            'inquiry_body': '내용'
        }

class InquiryImageForm(forms.ModelForm):
    class Meta:
        model = InquiryImage
        fields = ['image']
        labels = {
            'image': '이미지'
        }


class CommentcreateForm(forms.ModelForm):
    class Meta:
        model = InquiryComment
        fields = ['body']


class FaqcreateForm(forms.ModelForm):
    class Meta:
        model = Faq
        fields = ["faq_title",'faq_answer','faq_category']
        labels = {
            "faq_title" : 'FAQ제목',
            "faq_answer": 'FAQ내용',
            "faq_category":"카테고리"
        }

class SearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100,required=False)


class NoticecreateForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ["notice_title",'notice']
        labels = {
            "notice_title" : '공지제목',
            "notice": '공지내용',
        }