from django import forms
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from .models import Booking
from guest.models import Guest
from rooms.models import Room
from rate.models import RatePlan

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'guest', 'room', 'rate_plan', 'check_in_date', 'check_out_date',
            'number_of_adults', 'number_of_children', 'booking_source', 'status',
            'total_amount', 'advance_payment', 'payment_status', 'payment_method',
            'special_requests', 'confirmation_number', 'booking_notes'
        ]
        
        widgets = {
            'guest': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'room': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'rate_plan': forms.Select(attrs={
                'class': 'form-control'
            }),
            'check_in_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': date.today().isoformat()
            }),
            'check_out_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': (date.today() + timedelta(days=1)).isoformat()
            }),
            'number_of_adults': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '1'
            }),
            'number_of_children': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'value': '0'
            }),
            'booking_source': forms.Select(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'total_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'advance_payment': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'payment_status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'payment_method': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Cash, Card, UPI, Bank Transfer'
            }),
            'special_requests': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter any special requests or notes for this booking'
            }),
            'confirmation_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'External confirmation number (for OTA bookings)'
            }),
            'booking_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Internal booking notes'
            }),
        }
        
        labels = {
            'guest': 'Guest ID or Details',
            'room': 'Room Type and Number',
            'rate_plan': 'Rate Plan',
            'check_in_date': 'Check-in Date',
            'check_out_date': 'Check-out Date',
            'number_of_adults': 'Number of Adults',
            'number_of_children': 'Number of Children',
            'booking_source': 'Booking Source',
            'status': 'Reservation Status',
            'total_amount': 'Total Amount (₹)',
            'advance_payment': 'Advance Payment (₹)',
            'payment_status': 'Payment Status',
            'payment_method': 'Payment Method',
            'special_requests': 'Special Requests',
            'confirmation_number': 'Confirmation Number',
            'booking_notes': 'Booking Notes',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter available rooms (only show available rooms for new bookings)
        if not self.instance.pk:
            self.fields['room'].queryset = Room.objects.filter(status='AVAILABLE')
        
        # Set guest queryset with better display
        self.fields['guest'].queryset = Guest.objects.all().order_by('first_name', 'last_name')
        
        # Set rate plan queryset
        self.fields['rate_plan'].queryset = RatePlan.objects.filter(is_active=True).order_by('rate_name')
        self.fields['rate_plan'].empty_label = "Select Rate Plan (Optional)"
        
        # Make total_amount auto-calculated but allow manual override
        self.fields['total_amount'].help_text = 'Will be calculated automatically based on room price and duration'
        if not self.instance.pk:
            self.fields['total_amount'].widget.attrs['placeholder'] = 'Auto-calculated'
        
        # Set empty labels
        self.fields['guest'].empty_label = "Select Guest"
        self.fields['room'].empty_label = "Select Room"
        self.fields['booking_source'].empty_label = "Select Booking Source"
        self.fields['status'].empty_label = "Select Status"
        self.fields['payment_status'].empty_label = "Select Payment Status"
    
    def clean(self):
        cleaned_data = super().clean()
        check_in_date = cleaned_data.get('check_in_date')
        check_out_date = cleaned_data.get('check_out_date')
        room = cleaned_data.get('room')
        number_of_adults = cleaned_data.get('number_of_adults')
        number_of_children = cleaned_data.get('number_of_children')
        
        # Validate dates
        if check_in_date and check_out_date:
            if check_out_date <= check_in_date:
                raise ValidationError('Check-out date must be after check-in date.')
            
            if check_in_date < date.today():
                raise ValidationError('Check-in date cannot be in the past.')
        
        # Check room availability for the selected dates
        if check_in_date and check_out_date and room:
            overlapping_bookings = Booking.objects.filter(
                room=room,
                status__in=['CONFIRMED', 'CHECKED_IN'],
                check_in_date__lt=check_out_date,
                check_out_date__gt=check_in_date
            )
            
            # Exclude current booking if editing
            if self.instance.pk:
                overlapping_bookings = overlapping_bookings.exclude(pk=self.instance.pk)
            
            if overlapping_bookings.exists():
                raise ValidationError(
                    f'Room {room.room_number} is not available for the selected dates. '
                    f'Please choose different dates or another room.'
                )
        
        # Validate guest capacity
        if room and number_of_adults is not None and number_of_children is not None:
            total_guests = number_of_adults + number_of_children
            if hasattr(room, 'room_type') and room.room_type.capacity:
                if total_guests > room.room_type.capacity:
                    raise ValidationError(
                        f'Total guests ({total_guests}) exceeds room capacity ({room.room_type.capacity}).'
                    )
        
        return cleaned_data

class BookingSearchForm(forms.Form):
    """Form for searching available rooms"""
    check_in_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': date.today().isoformat()
        }),
        initial=date.today
    )
    check_out_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': (date.today() + timedelta(days=1)).isoformat()
        }),
        initial=date.today() + timedelta(days=1)
    )
    number_of_adults = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1'
        })
    )
    number_of_children = forms.IntegerField(
        min_value=0,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0'
        })
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

class CheckInForm(forms.Form):
    """Form for check-in process"""
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Check-in notes (optional)'
        }),
        label='Check-in Notes'
    )

class CheckOutForm(forms.Form):
    """Form for check-out process"""
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Check-out notes (optional)'
        }),
        label='Check-out Notes'
    )
    
    final_amount = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': 'Final amount (if different)'
        }),
        label='Final Amount (₹)'
    )