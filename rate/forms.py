from django import forms
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from .models import RatePlan
from rooms.models import RoomType

class RatePlanForm(forms.ModelForm):
    class Meta:
        model = RatePlan
        fields = [
            'rate_name', 'room_type', 'season_type', 'valid_from', 'valid_to',
            'base_rate', 'additional_guest_charges', 'meal_plan', 'meal_plan_cost',
            'cancellation_policy', 'description', 'weekend_surcharge', 
            'is_percentage_surcharge', 'is_active', 'minimum_stay', 'maximum_stay',
            'advance_booking_days'
        ]
        
        widgets = {
            'rate_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter rate plan name (e.g., Summer Special)'
            }),
            'room_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'season_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'valid_from': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': date.today().isoformat()
            }),
            'valid_to': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': (date.today() + timedelta(days=1)).isoformat()
            }),
            'base_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'additional_guest_charges': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.00',
                'placeholder': '0.00'
            }),
            'meal_plan': forms.Select(attrs={
                'class': 'form-control'
            }),
            'meal_plan_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.00',
                'placeholder': '0.00'
            }),
            'cancellation_policy': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter cancellation policy details...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional terms and conditions (optional)'
            }),
            'weekend_surcharge': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.00',
                'placeholder': '0.00'
            }),
            'is_percentage_surcharge': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'minimum_stay': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '1'
            }),
            'maximum_stay': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Optional'
            }),
            'advance_booking_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'value': '0'
            }),
        }
        
        labels = {
            'rate_name': 'Rate Plan Name',
            'room_type': 'Room Type',
            'season_type': 'Season Type',
            'valid_from': 'Valid From Date',
            'valid_to': 'Valid To Date',
            'base_rate': 'Base Rate per Night (₹)',
            'additional_guest_charges': 'Additional Guest Charges (₹)',
            'meal_plan': 'Meal Plan',
            'meal_plan_cost': 'Meal Plan Cost per Person per Day (₹)',
            'cancellation_policy': 'Cancellation Policy',
            'description': 'Description & Terms',
            'weekend_surcharge': 'Weekend Surcharge',
            'is_percentage_surcharge': 'Surcharge is Percentage',
            'is_active': 'Active',
            'minimum_stay': 'Minimum Stay (nights)',
            'maximum_stay': 'Maximum Stay (nights)',
            'advance_booking_days': 'Advance Booking Required (days)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set room type queryset
        self.fields['room_type'].queryset = RoomType.objects.all().order_by('name')
        
        # Set help texts
        self.fields['weekend_surcharge'].help_text = 'Enter amount or percentage based on checkbox below'
        self.fields['is_percentage_surcharge'].help_text = 'Check if weekend surcharge is a percentage, uncheck for fixed amount'
        self.fields['meal_plan_cost'].help_text = 'Only applicable if meal plan is not EP (Room Only)'
        self.fields['advance_booking_days'].help_text = '0 means no advance booking required'
    
    def clean(self):
        cleaned_data = super().clean()
        valid_from = cleaned_data.get('valid_from')
        valid_to = cleaned_data.get('valid_to')
        minimum_stay = cleaned_data.get('minimum_stay')
        maximum_stay = cleaned_data.get('maximum_stay')
        meal_plan = cleaned_data.get('meal_plan')
        meal_plan_cost = cleaned_data.get('meal_plan_cost')
        room_type = cleaned_data.get('room_type')
        rate_name = cleaned_data.get('rate_name')
        
        # Validate dates
        if valid_from and valid_to:
            if valid_to <= valid_from:
                raise ValidationError('Valid to date must be after valid from date.')
            
            if valid_from < date.today():
                raise ValidationError('Valid from date cannot be in the past.')
        
        # Validate stay duration
        if minimum_stay and maximum_stay:
            if maximum_stay < minimum_stay:
                raise ValidationError('Maximum stay must be greater than or equal to minimum stay.')
        
        # Validate meal plan cost
        if meal_plan and meal_plan == 'EP' and meal_plan_cost and meal_plan_cost > 0:
            raise ValidationError('Meal plan cost should be 0 for European Plan (Room Only).')
        
        # Check for overlapping rate plans
        if valid_from and valid_to and room_type and rate_name:
            overlapping_rates = RatePlan.objects.filter(
                room_type=room_type,
                valid_from__lt=valid_to,
                valid_to__gt=valid_from
            )
            
            # Exclude current instance if editing
            if self.instance.pk:
                overlapping_rates = overlapping_rates.exclude(pk=self.instance.pk)
            
            if overlapping_rates.exists():
                overlapping_rate = overlapping_rates.first()
                raise ValidationError(
                    f'Date range overlaps with existing rate plan: "{overlapping_rate.rate_name}" '
                    f'({overlapping_rate.validity_period})'
                )
        
        return cleaned_data

class RatePlanSearchForm(forms.Form):
    """Form for searching rate plans"""
    room_type = forms.ModelChoiceField(
        queryset=RoomType.objects.all(),
        required=False,
        empty_label="All Room Types",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    season_type = forms.ChoiceField(
        choices=[('', 'All Seasons')] + RatePlan.SEASON_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    meal_plan = forms.ChoiceField(
        choices=[('', 'All Meal Plans')] + RatePlan.MEAL_PLAN_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    is_active = forms.ChoiceField(
        choices=[('', 'All'), ('true', 'Active Only'), ('false', 'Inactive Only')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        help_text="Show rates valid from this date"
    )

class RateCalculatorForm(forms.Form):
    """Form for calculating rates"""
    room_type = forms.ModelChoiceField(
        queryset=RoomType.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    check_in_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': date.today().isoformat()
        })
    )
    
    check_out_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': (date.today() + timedelta(days=1)).isoformat()
        })
    )
    
    number_of_guests = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1'
        })
    )
    
    include_meals = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text="Include meal plan costs in calculation"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        check_in_date = cleaned_data.get('check_in_date')
        check_out_date = cleaned_data.get('check_out_date')
        
        if check_in_date and check_out_date:
            if check_out_date <= check_in_date:
                raise ValidationError('Check-out date must be after check-in date.')
            
            if check_in_date < date.today():
                raise ValidationError('Check-in date cannot be in the past.')
        
        return cleaned_data