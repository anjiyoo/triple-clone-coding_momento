from django import forms 
from django.db import models

from .models import diary,DiaryComment

class DiaryForm(forms.ModelForm):
    class Meta :
        model = diary
        fields = ['title','content','image']

    widgets = {
            "title": forms.Textarea(attrs={"class": "form-control mt-2", "rows": 10}),
            'content': forms.Textarea(attrs={"class": "textarea","id":"diary-title"}),
            'image': forms.ClearableFileInput(attrs={"class":"image-form"})
        }

# 댓글 작성
class CommentcreateForm(forms.ModelForm):
    class Meta:
        model = DiaryComment
        fields = ['diary_com_content']

# 댓글 수정
class CommentEditForm(forms.ModelForm):
    class Meta:
        model = DiaryComment
        fields = ['diary_com_content']
        labels = {
            'bae_com_content': '',  # 레이블을 빈 문자열로 설정
        }

# 댓글 삭제
class CommentDeleteForm(forms.ModelForm):
    class Meta:
        model = DiaryComment
        fields = []