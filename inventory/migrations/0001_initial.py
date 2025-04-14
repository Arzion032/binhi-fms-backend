# Generated by Django 5.1.7 on 2025-04-14 12:07

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0004_rename_user_userprofile_user_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='InventoryItems',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('item_name', models.TextField()),
                ('rental_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.IntegerField()),
                ('available', models.IntegerField()),
                ('rented', models.IntegerField(default=0)),
                ('unit', models.CharField(blank=True, max_length=50)),
                ('category', models.CharField(blank=True, max_length=50)),
                ('description', models.CharField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='InventoryRental',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('renter_name', models.CharField(max_length=255)),
                ('contact_number', models.CharField(max_length=15)),
                ('quantity', models.PositiveIntegerField()),
                ('notes', models.TextField(blank=True, null=True)),
                ('rental_date', models.DateTimeField(auto_now_add=True)),
                ('return_date', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('rented', 'Rented'), ('returned', 'Returned')], default='rented', max_length=10)),
                ('admin_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventory_rentals', to='users.customuser')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rentals', to='inventory.inventoryitems')),
            ],
        ),
    ]
