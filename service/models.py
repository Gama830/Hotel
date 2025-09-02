from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Service(models.Model):
    """Model for managing hotel services like Spa, Laundry, etc."""
    
    service_id = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique service identifier"
    )
    
    service_name = models.CharField(
        max_length=100,
        help_text="Service name (e.g., Spa, Laundry, Room Service)"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed description of the service"
    )
    
    rate_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Service rate/cost in ₹"
    )
    
    tax_applicable = models.BooleanField(
        default=True,
        help_text="Whether tax is applicable on this service"
    )
    
    # Availability choices
    AVAILABILITY_CHOICES = [
        ('24_7', '24/7 Available'),
        ('BUSINESS_HOURS', 'Business Hours Only'),
        ('WEEKDAYS', 'Weekdays Only'),
        ('WEEKENDS', 'Weekends Only'),
        ('CUSTOM', 'Custom Hours'),
    ]
    
    availability = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default='BUSINESS_HOURS',
        help_text="Service availability schedule"
    )
    
    # Custom availability fields
    available_from = models.TimeField(
        blank=True,
        null=True,
        help_text="Service available from (for custom hours)"
    )
    
    available_to = models.TimeField(
        blank=True,
        null=True,
        help_text="Service available until (for custom hours)"
    )
    
    available_days = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Available days (for custom schedule)"
    )
    
    # Additional fields
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this service is currently active"
    )
    
    requires_booking = models.BooleanField(
        default=False,
        help_text="Whether this service requires advance booking"
    )
    
    max_capacity = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Maximum capacity/slots available (if applicable)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['service_name']
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
    
    def __str__(self):
        return f"{self.service_name} (₹{self.rate_cost})"
    
    def save(self, *args, **kwargs):
        # Auto-generate service_id if not provided
        if not self.service_id:
            # Create service ID based on service name
            name_prefix = ''.join([word[0].upper() for word in self.service_name.split()[:2]])
            count = Service.objects.filter(service_name__icontains=self.service_name.split()[0]).count() + 1
            self.service_id = f"{name_prefix}{count:03d}"
        
        # Set default pricing values since they will be handled during billing
        if not self.rate_cost:
            self.rate_cost = Decimal('0.00')  # Will be set during billing
        
        super().save(*args, **kwargs)
    
    @property
    def availability_display(self):
        """Return formatted availability information"""
        if self.availability == 'CUSTOM' and self.available_from and self.available_to:
            return f"{self.available_from.strftime('%H:%M')} - {self.available_to.strftime('%H:%M')}"
        return self.get_availability_display()
    
    @property
    def total_cost_with_tax(self):
        """Calculate total cost including tax (assuming 18% GST)"""
        if self.tax_applicable:
            return (self.rate_cost * Decimal('1.18')).quantize(Decimal('0.01'))
        return self.rate_cost


class ServiceCharge(models.Model):
    """A charge for a specific service billed to a guest/booking."""

    STATUS_CHOICES = [
        ('BILLED', 'Billed'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    ]

    service = models.ForeignKey(
        'Service',
        on_delete=models.PROTECT,
        related_name='charges',
        help_text="Which service is being billed",
    )

    # Optional link to a room booking (when guest is in-house)
    booking = models.ForeignKey(
        'booking.Booking',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='service_charges',
        help_text="Associated booking, if applicable",
    )

    # Guest is required to know who is being billed
    guest = models.ForeignKey(
        'guest.Guest',
        on_delete=models.PROTECT,
        related_name='service_charges',
        help_text="Guest to bill",
    )

    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Quantity of the service",
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Price per unit at time of billing",
    )

    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('18.00'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Tax rate percentage applied",
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Total bill amount including tax",
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='BILLED',
        help_text="Current payment status of this charge",
    )

    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Service Charge'
        verbose_name_plural = 'Service Charges'

    def __str__(self):
        return f"{self.service.service_name} x{self.quantity} - ₹{self.total_amount} ({self.get_status_display()})"

    def calculate_total(self) -> Decimal:
        subtotal = self.unit_price * self.quantity
        tax_amount = Decimal('0.00')
        if self.tax_rate and self.tax_rate > 0:
            tax_amount = (subtotal * self.tax_rate) / Decimal('100')
        return (subtotal + tax_amount).quantize(Decimal('0.01'))

    def save(self, *args, **kwargs):
        # Auto-populate unit_price from service if not set
        if self.unit_price is None:
            self.unit_price = self.service.rate_cost
        # Auto-calc tax_rate from service if not explicitly set
        if self.tax_rate is None:
            self.tax_rate = Decimal('18.00') if self.service.tax_applicable else Decimal('0.00')
        # Always compute total_amount
        self.total_amount = self.calculate_total()
        super().save(*args, **kwargs)