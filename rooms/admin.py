from django.contrib import admin
from .models import Room, RoomType, AssetType, Asset

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'floor', 'tariff', 'single_bed', 'double_bed', 'extra_bed', 'allow_pax', 'status']
    list_filter = ['floor', 'status', 'single_bed', 'double_bed', 'extra_bed']
    search_fields = ['room_number']
    ordering = ['room_number']

@admin.register(AssetType)
class AssetTypeAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['asset_id', 'name', 'asset_type']
    list_filter = ['asset_type']
    search_fields = ['asset_id', 'name']

admin.site.register(RoomType)