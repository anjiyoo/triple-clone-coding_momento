from django import forms
from .models import *

# 배낭톡 ##############################################################################

# 게시글 작성
class BaenangtalkForm(forms.ModelForm):
    class Meta:
        model = Baenangtalk
        fields = ['county', 'period', 'subject', 'bae_title', 'bae_content', 'bae_img']
        labels = {
            'county': '도시',
            'period': '여행시기',
            'subject': '주제',
            'bae_title': '제목',
            'bae_content': '내용',
            'bae_img': '이미지'
        }


# 게시글 수정
class BaenangtalkForm(forms.ModelForm):
    class Meta:
        model = Baenangtalk
        fields = ['county', 'period', 'subject', 'bae_title', 'bae_content', 'bae_img']

# 댓글 ##############################################################################

# 댓글 작성
class CommentcreateForm(forms.ModelForm):
    class Meta:
        model = BaenangtalkComment
        fields = ['bae_com_content']

# 댓글 수정
class CommentEditForm(forms.ModelForm):
    class Meta:
        model = BaenangtalkComment
        fields = ['bae_com_content']
        labels = {
            'bae_com_content': '',  # 레이블을 빈 문자열로 설정
        }

# 댓글 삭제
class CommentDeleteForm(forms.ModelForm):
    class Meta:
        model = BaenangtalkComment
        fields = []