from django.utils import timezone 
from django.shortcuts import render
import django.utils.text
import rest_framework.decorators
from .models import InventoryRental, InventoryItems
from . serializers import InventoryItemSerializer, InventoryRentalsSerializer
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.exceptions import ValidationError

# Create your views here.
@api_view(['GET'])
@permission_classes([AllowAny])
def inventory(request):
    inventory = InventoryItems.objects.all()
    serializer = InventoryItemSerializer(inventory, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def add_item(request):
    serializer = InventoryItemSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def delete_item(request):
    
    item_id = request.data.get("id")
    item = InventoryItems.objects.get(id=item_id)
    item.delete()
    return Response({"message": f"Item deleted successfully"})
    
@api_view(['PUT'])
@permission_classes([AllowAny])
def update_item(request, slug):
    item = get_object_or_404(InventoryItems, slug=slug)
    
    serializer = InventoryItemSerializer(instance=item, data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def rent_item(request):
    with transaction.atomic():  
   
        rental_serializer = InventoryRentalsSerializer(data=request.data)

        if rental_serializer.is_valid():
            rental = rental_serializer.save()
            
            item = get_object_or_404(InventoryItems, id=rental.item_id)

            if item.available < rental.quantity:
                raise ValidationError("Not enough items available to rent.")

            item.available -= rental.quantity
            item.rented += rental.quantity
            item.save()

            return Response(rental_serializer.data, status=status.HTTP_201_CREATED)

        return Response(rental_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
@permission_classes([AllowAny])
def return_item(request, rental_id):
    with transaction.atomic():
     
        rental = get_object_or_404(InventoryRental, id=rental_id)

        if rental.status == 'returned':
            return Response({"message": "Item already returned."}, status=status.HTTP_400_BAD_REQUEST)

        item = rental.item

        item.available += rental.quantity
        item.rented -= rental.quantity
        item.save()

        rental.status = 'returned'
        rental.return_date = timezone.now()
        rental.save()

        return Response({"detail": "Item successfully returned."}, status=status.HTTP_200_OK)
    
    
@api_view(['GET'])
@permission_classes([AllowAny])
def list_rentals(request):
    rentals = InventoryRental.objects.all().order_by('-rental_date')
    serializer = InventoryRentalsSerializer(rentals, many=True)
    return Response(serializer.data)

