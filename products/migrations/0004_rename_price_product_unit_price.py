# Generated by Django 5.1.7 on 2025-05-23 08:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_alter_category_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='price',
            new_name='unit_price',
        ),
    ]
