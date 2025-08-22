from django import forms
from .models import Amenity

class AmenityForm(forms.ModelForm):
    class Meta:
        model = Amenity
        fields = ['name', 'description', 'applicable_room_types', 'quantity_limit']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter amenity name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter description (optional)'
            }),
            'applicable_room_types': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'quantity_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter quantity limit (optional)',
                'min': '1'
            })
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].help_text = 'Unique name for the amenity'
        self.fields['description'].help_text = 'Optional description of the amenity'
        self.fields['applicable_room_types'].help_text = 'Select room types where this amenity is available'
        self.fields['quantity_limit'].help_text = 'Maximum quantity available (leave blank if unlimited)'