from django.contrib import admin
from .models import BaenangtalkSubject, BaenangtalkPeriod, Baenangtalk, BaenangtalkComment

admin.site.register(BaenangtalkSubject)
admin.site.register(BaenangtalkPeriod)
admin.site.register(Baenangtalk)
admin.site.register(BaenangtalkComment)
