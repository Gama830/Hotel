from django.db import models
from django.core.validators import MinLengthValidator
from rooms.models import Room

class HousekeepingStatus(models.Model):
    """Model for managing housekeeping status types"""
    
    STATUS_CHOICES = [
        ('CLEAN', 'Clean'),
        ('DIRTY', 'Dirty'),
        ('IN_PROGRESS', 'In Progress'),
        ('OUT_OF_ORDER', 'Out of Order'),
        ('MAINTENANCE', 'Maintenance Required'),
        ('INSPECTED', 'Inspected'),
    ]
    
    status_id = models.AutoField(primary_key=True, verbose_name="Status ID")
    
    status_name = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        unique=True,
        help_text="Housekeeping status name"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of the housekeeping status"
    )
    
    color_code = models.CharField(
        max_length=7,
        default='#6c757d',
        help_text="Color code for status display (hex format)"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this status is currently active"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['status_name']
        verbose_name = 'Housekeeping Status'
        verbose_name_plural = 'Housekeeping Statuses'
    
    def __str__(self):
        return f"{self.get_status_name_display()}"
    
    @property
    def display_name(self):
        """Get the display name for the status"""
        return self.get_status_name_display()


class HousekeepingTask(models.Model):
    """Model for managing housekeeping tasks for rooms"""
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    
    TASK_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='housekeeping_tasks',
        help_text="Room for this housekeeping task"
    )
    
    status = models.ForeignKey(
        HousekeepingStatus,
        on_delete=models.CASCADE,
        related_name='tasks',
        help_text="Current housekeeping status"
    )
    
    task_type = models.CharField(
        max_length=100,
        help_text="Type of housekeeping task (e.g., Daily Cleaning, Deep Clean, Maintenance)"
    )
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MEDIUM',
        help_text="Priority level of the task"
    )
    
    task_status = models.CharField(
        max_length=20,
        choices=TASK_STATUS_CHOICES,
        default='PENDING',
        help_text="Current status of the task"
    )
    
    assigned_to = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Staff member assigned to this task"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed description of the housekeeping task"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes or observations"
    )
    
    estimated_duration = models.PositiveIntegerField(
        default=30,
        help_text="Estimated duration in minutes"
    )
    
    actual_duration = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Actual duration taken in minutes"
    )
    
    scheduled_date = models.DateField(
        help_text="Date when the task is scheduled"
    )
    
    scheduled_time = models.TimeField(
        blank=True,
        null=True,
        help_text="Time when the task is scheduled"
    )
    
    started_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the task was started"
    )
    
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the task was completed"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_date', 'priority', 'room__room_number']
        verbose_name = 'Housekeeping Task'
        verbose_name_plural = 'Housekeeping Tasks'
    
    def __str__(self):
        return f"Room {self.room.room_number} - {self.task_type} ({self.get_task_status_display()})"
    
    @property
    def is_overdue(self):
        """Check if the task is overdue"""
        from django.utils import timezone
        if self.task_status in ['COMPLETED', 'CANCELLED']:
            return False
        
        scheduled_datetime = timezone.datetime.combine(
            self.scheduled_date,
            self.scheduled_time or timezone.datetime.min.time()
        )
        scheduled_datetime = timezone.make_aware(scheduled_datetime)
        
        return timezone.now() > scheduled_datetime
    
    @property
    def duration_display(self):
        """Get formatted duration display"""
        if self.actual_duration:
            hours = self.actual_duration // 60
            minutes = self.actual_duration % 60
            if hours > 0:
                return f"{hours}h {minutes}m"
            return f"{minutes}m"
        return f"{self.estimated_duration}m (est.)"


class HousekeepingInspection(models.Model):
    """Model for room inspections after housekeeping"""
    
    INSPECTION_STATUS_CHOICES = [
        ('PASSED', 'Passed'),
        ('FAILED', 'Failed'),
        ('NEEDS_ATTENTION', 'Needs Attention'),
    ]
    
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='inspections',
        help_text="Room being inspected"
    )
    
    task = models.ForeignKey(
        HousekeepingTask,
        on_delete=models.CASCADE,
        related_name='inspections',
        blank=True,
        null=True,
        help_text="Related housekeeping task"
    )
    
    inspector_name = models.CharField(
        max_length=100,
        help_text="Name of the inspector"
    )
    
    inspection_status = models.CharField(
        max_length=20,
        choices=INSPECTION_STATUS_CHOICES,
        help_text="Result of the inspection"
    )
    
    cleanliness_score = models.PositiveIntegerField(
        default=5,
        help_text="Cleanliness score out of 10"
    )
    
    issues_found = models.TextField(
        blank=True,
        null=True,
        help_text="Issues found during inspection"
    )
    
    corrective_actions = models.TextField(
        blank=True,
        null=True,
        help_text="Actions needed to address issues"
    )
    
    inspection_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional inspection notes"
    )
    
    inspection_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time of inspection"
    )
    
    follow_up_required = models.BooleanField(
        default=False,
        help_text="Whether follow-up inspection is required"
    )
    
    follow_up_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date for follow-up inspection"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-inspection_date']
        verbose_name = 'Housekeeping Inspection'
        verbose_name_plural = 'Housekeeping Inspections'
    
    def __str__(self):
        return f"Room {self.room.room_number} - {self.get_inspection_status_display()} ({self.inspection_date.strftime('%Y-%m-%d')})"
    
    @property
    def score_percentage(self):
        """Get cleanliness score as percentage"""
        return (self.cleanliness_score / 10) * 100
    
    @property
    def score_grade(self):
        """Get letter grade based on score"""
        if self.cleanliness_score >= 9:
            return 'A+'
        elif self.cleanliness_score >= 8:
            return 'A'
        elif self.cleanliness_score >= 7:
            return 'B'
        elif self.cleanliness_score >= 6:
            return 'C'
        else:
            return 'D'