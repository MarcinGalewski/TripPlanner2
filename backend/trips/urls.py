from django.urls import path
from . import views

urlpatterns = [
    path('ready-plans/', views.ready_plans, name='ready_plans'),
    path('send-ready-plan/<int:plan_id>/', views.send_ready_plan, name='send_ready_plan'),
    path('individual-plan/', views.individual_plan, name='individual_plan'),
]
