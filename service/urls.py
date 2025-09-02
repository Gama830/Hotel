from django.urls import path
from . import views

urlpatterns = [
    # Service URLs
    path('', views.service_list, name='service-list'),
    path('create/', views.service_create, name='service-create'),
    path('bill/', views.service_bill, name='service-bill-generic'),
    path('<int:service_id>/bill/', views.service_bill, name='service-bill'),
    path('<int:service_id>/', views.service_detail, name='service-detail'),
    path('<int:service_id>/edit/', views.service_update, name='service-update'),
    path('<int:service_id>/delete/', views.service_delete, name='service-delete'),
    
    # AJAX endpoints
    path('get-room-guest-info/<int:room_id>/', views.get_room_guest_info, name='get-room-guest-info'),
]