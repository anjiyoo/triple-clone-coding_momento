from django.contrib import admin
from .models import *

admin.site.register(InquiryCategory)
admin.site.register(Inquiry)
admin.site.register(InquiryImage)
admin.site.register(InquiryComment)
admin.site.register(Notice)
admin.site.register(FaqCategory)
admin.site.register(Faq)
