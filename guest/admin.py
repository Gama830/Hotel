from django.contrib import admin
from .models import Guest

@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = [
        'guest_id', 'first_name', 'last_name', 'email', 
        'contact_number', 'loyalty_level', 'created_at'
    ]
    list_filter = ['gender', 'loyalty_level', 'nationality', 'created_at']
    search_fields = [
        'first_name', 'last_name', 'email', 'contact_number', 
        'member_id', 'id_proof_number'
    ]
    readonly_fields = ['guest_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('guest_id', 'first_name', 'last_name', 'date_of_birth', 'gender')
        }),
        ('Contact Information', {
            'fields': ('address', 'contact_number', 'email', 'nationality')
        }),
        ('Identification', {
            'fields': ('id_proof_type', 'id_proof_number')
        }),
        ('Loyalty Program', {
            'fields': ('loyalty_level', 'member_id')
        }),
        ('Additional Information', {
            'fields': ('preferences_notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-created_at']