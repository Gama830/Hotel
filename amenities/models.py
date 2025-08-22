from django.db import models

class Amenity(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Amenity Name")
    description = models.TextField(blank=True, verbose_name="Description")
    applicable_room_types = models.ManyToManyField('rooms.RoomType', blank=True, verbose_name="Applicable Room Types", related_name='applicable_amenities')
    quantity_limit = models.PositiveIntegerField(null=True, blank=True, verbose_name="Quantity/Limit", 
                                               help_text="Leave blank if not applicable")

    class Meta:
        verbose_name_plural = "Amenities"
        ordering = ['name']

    def __str__(self):
        return self.name
