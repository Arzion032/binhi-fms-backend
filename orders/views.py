from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from collections import defaultdict
from products.models import ProductVariation
from orders.serializers import OrderSerializer
from .models import Order, OrderItem, OrderStatusHistory, MarketTransaction
from users.models import CustomUser  
from uuid import UUID
import json
from rest_framework import viewsets
from rest_framework.decorators import action
from django.db.models import Count
from .serializers import OrderItemSerializer, OrderStatusHistorySerializer, MarketTransactionSerializer

class ConfirmCheckoutView(APIView):
    permission_classes = [AllowAny]
    
    @transaction.atomic
    def post(self, request):
        data = request.data
        buyer = request.user

        variation_ids = data.get("variation_ids", [])
        shipping_address = data.get("shipping_address")
        payment_method = data.get("payment_method")
        delivery_method = data.get("delivery_method")

        if not variation_ids or not shipping_address or not payment_method:
            return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

        cart = Cart.objects.get(user=buyer)
        cart_items = CartItem.objects.select_related('variation__product__vendor').filter(
            cart=cart,
            variation_id__in=variation_ids
        )

        # Log incoming data for debugging
        print("Variation IDs:", variation_ids)
        cart_variation_ids = cart_items.values_list('variation_id', flat=True)
        print("Cart Items Variation IDs:", cart_variation_ids)
        
        # Convert only the variation_ids to UUID, if they are not already UUIDs
        variation_ids = [UUID(v) if not isinstance(v, UUID) else v for v in variation_ids]

        # Cart items' variation IDs are already UUIDs, no need to convert them again
        cart_variation_ids = cart_items.values_list('variation_id', flat=True)

        # Now compare both as UUIDs
        missing_variations = [v for v in variation_ids if v not in cart_variation_ids]
        print("Missing Variations:", missing_variations)

        if missing_variations:
            return Response({"error": f"Variation(s) {missing_variations} are not in the cart."}, status=status.HTTP_400_BAD_REQUEST)

        print("this loop1")
        # Group cart items by vendor
        vendor_items = defaultdict(list)
        for item in cart_items:
            vendor_items[item.variation.product.vendor].append(item)

        order_ids = []
        response_orders = []

        print("this loop2")
        # Each vendor gets their own order
        for vendor, items in vendor_items.items():
            order_total = 0
            # Calculate total for this vendor's order
            for item in items:
                if item.variation.stock < item.quantity:
                    return Response({"error": f"Not enough stock for {item.variation.name}."}, status=status.HTTP_400_BAD_REQUEST)
                order_total += item.quantity * item.variation.unit_price

            print("order")
            # Create the order
            order = Order.objects.create(
                buyer=buyer,
                status='pending',
                total_price=order_total,
                shipping_address=shipping_address,
                payment_method=payment_method,
                delivery_method=delivery_method
            )

            print("order stats")
            # Status history
            OrderStatusHistory.objects.create(
                order=order, 
                status='pending'
            )

            # Create OrderItems, update stock
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    variation=item.variation,
                    quantity=item.quantity,
                    unit_price=item.variation.unit_price
                )
                # Decrement product stock
                item.variation.stock -= item.quantity
                if item.variation.stock <= 0:
                    item.variation.status = 'out_of_stock'
                    item.variation.is_available = False
                item.variation.save()
                
            print("market trans")
            # Create transaction (per vendor)
            MarketTransaction.objects.create(
                order=order,
                buyer=buyer,
                seller=vendor,
                payment_method=payment_method,
                total_amount=order_total,
                status='pending'
            )

            # Prepare response
            response_orders.append({
                "order_id": order.id,
                "vendor": vendor.username,
                "order_total": order_total
            })

            order_ids.append(order.id)

        # Remove these items from cart
        print("Cart items to be deleted:", cart_items)

        cart_items.delete()

        return Response({
            "message": "Orders created successfully.",
            "orders": response_orders
        }, status=status.HTTP_201_CREATED)
        
class OrderHistoryView(APIView):
    def get(self, request):
        if not request.user.is_authenticated or request.user.is_superuser:
            orders = Order.objects.all().order_by('-created_at')
        else:
            orders = Order.objects.filter(buyer=request.user).order_by('-created_at')

        serializer = OrderSerializer(orders, many=True)
        order_history = []
        for order in serializer.data:
            # Defensive: items list could be empty
            items = order.get("items", [])
            first_item = items[0] if items else {}
            product = first_item.get("product", {}) if isinstance(first_item.get("product", {}), dict) else {}

            product_info = {
                "name": product.get("name", ""),
                "variation": first_item.get("variation", ""),
                "image": product.get("image", ""),
            }
            order_data = {
                'id': order['id'],
                'orderId': order['order_identifier'],
                'status': order['status'],
                'total_price': order['total_price'],
                'shipping_address': order['shipping_address'],
                'payment_method': order['payment_method'],
                'orderDate': order['created_at'],
                'items': items,
                'product': product_info,  # always present!
                'sellerName': '',
                'sellerProfile': '',
                'deliveryAddress': {
                    'name': order['shipping_address'],
                    'phone': '',
                    'address': order['shipping_address'],
                },
                'payment_status': order.get('payment_status', 'Pending'),
            }
            order_history.append(order_data)

        # Debug print to confirm
        import pprint
        pprint.pprint(order_history)
        return Response(order_history)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.all()
        search = self.request.query_params.get('search', None)
        status = self.request.query_params.get('status', None)
        
        if search:
            queryset = queryset.filter(
                order_identifier__icontains=search
            ) | queryset.filter(
                buyer__username__icontains=search
            ) | queryset.filter(
                items__variation__product__name__icontains=search
            ).distinct()
            
        if status:
            queryset = queryset.filter(status=status.lower())
            
        return queryset.select_related('buyer').prefetch_related(
            'items__variation__product',
            'transaction'
        )

    @action(detail=False, methods=['get'])
    def status_counts(self, request):
        counts = Order.objects.values('status').annotate(
            count=Count('id')
        )
        return Response({
            status['status']: status['count'] 
            for status in counts
        })

    @action(detail=False, methods=['get'])
    def list_orders(self, request):
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 7))
        
        queryset = self.get_queryset()
        total = queryset.count()
        
        start = (page - 1) * per_page
        end = start + per_page
        
        orders = queryset[start:end]
        
        # Format orders to match frontend structure
        formatted_orders = []
        for order in orders:
            # Get the first item for product info
            first_item = order.items.first()
            if first_item:
                product_name = first_item.variation.product.name
                variation = first_item.variation.name
            else:
                product_name = "N/A"
                variation = "N/A"
                
            # Get transaction status
            transaction_status = "Pending"
            if hasattr(order, 'transaction'):
                if order.transaction.status == 'completed':
                    transaction_status = "Paid"
                elif order.transaction.status == 'refunded':
                    transaction_status = "Refunded"
            
            formatted_order = {
                'id': f"#{order.order_identifier}",
                'customer': {
                    'name': order.buyer.get_full_name() or order.buyer.username,
                    'email': order.buyer.email,
                    'avatar': order.buyer.profile.avatar.url if hasattr(order.buyer, 'profile') else "/sampleproduct.png",
                    'address': order.shipping_address,
                    'contact': order.buyer.profile.phone if hasattr(order.buyer, 'profile') else "N/A"
                },
                'product': {
                    'name': product_name,
                    'variation': variation
                },
                'date': order.created_at.strftime("%d %b %Y"),
                'time': order.created_at.strftime("%I:%M:%S %p"),
                'status': order.status.capitalize(),
                'transaction': transaction_status
            }
            formatted_orders.append(formatted_order)
            
        return Response({
            'orders': formatted_orders,
            'total': total,
            'page': page,
            'per_page': per_page
        })

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        order_ids = request.data.get('order_ids', [])
        if not order_ids:
            return Response(
                {'error': 'No order IDs provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Delete orders and their related objects
            Order.objects.filter(order_identifier__in=order_ids).delete()
            return Response({'message': 'Orders deleted successfully'})
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def status_categories(self, request):
        """Return status categories with their styling information"""
        status_categories = [
            {
                'name': status[1],  # Display name
                'value': status[0],  # Database value
                'count': Order.objects.filter(status=status[0]).count(),
                'color': self._get_status_color(status[0]),
                'border': self._get_status_border(status[0])
            }
            for status in Order.STATUS_CHOICES
        ]
        return Response(status_categories)

    def _get_status_color(self, status):
        """Helper method to get color for status"""
        colors = {
            'pending': "#757575",
            'confirmed': "#15803D",
            'processing': "#2563EB",
            'shipped': "#7C3AED",
            'delivered': "#15803D",
            'cancelled': "#DC2626",
            'returned': "#F59E42"
        }
        return colors.get(status, "#757575")

    def _get_status_border(self, status):
        """Helper method to get border color for status"""
        borders = {
            'pending': "#D4D4D8",
            'confirmed': "#4CAE4F",
            'processing': "#2563EB",
            'shipped': "#5E35B1",
            'delivered': "#26A69A",
            'cancelled': "#DC2626",
            'returned': "#FB8C00"
        }
        return borders.get(status, "#D4D4D8")

    @action(detail=False, methods=['get'])
    def badge_styles(self, request):
        """Return badge styles for all possible statuses"""
        styles = {
            status[1]: {
                'color': self._get_status_color(status[0]),
                'background': self._get_status_background(status[0]),
                'border': self._get_status_border(status[0])
            }
            for status in Order.STATUS_CHOICES
        }
        # Add transaction status styles
        styles.update({
            'Paid': {
                'color': "#16A34A",
                'background': "#D1FAE5",
                'border': "#16A34A"
            },
            'Refunded': {
                'color': "#F59E42",
                'background': "#FEF3C7",
                'border': "#F59E42"
            }
        })
        return Response(styles)

    def _get_status_background(self, status):
        """Helper method to get background color for status"""
        backgrounds = {
            'pending': "#E5E7EB",
            'confirmed': "#D1FAE5",
            'processing': "#DBEAFE",
            'shipped': "#EDE9FE",
            'delivered': "#D1FAE5",
            'cancelled': "#FEE2E2",
            'returned': "#FEF3C7"
        }
        return backgrounds.get(status, "#E5E7EB")

# ---- PATCH APIs for Order and Transaction Status ----

class OrderStatusPatchView(APIView):
    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        payment_status = request.data.get('payment_status')

        updated = False

        if new_status and new_status.lower() in dict(Order.STATUS_CHOICES):
            if order.status != new_status:
                order.status = new_status
                updated = True

        # PATCH the payment_status in related transaction if it exists
        if payment_status and hasattr(order, 'transaction') and order.transaction:
            if order.transaction.status != payment_status:
                order.transaction.status = payment_status
                order.transaction.save()
                updated = True

        if updated:
            order.save()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MarketTransactionStatusPatchView(APIView):
    permission_classes = [AllowAny]

    def patch(self, request, pk):
        try:
            txn = MarketTransaction.objects.get(pk=pk)
        except MarketTransaction.DoesNotExist:
            return Response({'error': 'Transaction not found.'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        if new_status not in dict(MarketTransaction.STATUS_CHOICES):
            return Response({'error': 'Invalid status value.'}, status=status.HTTP_400_BAD_REQUEST)

        if txn.status != new_status:
            txn.status = new_status
            # Set ended_at if final status
            if new_status in ['completed', 'failed', 'refunded']:
                from django.utils import timezone
                txn.ended_at = timezone.now()
            txn.save()

        serializer = MarketTransactionSerializer(txn)
        return Response(serializer.data, status=status.HTTP_200_OK)
