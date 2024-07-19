from .models import Inquiry
from django.views.generic import ListView

class InquiryListView(ListView):
    template_name = 'customer_service/customer_service.html'
    context_object_name = 'inquirys'
    model = Inquiry

    def get_queryset(self):
        return Inquiry.objects.all()

    def get_context_data(self, kwargs):
        context = super().get_context_data(kwargs)
        return context