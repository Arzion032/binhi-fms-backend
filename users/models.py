from django.db import models
import uuid
# Create your models here.

# This is the User Credentials
class CustomUser(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('farmer', 'Farmer'),
        ('buyer', 'Buyer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, blank=False, null=False)
    contact_no = models.CharField(max_length=15, blank=False, null=False)
    username = models.TextField(unique=True, blank=False, null=False)
    password = models.TextField(blank=False, null=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    updated_at = models.DateTimeField(auto_now=True, blank=False, null=False)
    
    def __str__(self):
        return self.username
    
        # CONTACT NO validation
        """
           def validate_contact_no(self, value):
        if not re.match(r'^09/d{9}$', value):
            raise serializers.ValidationError("Enter a valid PH contact number (e.g., 09171234567).")
        return value
        """

# This is the User Profiles   
class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True, related_name='profile')  
    full_name = models.TextField(blank=False, null=False)
    address = models.TextField(blank=False, null=False)
    profile_picture = models.TextField(blank=False, null=False)
    other_details = models.JSONField(blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name
    
class VerifiedEmail(models.Model):
    email = models.EmailField(unique=True)
    verified_at = models.DateTimeField(auto_now_add=True)
