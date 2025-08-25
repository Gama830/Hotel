from django.urls import path
from . import views

urlpatterns = [
    path('', views.guest_list, name='guest-list'),
    path('create/', views.guest_create, name='guest-create'),
    path('<int:guest_id>/', views.guest_detail, name='guest-detail'),
    path('<int:guest_id>/edit/', views.guest_update, name='guest-update'),
    path('<int:guest_id>/delete/', views.guest_delete, name='guest-delete'),
]