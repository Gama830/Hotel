from django.urls import path
from . import views

urlpatterns = [
    # Check-in URLs
    path('', views.checkin_dashboard, name='checkin-dashboard'),
    path('list/', views.checkin_list, name='checkin-list'),
    path('create/', views.checkin_create, name='checkin-create'),
    path('quick/', views.quick_checkin, name='quick-checkin'),
    path('from-booking/<int:booking_id>/', views.checkin_from_booking, name='checkin-from-booking'),
    path('<int:checkin_id>/', views.checkin_detail, name='checkin-detail'),
    path('<int:checkin_id>/edit/', views.checkin_update, name='checkin-update'),
    path('<int:checkin_id>/verify-id/', views.verify_id_proof, name='checkin-verify-id'),
    path('<int:checkin_id>/update-payment/', views.update_payment_status, name='checkin-update-payment'),
]