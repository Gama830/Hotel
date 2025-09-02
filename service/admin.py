from django.contrib import admin
from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        'service_id', 'service_name', 'rate_cost', 'tax_applicable', 
        'availability', 'requires_booking', 'is_active', 'created_at'
    ]
    list_filter = [
        'availability', 'tax_applicable', 'requires_booking', 'is_active', 'created_at'
    ]
    search_fields = ['service_id', 'service_name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('service_id', 'service_name', 'description')
        }),
        ('Pricing', {
            'fields': ('rate_cost', 'tax_applicable')
        }),
        ('Availability', {
            'fields': ('availability', 'available_from', 'available_to', 'available_days')
        }),
        ('Configuration', {
            'fields': ('requires_booking', 'max_capacity', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)
        if obj:  # Editing existing object
            readonly_fields.append('service_id')
        return readonly_fields