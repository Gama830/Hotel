from django import forms
from django.core.exceptions import ValidationError
from datetime import date, time
from .models import HousekeepingStatus, HousekeepingTask, HousekeepingInspection
from rooms.models import Room

class HousekeepingStatusForm(forms.ModelForm):
    class Meta:
        model = HousekeepingStatus
        fields = ['status_name', 'description', 'color_code', 'is_active']
        
        widgets = {
            'status_name': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter description of this housekeeping status'
            }),
            'color_code': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
                'title': 'Choose color for this status'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        
        labels = {
            'status_name': 'Status Name',
            'description': 'Description',
            'color_code': 'Color Code',
            'is_active': 'Active Status',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False
        
        # Set default colors for different statuses
        if not self.instance.pk:
            status_colors = {
                'CLEAN': '#28a745',
                'DIRTY': '#dc3545',
                'IN_PROGRESS': '#ffc107',
                'OUT_OF_ORDER': '#6c757d',
                'MAINTENANCE': '#fd7e14',
                'INSPECTED': '#17a2b8',
            }
            if 'status_name' in self.data:
                status = self.data['status_name']
                if status in status_colors:
                    self.fields['color_code'].initial = status_colors[status]


class HousekeepingTaskForm(forms.ModelForm):
    class Meta:
        model = HousekeepingTask
        fields = [
            'room', 'status', 'task_type', 'priority', 'task_status',
            'assigned_to', 'description', 'notes', 'estimated_duration',
            'scheduled_date', 'scheduled_time'
        ]
        
        widgets = {
            'room': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'task_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Daily Cleaning, Deep Clean, Maintenance'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control'
            }),
            'task_status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'assigned_to': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Staff member name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Detailed description of the task'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes or special instructions'
            }),
            'estimated_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '5',
                'step': '5',
                'placeholder': 'Duration in minutes'
            }),
            'scheduled_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': date.today().isoformat()
            }),
            'scheduled_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
        }
        
        labels = {
            'room': 'Room',
            'status': 'Housekeeping Status',
            'task_type': 'Task Type',
            'priority': 'Priority',
            'task_status': 'Task Status',
            'assigned_to': 'Assigned To',
            'description': 'Description',
            'notes': 'Notes',
            'estimated_duration': 'Estimated Duration (minutes)',
            'scheduled_date': 'Scheduled Date',
            'scheduled_time': 'Scheduled Time',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set querysets
        self.fields['room'].queryset = Room.objects.all().order_by('room_number')
        self.fields['status'].queryset = HousekeepingStatus.objects.filter(is_active=True).order_by('status_name')
        
        # Set empty labels
        self.fields['room'].empty_label = "Select Room"
        self.fields['status'].empty_label = "Select Status"
        
        # Make some fields optional
        self.fields['assigned_to'].required = False
        self.fields['description'].required = False
        self.fields['notes'].required = False
        self.fields['scheduled_time'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        scheduled_date = cleaned_data.get('scheduled_date')
        
        # Validate scheduled date
        if scheduled_date and scheduled_date < date.today():
            raise ValidationError('Scheduled date cannot be in the past.')
        
        return cleaned_data


class HousekeepingInspectionForm(forms.ModelForm):
    class Meta:
        model = HousekeepingInspection
        fields = [
            'room', 'task', 'inspector_name', 'inspection_status',
            'cleanliness_score', 'issues_found', 'corrective_actions',
            'inspection_notes', 'follow_up_required', 'follow_up_date'
        ]
        
        widgets = {
            'room': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'task': forms.Select(attrs={
                'class': 'form-control'
            }),
            'inspector_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Inspector name'
            }),
            'inspection_status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'cleanliness_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '10',
                'step': '1'
            }),
            'issues_found': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List any issues found during inspection'
            }),
            'corrective_actions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Actions needed to address the issues'
            }),
            'inspection_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional inspection notes'
            }),
            'follow_up_required': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'follow_up_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': date.today().isoformat()
            }),
        }
        
        labels = {
            'room': 'Room',
            'task': 'Related Task',
            'inspector_name': 'Inspector Name',
            'inspection_status': 'Inspection Result',
            'cleanliness_score': 'Cleanliness Score (1-10)',
            'issues_found': 'Issues Found',
            'corrective_actions': 'Corrective Actions',
            'inspection_notes': 'Inspection Notes',
            'follow_up_required': 'Follow-up Required',
            'follow_up_date': 'Follow-up Date',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set querysets
        self.fields['room'].queryset = Room.objects.all().order_by('room_number')
        self.fields['task'].queryset = HousekeepingTask.objects.filter(
            task_status__in=['COMPLETED', 'IN_PROGRESS']
        ).order_by('-scheduled_date')
        
        # Set empty labels
        self.fields['room'].empty_label = "Select Room"
        self.fields['task'].empty_label = "Select Related Task (Optional)"
        
        # Make some fields optional
        self.fields['task'].required = False
        self.fields['issues_found'].required = False
        self.fields['corrective_actions'].required = False
        self.fields['inspection_notes'].required = False
        self.fields['follow_up_date'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        follow_up_required = cleaned_data.get('follow_up_required')
        follow_up_date = cleaned_data.get('follow_up_date')
        inspection_status = cleaned_data.get('inspection_status')
        
        # Validate follow-up date
        if follow_up_required and not follow_up_date:
            raise ValidationError('Follow-up date is required when follow-up is needed.')
        
        if follow_up_date and follow_up_date < date.today():
            raise ValidationError('Follow-up date cannot be in the past.')
        
        # Auto-set follow-up required for failed inspections
        if inspection_status == 'FAILED' and not follow_up_required:
            cleaned_data['follow_up_required'] = True
        
        return cleaned_data


class TaskUpdateForm(forms.ModelForm):
    """Form for updating task status and adding completion details"""
    
    class Meta:
        model = HousekeepingTask
        fields = ['task_status', 'assigned_to', 'actual_duration', 'notes']
        
        widgets = {
            'task_status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'assigned_to': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Staff member name'
            }),
            'actual_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'step': '1',
                'placeholder': 'Actual time taken in minutes'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add completion notes or observations'
            }),
        }
        
        labels = {
            'task_status': 'Task Status',
            'assigned_to': 'Assigned To',
            'actual_duration': 'Actual Duration (minutes)',
            'notes': 'Update Notes',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].required = False
        self.fields['actual_duration'].required = False
        self.fields['notes'].required = False