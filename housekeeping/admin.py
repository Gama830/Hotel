from django.contrib import admin
from .models import HousekeepingStatus, HousekeepingTask, HousekeepingInspection

@admin.register(HousekeepingStatus)
class HousekeepingStatusAdmin(admin.ModelAdmin):
    list_display = ['status_id', 'status_name', 'description', 'color_code', 'is_active', 'created_at']
    list_filter = ['status_name', 'is_active', 'created_at']
    search_fields = ['status_name', 'description']
    ordering = ['status_name']
    readonly_fields = ['status_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('status_name', 'description', 'color_code', 'is_active')
        }),
        ('System Information', {
            'fields': ('status_id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(HousekeepingTask)
class HousekeepingTaskAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'room', 'task_type', 'priority', 'task_status', 
        'assigned_to', 'scheduled_date', 'scheduled_time'
    ]
    list_filter = [
        'task_status', 'priority', 'scheduled_date', 'status__status_name', 'created_at'
    ]
    search_fields = ['room__room_number', 'task_type', 'assigned_to', 'description']
    ordering = ['-scheduled_date', 'priority', 'room__room_number']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Task Information', {
            'fields': ('room', 'status', 'task_type', 'priority', 'task_status')
        }),
        ('Assignment & Scheduling', {
            'fields': ('assigned_to', 'scheduled_date', 'scheduled_time', 'estimated_duration')
        }),
        ('Details', {
            'fields': ('description', 'notes')
        }),
        ('Tracking', {
            'fields': ('actual_duration', 'started_at', 'completed_at'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('room', 'status')

@admin.register(HousekeepingInspection)
class HousekeepingInspectionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'room', 'inspector_name', 'inspection_status', 
        'cleanliness_score', 'inspection_date', 'follow_up_required'
    ]
    list_filter = [
        'inspection_status', 'follow_up_required', 'inspection_date', 'cleanliness_score'
    ]
    search_fields = ['room__room_number', 'inspector_name', 'issues_found']
    ordering = ['-inspection_date']
    readonly_fields = ['inspection_date', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Inspection Information', {
            'fields': ('room', 'task', 'inspector_name', 'inspection_status', 'cleanliness_score')
        }),
        ('Findings', {
            'fields': ('issues_found', 'corrective_actions', 'inspection_notes')
        }),
        ('Follow-up', {
            'fields': ('follow_up_required', 'follow_up_date')
        }),
        ('System Information', {
            'fields': ('inspection_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('room', 'task')