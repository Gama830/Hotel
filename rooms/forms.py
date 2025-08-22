from django import forms
from .models import Room, AssetType, Asset, RoomType
from amenities.models import Amenity

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = [
            'room_number', 'room_type', 'floor', 'bed_type',
            'single_bed', 'double_bed', 'extra_bed',
            'max_occupancy', 'allow_pax', 'status', 'description',
            'view', 'amenities', 'rate_default', 'tariff'
        ]
        widgets = {
            'room_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Room ID/Number'
            }),
            'room_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'floor': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Floor Number',
                'min': '1'
            }),
            'bed_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'max_occupancy': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Max Occupancy'
            }),
            'allow_pax': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Allow Pax'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Description/Notes',
                'rows': 3
            }),
            'view': forms.Select(attrs={
                'class': 'form-control'
            }),
            'amenities': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'rate_default': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'tariff': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
        }
        labels = {
            'room_number': 'Room ID/Number',
            'room_type': 'Room Type',
            'floor': 'Floor Number',
            'bed_type': 'Bed Type',
            'single_bed': 'Single Bed',
            'double_bed': 'Double Bed',
            'extra_bed': 'Extra Bed',
            'max_occupancy': 'Max Occupancy',
            'allow_pax': 'Allow Pax',
            'status': 'Status',
            'description': 'Description/Notes',
            'view': 'View',
            'amenities': 'Features/Amenities',
            'rate_default': 'Rate (Default)',
            'tariff': 'Tariff'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add empty choice for select fields
        self.fields['room_type'].empty_label = "Select Room Type"
        self.fields['bed_type'].empty_label = "Select Bed Type"
        self.fields['view'].empty_label = "Select View"
        self.fields['status'].empty_label = "Select Status"

class RoomTypeForm(forms.ModelForm):
    class Meta:
        model = RoomType
        fields = ['name', 'description', 'price_per_night', 'capacity', 'bed_type', 'amenities']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Room Type Name (e.g., Deluxe, Suite)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter description of the room type',
                'rows': 4
            }),
            'price_per_night': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Maximum occupancy',
                'min': '1'
            }),
            'bed_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'amenities': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'name': 'Room Type Name',
            'description': 'Description',
            'price_per_night': 'Default Rate (₹)',
            'capacity': 'Max Occupancy',
            'bed_type': 'Bed Type',
            'amenities': 'Included Amenities',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bed_type'].empty_label = "Select Bed Type"