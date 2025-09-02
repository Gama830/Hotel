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
            'number_of_adults', 'number_of_children', 'booking_source', 'reservation_source',
            'status', 'total_amount', 'advance_payment', 'payment_status', 'payment_method',
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
            'reservation_source': forms.TextInput(attrs={
                'class': 'form-control reservation-source-search',
                'placeholder': 'Type to search reservation sources...',
                'autocomplete': 'off'
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
            'reservation_source': 'Reservation Source',
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
        
        # Set reservation source help text for search field
        self.fields['reservation_source'].help_text = 'Type to search and select the specific travel agent, OTA, or source for this booking'
        
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
        
        # Handle reservation source from search input
        reservation_source_text = cleaned_data.get('reservation_source')
        if reservation_source_text and hasattr(self, 'data'):
            reservation_source_id = self.data.get('reservation_source_id')
            if reservation_source_id:
                try:
                    from .models import ReservationSource
                    reservation_source = ReservationSource.objects.get(id=reservation_source_id, is_active=True)
                    cleaned_data['reservation_source'] = reservation_source
                except ReservationSource.DoesNotExist:
                    cleaned_data['reservation_source'] = None
        
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
from .models import ReservationSource, CorporateAgent

class ReservationSourceForm(forms.ModelForm):
    class Meta:
        model = ReservationSource
        fields = [
            'source_id', 'name', 'source_type', 'contact_person', 'email', 'phone',
            'address', 'commission_rate', 'is_active', 'website_url', 'notes'
        ]
        
        widgets = {
            'source_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Leave blank for auto-generation'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Booking.com, Expedia, Company Website'
            }),
            'source_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact person name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contact@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+91-9876543210'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Complete address'
            }),
            'commission_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'placeholder': '0.00'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'website_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes about this source'
            }),
        }
        
        labels = {
            'source_id': 'Source ID',
            'name': 'Source Name',
            'source_type': 'Source Type',
            'contact_person': 'Contact Person',
            'email': 'Email',
            'phone': 'Phone',
            'address': 'Address',
            'commission_rate': 'Commission Rate (%)',
            'is_active': 'Active',
            'website_url': 'Website URL',
            'notes': 'Notes',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['source_id'].required = False
        self.fields['contact_person'].required = False
        self.fields['email'].required = False
        self.fields['phone'].required = False
        self.fields['address'].required = False
        self.fields['website_url'].required = False
        self.fields['notes'].required = False


class CorporateAgentForm(forms.ModelForm):
    class Meta:
        model = CorporateAgent
        fields = [
            'agent_id', 'name', 'agent_type', 'contact_person', 'designation',
            'address', 'city', 'state', 'country', 'postal_code',
            'phone', 'mobile', 'email', 'website',
            'business_registration', 'gstin', 'pan_number',
            'contracted_rate', 'commission_rate', 'credit_limit', 'payment_terms',
            'is_active', 'notes'
        ]
        
        widgets = {
            'agent_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Leave blank for auto-generation'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Corporate/Agent name'
            }),
            'agent_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Primary contact person'
            }),
            'designation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Manager, Director, etc.'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Complete address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State/Province'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'value': 'India'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Postal/ZIP code'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+91-11-12345678'
            }),
            'mobile': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+91-9876543210'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contact@company.com'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://company.com'
            }),
            'business_registration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Business registration number'
            }),
            'gstin': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '22AAAAA0000A1Z5',
                'maxlength': '15'
            }),
            'pan_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ABCDE1234F',
                'maxlength': '10'
            }),
            'contracted_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'commission_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'placeholder': '0.00'
            }),
            'credit_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'payment_terms': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes'
            }),
        }
        
        labels = {
            'agent_id': 'Corporate/Agent ID',
            'name': 'Name',
            'agent_type': 'Type',
            'contact_person': 'Contact Person',
            'designation': 'Designation',
            'address': 'Address',
            'city': 'City',
            'state': 'State',
            'country': 'Country',
            'postal_code': 'Postal Code',
            'phone': 'Phone',
            'mobile': 'Mobile',
            'email': 'Email',
            'website': 'Website',
            'business_registration': 'Business Registration',
            'gstin': 'GSTIN No.',
            'pan_number': 'PAN Number',
            'contracted_rate': 'Contracted Rate (₹)',
            'commission_rate': 'Commission Rate (%)',
            'credit_limit': 'Credit Limit (₹)',
            'payment_terms': 'Payment Terms',
            'is_active': 'Active',
            'notes': 'Notes',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['agent_id'].required = False
        self.fields['designation'].required = False
        self.fields['mobile'].required = False
        self.fields['website'].required = False
        self.fields['business_registration'].required = False
        self.fields['gstin'].required = False
        self.fields['pan_number'].required = False
        self.fields['notes'].required = False