from django.contrib import admin
from .models import Amenity

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'quantity_limit']
    search_fields = ['name', 'description']
    filter_horizontal = ['applicable_room_types']
    ordering = ['name']