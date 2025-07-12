from django.db import models
import uuid


def generate_farmer_code(association):
    # Take abbreviation
    abbr = ''.join(word[0] for word in association.name.split()[:3]).upper()

    # Increment the last number and save
    association.last_farmer_number += 1
    association.save()

    return f"{abbr}-{association.last_farmer_number:03d}"

class Association(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    last_farmer_number = models.IntegerField(default=0)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    barangay = models.CharField(max_length=100, blank=True, null=True)
    president = models.ForeignKey(
        'users.CustomUser',
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


from datetime import date
from django.db import models

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
    association = models.ForeignKey('Association', on_delete=models.CASCADE, related_name='farmers')
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

    @property
    def age(self):
        today = date.today()
        if self.birthday:
            return today.year - self.birthday.year - (
                (today.month, today.day) < (self.birthday.month, self.birthday.day)
            )
        return None


