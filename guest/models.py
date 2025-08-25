from django.db import models
from django.core.validators import RegexValidator

class Guest(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    ID_PROOF_CHOICES = [
        ('AADHAR', 'Aadhar Card'),
        ('PAN', 'PAN Card'),
        ('PASSPORT', 'Passport'),
        ('DRIVING_LICENSE', 'Driving License'),
        ('VOTER_ID', 'Voter ID'),
        ('OTHER', 'Other'),
    ]
    
    LOYALTY_LEVELS = [
        ('BRONZE', 'Bronze'),
        ('SILVER', 'Silver'),
        ('GOLD', 'Gold'),
        ('PLATINUM', 'Platinum'),
        ('DIAMOND', 'Diamond'),
    ]
    
    # Phone number validator
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    guest_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    address = models.TextField()
    contact_number = models.CharField(validators=[phone_regex], max_length=17)
    email = models.EmailField(unique=True)
    nationality = models.CharField(max_length=100, default='Indian')
    id_proof_type = models.CharField(max_length=20, choices=ID_PROOF_CHOICES)
    id_proof_number = models.CharField(max_length=50)
    loyalty_level = models.CharField(max_length=10, choices=LOYALTY_LEVELS, default='BRONZE')
    member_id = models.CharField(max_length=20, blank=True, null=True)
    preferences_notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['first_name', 'last_name']
        verbose_name = 'Guest'
        verbose_name_plural = 'Guests'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} (ID: {self.guest_id})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        # Auto-generate member ID if loyalty level is not BRONZE
        if self.loyalty_level != 'BRONZE' and not self.member_id:
            self.member_id = f"{self.loyalty_level[:3]}{str(self.guest_id).zfill(6)}"
        super().save(*args, **kwargs)