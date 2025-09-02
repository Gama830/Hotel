from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from booking.models import Booking
from guest.models import Guest
from rooms.models import Room


class CheckIn(models.Model):
    """Model for managing guest check-ins"""
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PARTIAL', 'Partial Payment'),
        ('PAID', 'Fully Paid'),
        ('REFUNDED', 'Refunded'),
    ]
    
    check_in_id = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique check-in identifier"
    )
    
    # Link to booking or guest (one must be provided)
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='check_ins',
        blank=True,
        null=True,
        help_text="Associated booking (if pre-booked)"
    )
    
    guest = models.ForeignKey(
        Guest,
        on_delete=models.CASCADE,
        related_name='check_ins',
        help_text="Primary guest checking in"
    )
    
    actual_check_in_date_time = models.DateTimeField(
        default=timezone.now,
        help_text="Actual date and time of check-in"
    )
    
    room_number = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='check_ins',
        help_text="Room assigned for check-in"
    )
    
    id_proof_verified = models.BooleanField(
        default=False,
        help_text="Whether guest's ID proof has been verified"
    )
    
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default='PENDING',
        help_text="Current payment status"
    )
    
    assigned_staff = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Staff member who handled the check-in"
    )
    
    remarks_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional remarks or notes about the check-in"
    )
    
    # Additional useful fields
    expected_check_out_date = models.DateField(
        blank=True,
        null=True,
        help_text="Expected check-out date"
    )
    
    number_of_guests = models.PositiveIntegerField(
        default=1,
        help_text="Total number of guests checking in"
    )
    
    advance_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Advance payment received"
    )
    
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Total amount for the stay"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-actual_check_in_date_time']
        verbose_name = 'Check-In'
        verbose_name_plural = 'Check-Ins'
    
    def __str__(self):
        return f"Check-In {self.check_in_id} - {self.guest.full_name} - Room {self.room_number.room_number}"
    
    def save(self, *args, **kwargs):
        # Auto-generate check_in_id if not provided
        if not self.check_in_id:
            today = timezone.now().date()
            date_str = today.strftime('%Y%m%d')
            count = CheckIn.objects.filter(
                actual_check_in_date_time__date=today
            ).count() + 1
            self.check_in_id = f"CI{date_str}{count:03d}"
        
        # Set total amount from booking if available
        if self.booking and not self.total_amount:
            self.total_amount = self.booking.total_amount
        
        # Set expected check-out from booking if available
        if self.booking and not self.expected_check_out_date:
            self.expected_check_out_date = self.booking.check_out_date
            
        super().save(*args, **kwargs)
    
    @property
    def remaining_amount(self):
        """Calculate remaining amount to be paid"""
        return self.total_amount - self.advance_payment
    
    @property
    def payment_percentage(self):
        """Calculate payment completion percentage"""
        if self.total_amount > 0:
            return (self.advance_payment / self.total_amount) * 100
        return 0
    
    @property
    def is_walk_in(self):
        """Check if this is a walk-in guest (no prior booking)"""
        return self.booking is None
    
    @property
    def days_since_checkin(self):
        """Calculate days since check-in"""
        return (timezone.now().date() - self.actual_check_in_date_time.date()).days