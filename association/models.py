from django.db import models
import uuid
from users.models import CustomUser

def generate_farmer_code(association):
    # Take first 3 uppercase letters of association name
    abbr = ''.join(word[0] for word in association.name.split()[:3]).upper()

    # Count current farmers in this association
    count = Farmer.objects.filter(association=association).count() + 1

    return f"{abbr}{count:03d}"  # Pads with zeros, e.g. BGR001

class Association(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    barangay = models.CharField(max_length=100)
    president = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='led_associations'
    )
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Farmer(models.Model):
    # Choices
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    CIVIL_STATUS_CHOICES = [
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Widowed', 'Widowed'),
        ('Divorced', 'Divorced'),
    ]

    # Use farmer_code as primary key
    id = models.CharField(max_length=50, primary_key=True)
    full_name = models.CharField(max_length=255)
    association = models.ForeignKey(Association, on_delete=models.CASCADE, related_name='farmers')
    age = models.PositiveIntegerField()
    birthday = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    civil_status = models.CharField(max_length=10, choices=CIVIL_STATUS_CHOICES, blank=True, null=True)
    address = models.TextField()
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    date_registered = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.full_name} ({self.id})"

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_farmer_code(self.association)
        super().save(*args, **kwargs)

