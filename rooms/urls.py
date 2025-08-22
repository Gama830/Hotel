from django.urls import path
from . import views

urlpatterns = [
    # Room URLs
    path('create/', views.RoomCreateView.as_view(), name='room-create'),
    path('<int:pk>/edit/', views.RoomUpdateView.as_view(), name='room-edit'),
    path('<int:pk>/delete/', views.RoomDeleteView.as_view(), name='room-delete'),
    path('', views.RoomListView.as_view(), name='room-list'),
    
    # Room Type URLs
    path('room-types/', views.RoomTypeListView.as_view(), name='roomtype-list'),
    path('room-types/create/', views.RoomTypeCreateView.as_view(), name='roomtype-create'),
    path('room-types/<int:pk>/edit/', views.RoomTypeUpdateView.as_view(), name='roomtype-edit'),
    path('room-types/<int:pk>/delete/', views.RoomTypeDeleteView.as_view(), name='roomtype-delete'),
    
    # API URLs
    path('api/room-type/<int:room_type_id>/', views.get_room_type_details, name='room-type-details'),
]