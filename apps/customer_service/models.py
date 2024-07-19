from django.db import models
from apps.userinfo.models import User
from django.utils.timesince import timesince
import uuid

class InquiryCategory(models.Model):
    name = models.CharField(max_length=255)  # max_length 추가

    def __str__(self):
        return self.name


class Inquiry(models.Model):
    inquiries_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)  
    category = models.ForeignKey(InquiryCategory, on_delete=models.CASCADE)  
    email = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)  
    inquiry_title = models.CharField(max_length=50)
    inquiry_body = models.TextField()  
    created_at = models.DateTimeField(auto_now_add=True)
    answer_status = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created_at',)

    def created_at_formatted(self):
        return timesince(self.created_at)


class InquiryImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE)  
    image = models.ImageField(upload_to='inquiry_images/img')

    def __str__(self):
        return f"Inquiry {self.inquiry.inquiries_id} Image"


class InquiryComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    body = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    post = models.ForeignKey(Inquiry, related_name='comments', on_delete=models.CASCADE)

    class Meta:
        ordering = ('-created_at',)

    def created_at_formatted(self):
        return timesince(self.created_at)


class Notice(models.Model):
    notice_title = models.CharField(max_length=255)  
    notice = models.TextField()
    created_at = models.DateField(auto_now_add=True)  

    class Meta:
        ordering = ('-created_at',)

    def created_at_formatted(self):
        return timesince(self.created_at)


class FaqCategory(models.Model):
    name = models.CharField(max_length=255)  
    def __str__(self):
        return self.name


class Faq(models.Model):
    faq_title = models.CharField(max_length=255)  
    faq_answer = models.TextField()
    faq_category = models.ForeignKey(FaqCategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.faq_title