from django.contrib import admin
from .models import RatePlan

@admin.register(RatePlan)
class RatePlanAdmin(admin.ModelAdmin):
    list_display = [
        'rate_plan_id', 'rate_name', 'room_type', 'season_type',
        'base_rate', 'meal_plan', 'validity_period', 'is_active', 'created_at'
    ]
    list_filter = [
        'season_type', 'meal_plan', 'is_active', 'room_type',
        'valid_from', 'valid_to', 'created_at'
    ]
    search_fields = [
        'rate_name', 'room_type__name', 'description', 'cancellation_policy'
    ]
    readonly_fields = ['rate_plan_id', 'validity_period', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('rate_plan_id', 'rate_name', 'room_type', 'season_type', 'is_active')
        }),
        ('Validity Period', {
            'fields': ('valid_from', 'valid_to', 'validity_period')
        }),
        ('Pricing', {
            'fields': ('base_rate', 'additional_guest_charges', 'weekend_surcharge', 'is_percentage_surcharge')
        }),
        ('Meal Plan', {
            'fields': ('meal_plan', 'meal_plan_cost')
        }),
        ('Stay Requirements', {
            'fields': ('minimum_stay', 'maximum_stay', 'advance_booking_days')
        }),
        ('Policies & Terms', {
            'fields': ('cancellation_policy', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-created_at']
    date_hierarchy = 'valid_from'
    
    def validity_period(self, obj):
        return obj.validity_period
    validity_period.short_description = 'Validity Period'
    
    actions = ['activate_rate_plans', 'deactivate_rate_plans', 'duplicate_rate_plans']
    
    def activate_rate_plans(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} rate plans activated.')
    activate_rate_plans.short_description = 'Activate selected rate plans'
    
    def deactivate_rate_plans(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} rate plans deactivated.')
    deactivate_rate_plans.short_description = 'Deactivate selected rate plans'
    
    def duplicate_rate_plans(self, request, queryset):
        """Duplicate selected rate plans for easy creation of similar rates"""
        duplicated = 0
        for rate_plan in queryset:
            rate_plan.pk = None  # This will create a new instance
            rate_plan.rate_name = f"{rate_plan.rate_name} (Copy)"
            rate_plan.is_active = False  # Make copies inactive by default
            rate_plan.save()
            duplicated += 1
        
        self.message_user(request, f'{duplicated} rate plans duplicated. Please review and activate them.')
    duplicate_rate_plans.short_description = 'Duplicate selected rate plans'