from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from rooms.models import RoomType

class RatePlan(models.Model):
    MEAL_PLAN_CHOICES = [
        ('EP', 'European Plan (Room Only)'),
        ('CP', 'Continental Plan (Room + Breakfast)'),
        ('MAP', 'Modified American Plan (Room + Breakfast + Dinner)'),
        ('AP', 'American Plan (Room + All Meals)'),
        ('AI', 'All Inclusive'),
    ]
    
    SEASON_CHOICES = [
        ('PEAK', 'Peak Season'),
        ('HIGH', 'High Season'),
        ('REGULAR', 'Regular Season'),
        ('LOW', 'Low Season'),
        ('OFF', 'Off Season'),
    ]
    
    # Primary key
    rate_plan_id = models.AutoField(primary_key=True)
    
    # Rate identification
    rate_name = models.CharField(
        max_length=100,
        help_text="Name of the rate plan (e.g., 'Summer Special', 'Corporate Rate')"
    )
    
    # Room type relationship
    room_type = models.ForeignKey(
        RoomType,
        on_delete=models.CASCADE,
        related_name='rate_plans',
        help_text="Links to Room Type Master"
    )
    
    # Season/Date Range
    season_type = models.CharField(
        max_length=10,
        choices=SEASON_CHOICES,
        default='REGULAR',
        help_text="Season category for this rate"
    )
    
    # Date range for validity
    valid_from = models.DateField(
        help_text="Start date for this rate plan"
    )
    valid_to = models.DateField(
        help_text="End date for this rate plan"
    )
    
    # Pricing
    base_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Base rate per night for the room type"
    )
    
    additional_guest_charges = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Extra charges per additional guest beyond base occupancy"
    )
    
    # Meal plan
    meal_plan = models.CharField(
        max_length=3,
        choices=MEAL_PLAN_CHOICES,
        default='EP',
        help_text="Meal plan included in the rate"
    )
    
    meal_plan_cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Cost of meal plan per person per day (if applicable)"
    )
    
    # Policies
    cancellation_policy = models.TextField(
        help_text="Cancellation policy for this rate plan"
    )
    
    # Additional information
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Additional description or terms for this rate plan"
    )
    
    # Discounts and modifiers
    weekend_surcharge = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Additional charges for weekends (percentage or fixed amount)"
    )
    
    is_percentage_surcharge = models.BooleanField(
        default=False,
        help_text="Whether weekend surcharge is a percentage (True) or fixed amount (False)"
    )
    
    # Status and availability
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this rate plan is currently active"
    )
    
    minimum_stay = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Minimum number of nights required for this rate"
    )
    
    maximum_stay = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Maximum number of nights allowed for this rate (optional)"
    )
    
    # Advance booking requirements
    advance_booking_days = models.PositiveIntegerField(
        default=0,
        help_text="Minimum days in advance required for booking"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['room_type', 'valid_from', 'rate_name']
        verbose_name = 'Rate Plan'
        verbose_name_plural = 'Rate Plans'
        
        # Ensure no overlapping rate plans for the same room type and season
        constraints = [
            models.CheckConstraint(
                check=models.Q(valid_to__gt=models.F('valid_from')),
                name='valid_to_after_valid_from'
            ),
            models.CheckConstraint(
                check=models.Q(base_rate__gt=0),
                name='base_rate_positive'
            )
        ]
        
        # Unique constraint to prevent duplicate rate plans
        unique_together = ['room_type', 'rate_name', 'valid_from', 'valid_to']
    
    def __str__(self):
        return f"{self.rate_name} - {self.room_type.name} ({self.get_season_type_display()})"
    
    @property
    def validity_period(self):
        """Return formatted validity period"""
        return f"{self.valid_from.strftime('%b %d, %Y')} - {self.valid_to.strftime('%b %d, %Y')}"
    
    @property
    def is_currently_valid(self):
        """Check if rate plan is currently valid"""
        from datetime import date
        today = date.today()
        return self.valid_from <= today <= self.valid_to and self.is_active
    
    def calculate_total_rate(self, nights=1, guests=1, include_meal=True):
        """Calculate total rate for given nights and guests"""
        total = self.base_rate * nights
        
        # Add additional guest charges
        if guests > 1:
            additional_guests = guests - 1
            total += (self.additional_guest_charges * additional_guests * nights)
        
        # Add meal plan cost
        if include_meal and self.meal_plan != 'EP':
            total += (self.meal_plan_cost * guests * nights)
        
        return total
    
    def get_weekend_rate(self, base_amount):
        """Calculate rate with weekend surcharge"""
        if self.weekend_surcharge > 0:
            if self.is_percentage_surcharge:
                return base_amount + (base_amount * self.weekend_surcharge / 100)
            else:
                return base_amount + self.weekend_surcharge
        return base_amount
    
    def clean(self):
        """Validate rate plan data"""
        from django.core.exceptions import ValidationError
        
        # Check if valid_to is after valid_from
        if self.valid_to <= self.valid_from:
            raise ValidationError('Valid to date must be after valid from date.')
        
        # Check maximum stay is greater than minimum stay
        if self.maximum_stay and self.maximum_stay < self.minimum_stay:
            raise ValidationError('Maximum stay must be greater than or equal to minimum stay.')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)