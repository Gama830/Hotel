from django.db import models

class RoomType(models.Model):
    BED_TYPE_CHOICES = [
        ('SINGLE', 'Single Bed'),
        ('DOUBLE', 'Double Bed'),
        ('KING', 'King Bed'),
        ('QUEEN', 'Queen Bed'),
        ('TWIN', 'Twin Bed'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField()
    bed_type = models.CharField(max_length=20, choices=BED_TYPE_CHOICES, default='SINGLE', verbose_name="Bed Type")
    amenities = models.ManyToManyField('amenities.Amenity', blank=True)

    def __str__(self):
        return self.name

class AssetType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class Asset(models.Model):
    asset_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    asset_type = models.ForeignKey(AssetType, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.name} ({self.asset_id})"

class Room(models.Model):
    ROOM_STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('OCCUPIED', 'Occupied'),
        ('MAINTENANCE', 'Under Maintenance'),
        ('OUT_OF_ORDER', 'Out of Order'),
    ]
    
    BED_TYPE_CHOICES = [
        ('SINGLE', 'Single Bed'),
        ('DOUBLE', 'Double Bed'),
        ('KING', 'King Bed'),
        ('QUEEN', 'Queen Bed'),
        ('TWIN', 'Twin Bed'),
    ]
    
    VIEW_CHOICES = [
        ('SEA', 'Sea View'),
        ('CITY', 'City View'),
        ('GARDEN', 'Garden View'),
        ('MOUNTAIN', 'Mountain View'),
        ('POOL', 'Pool View'),
        ('COURTYARD', 'Courtyard View'),
    ]
    
    # Basic room information
    room_number = models.CharField(max_length=10, unique=True, verbose_name="Room ID/Number")
    room_type = models.ForeignKey(RoomType, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Room Type")
    floor = models.IntegerField(verbose_name="Floor Number")
    
    # Bed configuration
    bed_type = models.CharField(max_length=20, choices=BED_TYPE_CHOICES, default='SINGLE', verbose_name="Bed Type")
    single_bed = models.BooleanField(default=False)
    double_bed = models.BooleanField(default=False)
    extra_bed = models.BooleanField(default=False)
    
    # Capacity and occupancy
    max_occupancy = models.PositiveIntegerField(default=1, verbose_name="Max Occupancy")
    allow_pax = models.PositiveIntegerField(default=1, verbose_name="Allow Pax")
    
    # Room status and condition
    status = models.CharField(max_length=20, choices=ROOM_STATUS_CHOICES, default='AVAILABLE')
    description = models.TextField(blank=True, verbose_name="Description/Notes")
    
    # Room features
    view = models.CharField(max_length=20, choices=VIEW_CHOICES, blank=True, verbose_name="View")
    amenities = models.ManyToManyField('amenities.Amenity', blank=True, verbose_name="Features/Amenities")
    
    # Pricing
    rate_default = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Rate (Default)")
    tariff = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Keep for backward compatibility
    
    # Legacy fields for backward compatibility
    slave_time = models.CharField(max_length=100, blank=True, verbose_name="Slave Time")
    conditions = models.TextField(blank=True)
    asset_type = models.ForeignKey(AssetType, on_delete=models.SET_NULL, null=True, blank=True)
    asset = models.ForeignKey(Asset, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Room {self.room_number} - Floor {self.floor}"
