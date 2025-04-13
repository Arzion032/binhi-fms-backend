from django.contrib import admin
from .models import CustomUser, UserProfile  # Import your custom UserProfile model

admin.site.register([UserProfile])
@admin.register(CustomUser)  # Registers the CustomUser model with the admin
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'contact_no', 'username', 'password', 'email', 'role', 'created_at', 'updated_at')
    search_fields = ('username', 'email')
    list_filter = ('role',)
    ordering = ('-created_at',)  # Order by creation date, most recent first
    
    # Define which fields are editable in the admin form
    fields = ('contact_no', 'username', 'password', 'email', 'role')
    readonly_fields = ('id', 'created_at', 'updated_at') 
    
