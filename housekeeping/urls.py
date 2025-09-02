from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.housekeeping_dashboard, name='housekeeping-dashboard'),
    
    # Housekeeping Status URLs
    path('statuses/', views.housekeeping_status_list, name='housekeeping-status-list'),
    path('statuses/create/', views.housekeeping_status_create, name='housekeeping-status-create'),
    path('statuses/<int:status_id>/', views.housekeeping_status_detail, name='housekeeping-status-detail'),
    path('statuses/<int:status_id>/edit/', views.housekeeping_status_update, name='housekeeping-status-update'),
    
    # Housekeeping Task URLs
    path('tasks/', views.housekeeping_task_list, name='housekeeping-task-list'),
    path('tasks/create/', views.housekeeping_task_create, name='housekeeping-task-create'),
    path('tasks/<int:task_id>/', views.housekeeping_task_detail, name='housekeeping-task-detail'),
    path('tasks/<int:task_id>/edit/', views.housekeeping_task_update, name='housekeeping-task-update'),
    path('tasks/<int:task_id>/update-status/', views.housekeeping_task_update_status, name='housekeeping-task-update-status'),
    
    # Housekeeping Inspection URLs
    path('inspections/', views.housekeeping_inspection_list, name='housekeeping-inspection-list'),
    path('inspections/create/', views.housekeeping_inspection_create, name='housekeeping-inspection-create'),
    path('inspections/<int:inspection_id>/', views.housekeeping_inspection_detail, name='housekeeping-inspection-detail'),
]