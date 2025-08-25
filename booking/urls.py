from django.urls import path
from . import views

urlpatterns = [
    path('', views.booking_list, name='booking-list'),
    path('create/', views.booking_create, name='booking-create'),
    path('search/', views.room_availability_search, name='room-availability-search'),
    path('<int:booking_id>/', views.booking_detail, name='booking-detail'),
    path('<int:booking_id>/edit/', views.booking_update, name='booking-update'),
    path('<int:booking_id>/delete/', views.booking_delete, name='booking-delete'),
    path('<int:booking_id>/check-in/', views.booking_check_in, name='booking-check-in'),
    path('<int:booking_id>/check-out/', views.booking_check_out, name='booking-check-out'),
    path('<int:booking_id>/cancel/', views.booking_cancel, name='booking-cancel'),
]