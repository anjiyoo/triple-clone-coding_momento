from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def guidemain(request):
    return render(request, 'guidepage/guidemain.html')

def guide_plan(request):
    return render(request, 'guidepage/travel_plan.html')

def guide_info(request):
    return render(request, 'guidepage/custom_info.html')

def guide_reservation(request):
    return render(request, 'guidepage/all_reservation.html')

def guide_memory(request):
    return render(request, 'guidepage/travel_memory.html')
