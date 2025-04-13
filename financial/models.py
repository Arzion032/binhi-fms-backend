from django.db import models
import uuid
from users.models import CustomUser
# Create your models here.

class Financials(models.Model):
    transaction_type= [
        ('income', 'Income'),
        ('expense', 'Expense')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, blank=False, null=False)
    admin_id = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=20, choices=transaction_type, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    source = models.TextField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    
    def __str__(self):
        return f"{self.type} - {self.amount} by {self.admin_id.username}"
    