from django.shortcuts import render
from rest_framework.decorators import api_view
from .serializers import FinancialSerializer, get_federation_balance
from .models import Financials
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

# Create your views here.

@api_view(['GET'])
@permission_classes([AllowAny])
def federation_balance_view(request):
    balance = get_federation_balance()
    return Response({'balance': balance})

@api_view(["GET"])
@permission_classes([AllowAny])
def transactions(request):
    transactions = Financials.objects.all()
    serializer = FinancialSerializer(transactions, many=True)
    return Response(serializer.data)

# Delete endpoint
@api_view(["POST"])
@permission_classes([AllowAny])
def add_transaction(request):
    serializer = FinancialSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
     
# Delete endpoint
@api_view(["POST"])
@permission_classes([AllowAny])
def del_transaction(request):
    
    transaction_id = request.data.get("id")
    transaction = Financials.objects.get(id=transaction_id)
    transaction.delete()
    return Response({"message":f"Item deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

            
          