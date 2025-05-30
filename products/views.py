from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from users.models import CustomUser
from rest_framework.decorators import api_view, permission_classes

# GET all products
class GetProducts(APIView):
    permission_classes = [AllowAny]
    VALID_STATUSES = {
        'published', 'out_of_stock', 'hidden', 'pending_approval', 'rejected'
    }

    def get(self, request):
        user_id = request.query_params.get('user_id')
        status = request.query_params.get('status')

      
        products = Product.objects.all()

        if user_id:
            products = products.filter(vendor__id=user_id)

       
        if status and status in self.VALID_STATUSES:
            products = products.filter(status=status)
            print("Here")

        print(status)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
# ADD a new product
class AddProduct(APIView):
    permission_classes = [AllowAny]  # Currently, no authentication, anyone can access

    def post(self, request):
        # Get the vendor (user) from request body or pass it directly as a parameter
        vendor_id = str(request.data.get('vendor', None))  # Expecting 'vendor' field in the request body
        if vendor_id:
            try:
                vendor = CustomUser.objects.get(id=vendor_id)
            except CustomUser.DoesNotExist:
                return Response({"error": "Vendor not found"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Vendor not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Create the product 
        serializer = ProductSerializer(data=request.data)
        
        if serializer.is_valid():

            serializer.save()  # Save the product

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# UPDATE an existing product
class UpdateProduct(APIView):
    permission_classes = [AllowAny]
    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        # Optional: Ensure that only the vendor who owns the product can update it
        # if product.vendor != request.user:
        #     return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProductSerializer(product, data=request.data, partial=True)  # partial=True means PATCH-like
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AcceptProduct(APIView):
    permission_classes = [AllowAny]

    def patch(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        # Extract only allowed fields from request data
        allowed_fields = {'status'}
        data = {key: value for key, value in request.data.items() if key in allowed_fields}

        if not data:
            return Response({'detail': 'No valid fields to update.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductSerializer(product, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# DELETE a product
class DeleteProduct(APIView):
    permission_classes = [AllowAny]
    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        # Optional: Only the vendor who owns it can delete
        # if product.vendor != request.user:
        #    return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

        product.delete()
        return Response({'detail': 'Product deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]  # Adjust for your needs
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            "message": "Category created successfully.",
            "data": response.data
        }, status=response.status_code)

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        return Response({
            "message": "Category updated successfully.",
            "data": response.data
        }, status=response.status_code)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'detail': f'Category {instance.name} deleted successfully.'}, status=status.HTTP_200_OK)
    
    
    
    
    