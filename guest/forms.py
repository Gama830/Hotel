from django import forms
from .models import Guest

class GuestForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender',
            'address', 'contact_number', 'email', 'nationality',
            'id_proof_type', 'id_proof_number', 'loyalty_level',
            'member_id', 'preferences_notes'
        ]
        
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter last name'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter complete address'
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+91XXXXXXXXXX'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'nationality': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter nationality'
            }),
            'id_proof_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'id_proof_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter ID proof number'
            }),
            'loyalty_level': forms.Select(attrs={
                'class': 'form-control'
            }),
            'member_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Auto-generated for non-bronze members',
                'readonly': True
            }),
            'preferences_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter guest preferences or special notes'
            }),
        }
        
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'date_of_birth': 'Date of Birth',
            'gender': 'Gender',
            'address': 'Address',
            'contact_number': 'Contact Number',
            'email': 'Email',
            'nationality': 'Nationality',
            'id_proof_type': 'ID Proof Type',
            'id_proof_number': 'ID Proof Number',
            'loyalty_level': 'Loyalty Level',
            'member_id': 'Member ID',
            'preferences_notes': 'Preferences/Notes',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make member_id readonly if it's already set
        if self.instance and self.instance.member_id:
            self.fields['member_id'].widget.attrs['readonly'] = True