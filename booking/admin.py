from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'guest', 'room', 'check_in_date', 'check_out_date',
        'duration_nights', 'total_guests', 'status', 'total_amount', 'created_at'
    ]
    list_filter = [
        'status', 'check_in_date', 'check_out_date', 'created_at',
        'room__room_type', 'number_of_adults', 'number_of_children'
    ]
    search_fields = [
        'guest__first_name', 'guest__last_name', 'guest__email',
        'room__room_number', 'id'
    ]
    readonly_fields = ['id', 'duration_nights', 'total_guests', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('id', 'guest', 'room', 'status')
        }),
        ('Stay Details', {
            'fields': ('check_in_date', 'check_out_date', 'duration_nights')
        }),
        ('Guest Information', {
            'fields': ('number_of_adults', 'number_of_children', 'total_guests')
        }),
        ('Financial Information', {
            'fields': ('total_amount',)
        }),
        ('Additional Information', {
            'fields': ('special_requests',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-created_at']
    date_hierarchy = 'check_in_date'
    
    def duration_nights(self, obj):
        return obj.duration_nights
    duration_nights.short_description = 'Nights'
    
    def total_guests(self, obj):
        return obj.total_guests
    total_guests.short_description = 'Total Guests'
    
    actions = ['mark_as_confirmed', 'mark_as_checked_in', 'mark_as_checked_out', 'mark_as_canceled']
    
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='CONFIRMED')
        self.message_user(request, f'{updated} bookings marked as confirmed.')
    mark_as_confirmed.short_description = 'Mark selected bookings as confirmed'
    
    def mark_as_checked_in(self, request, queryset):
        updated = queryset.update(status='CHECKED_IN')
        self.message_user(request, f'{updated} bookings marked as checked in.')
    mark_as_checked_in.short_description = 'Mark selected bookings as checked in'
    
    def mark_as_checked_out(self, request, queryset):
        updated = queryset.update(status='CHECKED_OUT')
        self.message_user(request, f'{updated} bookings marked as checked out.')
    mark_as_checked_out.short_description = 'Mark selected bookings as checked out'
    
    def mark_as_canceled(self, request, queryset):
        updated = queryset.update(status='CANCELED')
        self.message_user(request, f'{updated} bookings marked as canceled.')
    mark_as_canceled.short_description = 'Mark selected bookings as canceled'