from django.db import models

class Amenity(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Amenity Name")
    description = models.TextField(blank=True, verbose_name="Description")
    applicable_room_types = models.ManyToManyField('rooms.RoomType', blank=True, verbose_name="Applicable Room Types", related_name='applicable_amenities')
    quantity_limit = models.PositiveIntegerField(null=True, blank=True, verbose_name="Quantity/Limit", 
                                               help_text="Leave blank if not applicable")
    
    # Link to services
    related_services = models.ManyToManyField(
        'service.Service', 
        blank=True, 
        verbose_name="Related Services",
        help_text="Services associated with this amenity",
        related_name='amenities'
    )
    
    # Additional fields for service integration
    is_chargeable = models.BooleanField(
        default=False,
        verbose_name="Chargeable Amenity",
        help_text="Check if this amenity has associated charges"
    )
    
    base_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Base Charge (₹)",
        help_text="Base charge for this amenity (if chargeable)"
    )

    class Meta:
        verbose_name_plural = "Amenities"
        ordering = ['name']

    def __str__(self):
        return self.name
