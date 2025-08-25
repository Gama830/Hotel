from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from guest.models import Guest
from rooms.models import Room

class Booking(models.Model):
    STATUS_CHOICES = [
        ('CONFIRMED', 'Confirmed'),
        ('CHECKED_IN', 'Checked In'),
        ('CHECKED_OUT', 'Checked Out'),
        ('CANCELED', 'Canceled'),
        ('NO_SHOW', 'No Show'),
        ('PENDING', 'Pending'),
    ]
    
    # Foreign Key relationships
    guest = models.ForeignKey(
        Guest, 
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text="The guest making this booking"
    )
    room = models.ForeignKey(
        Room, 
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text="The room being booked"
    )
    
    # Date fields
    check_in_date = models.DateField(
        help_text="The scheduled date of arrival"
    )
    check_out_date = models.DateField(
        help_text="The scheduled date of departure"
    )
    
    # Guest count fields
    number_of_adults = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="The number of adults for the booking"
    )
    number_of_children = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="The number of children for the booking"
    )
    
    # Booking status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='CONFIRMED',
        help_text="The status of the booking"
    )
    
    # Financial information
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="The calculated total cost of the room for the stay"
    )
    
    # Additional booking information
    special_requests = models.TextField(
        blank=True,
        null=True,
        help_text="Any special requests or notes for the booking"
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
            return self.room.price_per_night * nights
        return Decimal('0.00')
    
    def save(self, *args, **kwargs):
        # Auto-calculate total amount if not provided
        if not self.total_amount:
            self.total_amount = self.calculate_total_amount()
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