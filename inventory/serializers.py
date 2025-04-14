from .models import InventoryItems, InventoryRental
from rest_framework import serializers

class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItems
        fields = '__all__'
        
    def validate(self, data):
        quantity = data.get('quantity', getattr(self.instance, 'quantity', 0))
        available = data.get('available', getattr(self.instance, 'available', 0))
        rented = data.get('rented', getattr(self.instance, 'rented', 0))

        print("Running validation:")
        print("quantity =", quantity, "available =", available, "rented =", rented)

        if quantity < 0 or available < 0 or rented < 0:
            raise serializers.ValidationError("Quantities cannot be negative.")

        if available > quantity:
            raise serializers.ValidationError({
                'available': 'Available quantity cannot be greater than total quantity.'
            })

        if rented > quantity:
            raise serializers.ValidationError({
                'rented': 'Rented quantity cannot be greater than total quantity.'
            })

        if available + rented > quantity:
            raise serializers.ValidationError(
                "The sum of available and rented items cannot exceed total quantity."
            )

        return data



class InventoryRentalsSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryRental
        fields = '__all__'