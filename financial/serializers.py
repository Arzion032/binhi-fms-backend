from .models import Financials
from rest_framework import serializers
from django.db.models import Sum, Case, When, DecimalField, F, Value

class FinancialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Financials
        fields = '__all__'
        
def get_federation_balance():
    result = Financials.objects.aggregate(
        balance=Sum(
            Case(
                When(type='income', then=F('amount')),
                When(type='expense', then=F('amount') * -1),
                default=Value(0),
                output_field=DecimalField()
            )
        )
    )
    return result['balance'] or 0
