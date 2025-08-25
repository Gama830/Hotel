from django.urls import path
from . import views

urlpatterns = [
    path('', views.rate_plan_list, name='rate-plan-list'),
    path('create/', views.rate_plan_create, name='rate-plan-create'),
    path('calculator/', views.rate_calculator, name='rate-calculator'),
    path('current/', views.current_rates, name='current-rates'),
    path('<int:rate_plan_id>/', views.rate_plan_detail, name='rate-plan-detail'),
    path('<int:rate_plan_id>/edit/', views.rate_plan_update, name='rate-plan-update'),
    path('<int:rate_plan_id>/delete/', views.rate_plan_delete, name='rate-plan-delete'),
    path('<int:rate_plan_id>/toggle-status/', views.rate_plan_toggle_status, name='rate-plan-toggle-status'),
]