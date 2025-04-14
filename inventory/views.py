from django.shortcuts import render
import rest_framework.decorators
from .models import InventoryRental, InventoryItems
from . serializers import InventoryItemSerializer, InventoryRentalsSerializer
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

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
    