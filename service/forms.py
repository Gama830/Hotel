from django import forms
from .models import Service, ServiceCharge
from booking.models import Booking
from guest.models import Guest
from rooms.models import Room


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = [
            'service_id', 'service_name', 'description', 
            'availability', 'available_from', 'available_to', 
            'available_days', 'requires_booking', 'max_capacity', 'is_active'
        ]
        
        widgets = {
            'service_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Auto-generated if left blank'
            }),
            'service_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Spa, Laundry, Room Service'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Detailed description of the service...'
            }),

            'availability': forms.Select(attrs={
                'class': 'form-control'
            }),
            'available_from': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'available_to': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'available_days': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Monday, Wednesday, Friday'
            }),
            'requires_booking': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'max_capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Maximum capacity (optional)'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        
        labels = {
            'service_id': 'Service ID',
            'service_name': 'Service Name',
            'description': 'Description',

            'availability': 'Availability',
            'available_from': 'Available From',
            'available_to': 'Available To',
            'available_days': 'Available Days',
            'requires_booking': 'Requires Advance Booking',
            'max_capacity': 'Maximum Capacity',
            'is_active': 'Active',
        }
        
        help_texts = {
            'service_id': 'Unique identifier for the service (auto-generated if blank)',
            'service_name': 'Name of the service (e.g., Spa, Laundry, Room Service)',
            'description': 'Detailed description of what this service includes',

            'availability': 'When is this service available?',
            'available_from': 'Start time (for custom hours)',
            'available_to': 'End time (for custom hours)',
            'available_days': 'Specific days when service is available (for custom schedule)',
            'requires_booking': 'Check if customers need to book this service in advance',
            'max_capacity': 'Maximum number of customers that can use this service simultaneously',
            'is_active': 'Uncheck to temporarily disable this service',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make service_id optional for creation
        if not self.instance.pk:
            self.fields['service_id'].required = False


class ServiceSearchForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search services by name, ID, or description...'
        })
    )


class ServiceChargeForm(forms.ModelForm):
    # Add room selection field
    room_number = forms.ModelChoiceField(
        queryset=None,
        empty_label="Select Room Number",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_room_number'
        }),
        label='Room Number',
        help_text='Select the room for which this service is being billed'
    )
    
    class Meta:
        model = ServiceCharge
        fields = [
            'service', 'room_number', 'guest', 'booking', 'quantity', 'unit_price', 'tax_rate', 'notes'
        ]

        widgets = {
            'service': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_service'
            }),
            'guest': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_guest',
                'readonly': True
            }),
            'booking': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_booking'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': '1',
                'value': '1'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01', 
                'min': '0'
            }),
            'tax_rate': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01', 
                'min': '0', 
                'max': '100',
                'value': '18.00'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3
            }),
        }

        labels = {
            'service': 'Service',
            'guest': 'Guest (Auto-filled)',
            'booking': 'Booking (Auto-filled)',
            'quantity': 'Quantity',
            'unit_price': 'Unit Price (₹)',
            'tax_rate': 'Tax Rate %',
            'notes': 'Notes',
        }

    def __init__(self, *args, **kwargs):
        service_instance = kwargs.pop('service_instance', None)
        super().__init__(*args, **kwargs)
        
        # Set room queryset to occupied rooms only
        from rooms.models import Room
        self.fields['room_number'].queryset = Room.objects.filter(
            status='OCCUPIED'
        ).order_by('room_number')
        
        # Prefill service and pricing if provided
        if service_instance and not self.instance.pk:
            self.fields['service'].initial = service_instance.pk
            self.fields['unit_price'].initial = service_instance.rate_cost if service_instance.rate_cost > 0 else 0
            self.fields['tax_rate'].initial = 18.00 if service_instance.tax_applicable else 0.00

        # Limit bookings dropdown to active/checked-in ones
        self.fields['booking'].queryset = Booking.objects.filter(
            status='CHECKED_IN'
        ).order_by('-created_at')
        
        # Make guest field readonly initially
        self.fields['guest'].widget.attrs['disabled'] = True
        self.fields['booking'].widget.attrs['disabled'] = True
        
        # Set help texts
        self.fields['service'].help_text = 'Select the service to bill'
        self.fields['room_number'].help_text = 'Select occupied room - guest info will auto-populate'
        self.fields['guest'].help_text = 'Guest information will be filled automatically when room is selected'
        self.fields['booking'].help_text = 'Associated booking will be filled automatically if available'
    
    availability = forms.ChoiceField(
        choices=[('', 'All Availabilities')] + Service.AVAILABILITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    tax_applicable = forms.ChoiceField(
        choices=[
            ('', 'All Services'),
            ('true', 'Tax Applicable'),
            ('false', 'No Tax'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    is_active = forms.ChoiceField(
        choices=[
            ('', 'All Services'),
            ('true', 'Active Only'),
            ('false', 'Inactive Only'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )