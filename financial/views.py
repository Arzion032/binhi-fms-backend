from django.shortcuts import render
from rest_framework.decorators import api_view
from .serializers import FinancialSerializer, get_federation_balance
from .models import Financials
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.db.models import Sum
from django.db.models.functions import TruncMonth, TruncQuarter, TruncYear
from datetime import datetime
import json
from users.models import CustomUser

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

@api_view(["POST"])
@permission_classes([AllowAny])
def add_transaction(request):
    print("------ add_transaction view called ------") # Added for debugging
    try:
        # Log raw request data
        print("Raw request data:", request.data)
        print("Request content type:", request.content_type)

        # Create a copy of the data
        data = request.data.copy()

        # Set default values for required fields if not provided
        if 'type' not in data:
            data['type'] = 'income'  # Default to income
        if 'description' not in data:
            data['description'] = 'No description provided'
        if 'source' not in data:
            data['source'] = 'No source provided'
        if 'name' not in data:
            data['name'] = 'No name provided'

        # Convert amount to decimal if it's a string
        if 'amount' in data:
            try:
                if isinstance(data['amount'], str):
                    data['amount'] = float(data['amount'])
            except ValueError:
                return Response({'error': 'Invalid amount format'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Amount is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure type is lowercase
        data['type'] = data['type'].lower()

        # Get or create a default admin user for testing
        try:
            default_admin = CustomUser.objects.get(email='admin@test.com')
        except CustomUser.DoesNotExist:
            default_admin = CustomUser.objects.create(
                email='admin@test.com',
                username='admin',
                password='admin123',
                is_active=True
            )
        
        data['admin'] = default_admin.id

        # Log processed data
        print("Processed data (before serializer):", data)

        # Create serializer with partial=True to allow missing fields
        serializer = FinancialSerializer(data=data, partial=True)
        if serializer.is_valid():
            try:
                print(f"Attempting to create transaction with name: {data.get('name')}") # Added for debugging
                # Create the transaction directly
                transaction = Financials.objects.create(
                    name=data.get('name'),
                    amount=data.get('amount'),
                    type=data.get('type'),
                    description=data.get('description'),
                    source=data.get('source'),
                    admin=default_admin,
                    receipts=[]  # Initialize empty receipts list
                )
                print("Created transaction:", transaction)
                return Response(FinancialSerializer(transaction).data, status=status.HTTP_201_CREATED)
            except Exception as save_error:
                print("Error saving transaction (during creation):", str(save_error))
                import traceback
                print("Save error traceback:", traceback.format_exc())
                return Response({'error': f'Error saving transaction: {str(save_error)}'}, 
                              status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        print("Serializer errors (if not valid):", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print("General error in add_transaction view:", str(e))
        import traceback
        print("Full traceback for general error:", traceback.format_exc())
        return Response({'error': f'Server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Delete endpoint
@api_view(["POST"])
@permission_classes([AllowAny])
def del_transaction(request):
    
    transaction_id = request.data.get("id")
    transaction = Financials.objects.get(id=transaction_id)
    transaction.delete()
    return Response({"message":f"Item deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def get_statistics(request):
    try:
        year = int(request.GET.get('year', datetime.now().year))
        range_type = request.GET.get('range', 'Month')  # Month, Quarter, or Year
        
        print(f"get_statistics called: year={year}, range_type={range_type}")

        # Base queryset
        transactions = Financials.objects.filter(created_at__year=year)
        
        # Determine the truncation function based on range type
        if range_type == 'Month':
            trunc_func = TruncMonth('created_at')
            date_format = '%Y-%m'
        elif range_type == 'Quarter':
            trunc_func = TruncQuarter('created_at')
            date_format = '%Y-Q%q'
        else:  # Year
            trunc_func = TruncYear('created_at')
            date_format = '%Y'
        
        # Get income data
        income_data = transactions.filter(type='income').annotate(
            period=trunc_func
        ).values('period').annotate(
            total=Sum('amount')
        ).order_by('period')
        print("income_data:", list(income_data))

        # Get expense data
        expense_data = transactions.filter(type='expense').annotate(
            period=trunc_func
        ).values('period').annotate(
            total=Sum('amount')
        ).order_by('period')
        print("expense_data:", list(expense_data))

        # Format the data
        labels = []
        income = []
        expenses = []
        
        # Combine and sort all periods
        all_periods = sorted(set(
            [item['period'] for item in income_data] +
            [item['period'] for item in expense_data]
        ))
        print("all_periods:", all_periods)

        # Create lookup dictionaries for quick access
        income_dict = {item['period']: item['total'] for item in income_data}
        expense_dict = {item['period']: item['total'] for item in expense_data}
        
        # Build the response data
        for period in all_periods:
            formatted_label = ""
            if range_type == 'Month':
                formatted_label = period.strftime(date_format)
            elif range_type == 'Quarter':
                # period will be a date object (e.g., 2025-01-01 for Q1, 2025-04-01 for Q2)
                quarter = (period.month - 1) // 3 + 1
                formatted_label = f'{period.year}-Q{quarter}'
            else: # Year
                formatted_label = str(period.year)
            
            labels.append(formatted_label)
            income.append(float(income_dict.get(period, 0)))
            expenses.append(float(expense_dict.get(period, 0)))

        return Response({
            'labels': labels,
            'income': income,
            'expenses': expenses,
        })
    except Exception as e:
        print("Error in get_statistics:", str(e))
        import traceback
        print("Statistics error traceback:", traceback.format_exc())
        return Response({'error': f'Server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            
          