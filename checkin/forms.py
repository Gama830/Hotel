from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta, datetime
from .models import CheckIn
from booking.models import Booking
from guest.models import Guest
from rooms.models import Room


class DateTime12HourWidget(forms.DateTimeInput):
    """Custom widget for 12-hour datetime input with Indian timezone"""
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-control',
            'type': 'datetime-local',
            'step': '60'  # 1 minute steps
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)
    
    def format_value(self, value):
        if value is None:
            return ''
        
        # Convert to Indian timezone if it's timezone-aware
        if timezone.is_aware(value):
            indian_tz = timezone.get_current_timezone()
            value = value.astimezone(indian_tz)
        
        # Format for datetime-local input (24-hour format for HTML input)
        return value.strftime('%Y-%m-%dT%H:%M')
    
    def value_from_datadict(self, data, files, name):
        value = super().value_from_datadict(data, files, name)
        if value:
            try:
                # Parse the datetime-local format
                dt = datetime.strptime(value, '%Y-%m-%dT%H:%M')
                # Make it timezone-aware with Indian timezone
                indian_tz = timezone.get_current_timezone()
                # Use replace() method for zoneinfo.ZoneInfo objects
                return dt.replace(tzinfo=indian_tz)
            except ValueError:
                return None
        return None


class CheckInForm(forms.ModelForm):
    class Meta:
        model = CheckIn
        fields = [
            'check_in_id', 'booking', 'guest', 'actual_check_in_date_time',
            'room_number', 'id_proof_verified', 'payment_status',
            'assigned_staff', 'expected_check_out_date', 'number_of_guests',
            'advance_payment', 'total_amount', 'remarks_notes'
        ]
        
        widgets = {
            'check_in_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Auto-generated if left blank'
            }),
            'booking': forms.Select(attrs={
                'class': 'form-control'
            }),
            'guest': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'actual_check_in_date_time': DateTime12HourWidget(),
            'room_number': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'id_proof_verified': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'payment_status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'assigned_staff': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Staff member name'
            }),
            'expected_check_out_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'number_of_guests': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '1'
            }),
            'advance_payment': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'total_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'remarks_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes or special requests...'
            }),
        }
        
        labels = {
            'check_in_id': 'Check-In ID',
            'booking': 'Booking Reference',
            'guest': 'Primary Guest',
            'actual_check_in_date_time': 'Check-In Date & Time',
            'room_number': 'Room Number',
            'id_proof_verified': 'ID Proof Verified',
            'payment_status': 'Payment Status',
            'assigned_staff': 'Assigned Staff',
            'expected_check_out_date': 'Expected Check-Out Date',
            'number_of_guests': 'Number of Guests',
            'advance_payment': 'Advance Payment (₹)',
            'total_amount': 'Total Amount (₹)',
            'remarks_notes': 'Remarks/Notes',
        }
    
    def __init__(self, *args, **kwargs):
        booking_instance = kwargs.pop('booking_instance', None)
        super().__init__(*args, **kwargs)
        
        # Set querysets
        self.fields['guest'].queryset = Guest.objects.all().order_by('first_name', 'last_name')
        self.fields['room_number'].queryset = Room.objects.all().order_by('room_number')
        self.fields['booking'].queryset = Booking.objects.filter(
            status__in=['CONFIRMED', 'CHECKED_IN']
        ).order_by('-created_at')
        
        # Set empty labels
        self.fields['booking'].empty_label = "Select Booking (Optional for Walk-ins)"
        self.fields['guest'].empty_label = "Select Guest"
        self.fields['room_number'].empty_label = "Select Room"
        
        # Make some fields optional
        self.fields['check_in_id'].required = False
        self.fields['booking'].required = False
        self.fields['assigned_staff'].required = False
        self.fields['expected_check_out_date'].required = False
        self.fields['remarks_notes'].required = False
        
        # Set default check-in time to current Indian time
        if not self.instance.pk:
            current_time = timezone.now()
            self.fields['actual_check_in_date_time'].initial = current_time
        
        # Pre-fill from booking if provided
        if booking_instance and not self.instance.pk:
            self.fields['booking'].initial = booking_instance.pk
            self.fields['guest'].initial = booking_instance.guest.pk
            self.fields['room_number'].initial = booking_instance.room.pk
            self.fields['expected_check_out_date'].initial = booking_instance.check_out_date
            self.fields['total_amount'].initial = booking_instance.total_amount
            self.fields['number_of_guests'].initial = booking_instance.number_of_guests
    
    def clean(self):
        cleaned_data = super().clean()
        booking = cleaned_data.get('booking')
        guest = cleaned_data.get('guest')
        room_number = cleaned_data.get('room_number')
        actual_check_in_date_time = cleaned_data.get('actual_check_in_date_time')
        expected_check_out_date = cleaned_data.get('expected_check_out_date')
        advance_payment = cleaned_data.get('advance_payment', 0)
        total_amount = cleaned_data.get('total_amount', 0)
        
        # Validate that either booking or guest is provided
        if not booking and not guest:
            raise ValidationError('Either booking reference or guest must be provided.')
        
        # If booking is provided, validate guest matches
        if booking and guest and booking.guest != guest:
            raise ValidationError('Selected guest does not match the booking guest.')
        
        # Validate check-in date is not in the future (allow some flexibility)
        if actual_check_in_date_time and actual_check_in_date_time > timezone.now() + timedelta(hours=1):
            raise ValidationError('Check-in date cannot be more than 1 hour in the future.')
        
        # Validate expected check-out is after check-in
        if actual_check_in_date_time and expected_check_out_date:
            if expected_check_out_date <= actual_check_in_date_time.date():
                raise ValidationError('Expected check-out date must be after check-in date.')
        
        # Validate advance payment doesn't exceed total amount
        if advance_payment and total_amount and advance_payment > total_amount:
            raise ValidationError('Advance payment cannot exceed total amount.')
        
        # Check room availability (basic check)
        if room_number and actual_check_in_date_time:
            overlapping_checkins = CheckIn.objects.filter(
                room_number=room_number,
                actual_check_in_date_time__date=actual_check_in_date_time.date()
            )
            if self.instance.pk:
                overlapping_checkins = overlapping_checkins.exclude(pk=self.instance.pk)
            
            if overlapping_checkins.exists():
                raise ValidationError(f'Room {room_number.room_number} already has a check-in for this date.')
        
        return cleaned_data


class CheckInSearchForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by Check-In ID, Guest name, or Room number...'
        })
    )
    
    payment_status = forms.ChoiceField(
        choices=[('', 'All Payment Status')] + CheckIn.PAYMENT_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    date_range = forms.ChoiceField(
        choices=[
            ('', 'All Dates'),
            ('today', 'Today'),
            ('yesterday', 'Yesterday'),
            ('this_week', 'This Week'),
            ('this_month', 'This Month'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    id_verified = forms.ChoiceField(
        choices=[
            ('', 'All'),
            ('true', 'ID Verified'),
            ('false', 'ID Not Verified'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )


class QuickCheckInForm(forms.ModelForm):
    """Simplified form for quick walk-in check-ins"""
    
    class Meta:
        model = CheckIn
        fields = [
            'guest', 'room_number', 'number_of_guests', 
            'expected_check_out_date', 'advance_payment', 'total_amount'
        ]
        
        widgets = {
            'guest': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'room_number': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'number_of_guests': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '1'
            }),
            'expected_check_out_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': date.today().isoformat()
            }),
            'advance_payment': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'total_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set querysets for available rooms only
        self.fields['room_number'].queryset = Room.objects.filter(
            status='AVAILABLE'
        ).order_by('room_number')
        
        self.fields['guest'].queryset = Guest.objects.all().order_by('first_name', 'last_name')
        
        # Set empty labels
        self.fields['guest'].empty_label = "Select Guest"
        self.fields['room_number'].empty_label = "Select Available Room"
        
        # Set default expected check-out to tomorrow
        self.fields['expected_check_out_date'].initial = date.today() + timedelta(days=1)