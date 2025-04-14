from django.contrib import admin
from .models import InventoryItems, InventoryRental
# Register your models here.

admin.site.register([InventoryItems, InventoryRental])


