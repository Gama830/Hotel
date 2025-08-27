from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from guest.models import Guest
from rooms.models import Room
from rate.models import RatePlan

class Booking(models.Model):
    STATUS_CHOICES = [
        ('CONFIRMED', 'Confirmed'),
        ('CHECKED_IN', 'Checked In'),
        ('CHECKED_OUT', 'Checked Out'),
        ('CANCELED', 'Canceled'),
        ('NO_SHOW', 'No Show'),
        ('PENDING', 'Pending'),
    ]
    
    BOOKING_SOURCE_CHOICES = [
        ('DIRECT', 'Direct'),
        ('OTA', 'Online Travel Agency'),
        ('AGENT', 'Travel Agent'),
        ('PHONE', 'Phone'),
        ('EMAIL', 'Email'),
        ('WALK_IN', 'Walk-in'),
        ('CORPORATE', 'Corporate'),
        ('WEBSITE', 'Website'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PARTIAL', 'Partial Payment'),
        ('PAID', 'Fully Paid'),
        ('REFUNDED', 'Refunded'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Reservation/Booking ID (unique identifier) - Django auto-creates 'id' field
    
    # Foreign Key relationships
    guest = models.ForeignKey(
        Guest, 
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text="Guest ID or details"
    )
    room = models.ForeignKey(
        Room, 
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text="Room Type and Number"
    )
    
    # Rate Plan
    rate_plan = models.ForeignKey(
        RatePlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings',
        help_text="Rate Plan applied to this booking"
    )
    
    # Date and Time fields
    check_in_date = models.DateField(
        help_text="Check-in Date"
    )
    check_out_date = models.DateField(
        help_text="Check-out Date"
    )
    
    # Actual check-in and check-out times
    actual_check_in_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Actual check-in date and time"
    )
    actual_check_out_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Actual check-out date and time"
    )
    
    # Number of Guests
    number_of_adults = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Number of adults"
    )
    number_of_children = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of children"
    )
    
    # Booking Source
    booking_source = models.CharField(
        max_length=20,
        choices=BOOKING_SOURCE_CHOICES,
        default='DIRECT',
        help_text="Booking Source (direct, OTA, agent)"
    )
    
    # Reservation Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='CONFIRMED',
        help_text="Reservation Status (confirmed, pending, cancelled)"
    )
    
    # Payment Details
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total booking amount"
    )
    
    advance_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Advance payment received"
    )
    
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='PENDING',
        help_text="Payment status"
    )
    
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Payment method used"
    )
    
    # Special Requests
    special_requests = models.TextField(
        blank=True,
        null=True,
        help_text="Special Requests"
    )
    
    # Additional booking details
    confirmation_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="External confirmation number (for OTA bookings)"
    )
    
    booking_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Internal booking notes"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        
        # Ensure no double booking of the same room for overlapping dates
        constraints = [
            models.CheckConstraint(
                check=models.Q(check_out_date__gt=models.F('check_in_date')),
                name='check_out_after_check_in'
            )
        ]
    
    def __str__(self):
        return f"Booking #{self.id} - {self.guest.full_name} - Room {self.room.room_number}"
    
    @property
    def duration_nights(self):
        """Calculate the number of nights for the stay"""
        return (self.check_out_date - self.check_in_date).days
    
    @property
    def total_guests(self):
        """Calculate total number of guests"""
        return self.number_of_adults + self.number_of_children
    
    def calculate_total_amount(self):
        """Calculate the total amount based on room price and duration"""
        nights = self.duration_nights
        if nights > 0:
            # Try rate plan first
            if self.rate_plan:
                try:
                    return self.rate_plan.calculate_total_rate(nights, self.total_guests)
                except:
                    pass  # Fall back to room rates if rate plan calculation fails
            
            # Try room type price
            if hasattr(self.room, 'room_type') and self.room.room_type and self.room.room_type.price_per_night:
                return self.room.room_type.price_per_night * nights
            
            # Fall back to room default rate
            if self.room.rate_default:
                return self.room.rate_default * nights
                
        return Decimal('0.00')
    
    @property
    def remaining_amount(self):
        """Calculate remaining amount to be paid"""
        return self.total_amount - self.advance_payment
    
    @property
    def is_fully_paid(self):
        """Check if booking is fully paid"""
        return self.payment_status == 'PAID' or self.advance_payment >= self.total_amount
    
    def save(self, *args, **kwargs):
        # Auto-calculate total amount if not provided or if it's zero
        if not self.total_amount or self.total_amount == Decimal('0.00'):
            calculated_amount = self.calculate_total_amount()
            if calculated_amount > 0:
                self.total_amount = calculated_amount
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validate booking data"""
        from django.core.exceptions import ValidationError
        
        # Check if check-out date is after check-in date
        if self.check_out_date <= self.check_in_date:
            raise ValidationError('Check-out date must be after check-in date.')
        
        # Check if the room capacity is sufficient
        if hasattr(self.room, 'room_type') and self.room.room_type.capacity:
            if self.total_guests > self.room.room_type.capacity:
                raise ValidationError(
                    f'Total guests ({self.total_guests}) exceeds room capacity ({self.room.room_type.capacity}).'
                )
    
    def is_active(self):
        """Check if booking is currently active (checked in)"""
        return self.status == 'CHECKED_IN'
    
    def can_check_in(self):
        """Check if booking can be checked in"""
        return self.status in ['CONFIRMED', 'PENDING']
    
    def can_check_out(self):
        """Check if booking can be checked out"""
        return self.status == 'CHECKED_IN'
    
    def can_cancel(self):
        """Check if booking can be canceled"""
        return self.status in ['CONFIRMED', 'PENDING']
    
    def check_in(self):
        """Perform check-in operation"""
        from django.utils import timezone
        if self.can_check_in():
            self.status = 'CHECKED_IN'
            self.actual_check_in_time = timezone.now()
            # Update room status to occupied
            self.room.status = 'OCCUPIED'
            self.room.save()
            self.save()
            return True
        return False
    
    def check_out(self):
        """Perform check-out operation"""
        from django.utils import timezone
        if self.can_check_out():
            self.status = 'CHECKED_OUT'
            self.actual_check_out_time = timezone.now()
            # Update room status to available
            self.room.status = 'AVAILABLE'
            self.room.save()
            self.save()
            return True
        return False
    
    @property
    def actual_duration_hours(self):
        """Calculate actual stay duration in hours"""
        if self.actual_check_in_time and self.actual_check_out_time:
            duration = self.actual_check_out_time - self.actual_check_in_time
            return duration.total_seconds() / 3600
        return None