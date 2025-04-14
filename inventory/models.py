from django.db import models
import uuid
from users.models import CustomUser
# Create your models here.

class InventoryItems(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, blank=False, null=False)
    admin_id = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='inventory'),
    item_name = models.TextField(blank=False, null=False)
    rental_price = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    quantity = models.IntegerField(blank=False, null=False)
    available = models.IntegerField(blank=False, null=False)
    rented = models.IntegerField(blank=False, null=False, default=0)
    unit = models.CharField(max_length=50, blank=True)
    category = models.CharField(max_length=50, blank=True)
    description = models.CharField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class InventoryRental(models.Model):
    STATUS_CHOICES = [
        ('rented', 'Rented'),
        ('returned', 'Returned'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    admin_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='inventory_rentals')
    item = models.ForeignKey(InventoryItems, on_delete=models.CASCADE, related_name='rentals')
    renter_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)
    quantity = models.PositiveIntegerField()
    notes = models.TextField(blank=True, null=True)
    rental_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='rented')
    
    def __str__(self):
        return f"{self.renter_name} - {self.item.item_name} ({self.status})"