# Generated by Django 5.1.7 on 2025-04-02 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_rename_user_customuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('member', 'Member'), ('farmer', 'Farmer'), ('buyer', 'Buyer')], max_length=20),
        ),
    ]
