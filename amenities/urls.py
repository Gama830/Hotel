from django.urls import path
from . import views

urlpatterns = [
    path('', views.AmenityListView.as_view(), name='amenity-list'),
    path('create/', views.AmenityCreateView.as_view(), name='amenity-create'),
    path('<int:pk>/edit/', views.AmenityUpdateView.as_view(), name='amenity-edit'),
    path('<int:pk>/delete/', views.AmenityDeleteView.as_view(), name='amenity-delete'),
]