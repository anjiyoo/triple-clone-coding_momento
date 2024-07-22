from django.shortcuts import render
from .models import *
from django.views.generic import *

# main(city)
class SelectCityListView(View):
    template_name = 'select_city.html'

    def get(self, request, *args, **kwargs):
        context = {
            'counties': County.objects.all()
            }
        return render(request, self.template_name, context)
    
# date
class SelectDateListView(View):
    template_name = 'select_date.html'

    def get(self, request, *args, **kwargs):
        selected_city = request.GET.get('city')  # URL 쿼리 파라미터에서 도시를 추출
        
        context = {
            'selected_city': selected_city,  # 선택된 도시
            'counties': County.objects.all(),
            'dates': TripDate.objects.all()
        }
        return render(request, self.template_name, context)
    
# who
class SelectWhoListView(View):
    template_name = 'select_who.html'

    def get(self, request, *args, **kwargs):
        context = {
            'counties': County.objects.all(),
            'dates': TripDate.objects.all(),
            'whose': TripWho.objects.all() 
        } 
        return render(request, self.template_name, context)

# style
class SelectStyleListView(View):
    template_name = 'select_style.html'

    def get(self, request, *args, **kwargs):
        context = {
            'counties': County.objects.all(),
            'dates': TripDate.objects.all(),
            'whose': TripWho.objects.all(),
            'styles': TripStyle.objects.all() 
        } 
        return render(request, self.template_name, context)
    
# plan
class SelectPlanListView(View):
    template_name = 'select_plan.html'

    def get(self, request, *args, **kwargs):
        context = {
            'counties': County.objects.all(),
            'dates': TripDate.objects.all(),
            'whose': TripWho.objects.all(),
            'styles': TripStyle.objects.all(), 
            'plans': TripPlan.objects.all() 
        } 
        return render(request, self.template_name, context)
