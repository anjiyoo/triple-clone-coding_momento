from django.urls import path
from . import views
app_name= 'plan'
urlpatterns = [
    path('city/',views.CityList.as_view(),name='city'),
    path('days/',views.days,name='days'),
    path('day_plan/<int:region>/<int:cigungu1>/<int:cigungu2>/<int:cigungu3>/',views.day_plan,name='day_plan'),
    path('add_plan/',views.add_plan,name='add_plan'),
    path('add_memo/',views.add_memo,name='add_memo'),
    path('plan/',views.plan,name='plan'),
    path('del_plan/',views.del_plan,name='del_plan'),
    path('plan_list/',views.PlanList.as_view(),name='plan_list'),
    path('trip_delete/<int:pk>/',views.TripDelete.as_view(),name='trip_delete')

]