from django.contrib import admin
from .models import CheckIn


@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = [
        'check_in_id', 'guest', 'room_number', 'actual_check_in_date_time',
        'payment_status', 'id_proof_verified', 'assigned_staff'
    ]
    
    list_filter = [
        'payment_status', 'id_proof_verified', 'actual_check_in_date_time',
        'created_at'
    ]
    
    search_fields = [
        'check_in_id', 'guest__first_name', 'guest__last_name',
        'room_number__room_number', 'assigned_staff'
    ]
    
    readonly_fields = ['check_in_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Check-In Information', {
            'fields': (
                'check_in_id', 'booking', 'guest', 'actual_check_in_date_time',
                'room_number', 'number_of_guests'
            )
        }),
        ('Verification & Payment', {
            'fields': (
                'id_proof_verified', 'payment_status', 'advance_payment',
                'total_amount', 'assigned_staff'
            )
        }),
        ('Additional Information', {
            'fields': (
                'expected_check_out_date', 'remarks_notes'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'actual_check_in_date_time'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'guest', 'room_number', 'booking'
        )