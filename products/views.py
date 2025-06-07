from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from .models import Product, Category, ProductVariation, ProductImage
from .serializers import ProductSerializer, CategorySerializer, ProductVariationSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from users.models import CustomUser
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q
import json
from uuid import UUID

# GET all products
class GetProducts(APIView):
    permission_classes = [AllowAny]
    VALID_STATUSES = {
        'published', 'out_of_stock', 'hidden', 'pending_approval', 'rejected'
    }

    def get(self, request):
        # Get query parameters
        user_id = request.query_params.get('user_id')
        status = request.query_params.get('status')
        category = request.query_params.get('category')
        search = request.query_params.get('search')
        summarize = request.query_params.get('summarize', 'false').lower() == 'true'
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 7))
        
        # Start with all products
        products = Product.objects.all()

        # Apply filters
        if user_id:
            products = products.filter(vendor__id=user_id)
        
        if status and status in self.VALID_STATUSES:
            products = products.filter(status=status)
            
        if category:
            products = products.filter(category__name=category)
            
        if search:
            products = products.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(vendor__get_full_name__icontains=search)
            )

        # Calculate pagination ONLY if not in summarize mode
        if not summarize:
            total = products.count()
            start = (page - 1) * per_page
            end = start + per_page

            products = products[start:end]
        else: # If in summarize mode, get all products and return simplified response
            total = products.count()

        # Serialize data
        serializer = ProductSerializer(products, many=True)

        if summarize: # Simplified response for summary data
            return Response({
                'products': serializer.data,
                'total': total,
            })
        else: # Full response for paginated data
            return Response({
                'products': serializer.data,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            })

# ADD a new product
class AddProduct(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            print("\n=== Product Creation Request ===")
            print("Request data:", request.data)
            print("Request files:", request.FILES)
            
            # Validate required fields
            required_fields = ['name', 'description', 'category']
            missing_fields = [
                field for field in required_fields 
                if field not in request.data or not str(request.data.get(field)).strip()
            ]
            if missing_fields:
                print("Missing required fields:", missing_fields)
                return Response({
                    'error': 'Missing required fields',
                    'missing_fields': missing_fields
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validate category
            try:
                category = Category.objects.get(id=request.data['category'])
                print("Category found:", category.name)
            except (Category.DoesNotExist, ValueError):
                print("Invalid category ID:", request.data['category'])
                return Response({
                    'error': 'Invalid category',
                    'details': 'Category not found or invalid UUID'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Prepare product data
            product_data = {
                'name': request.data['name'].strip(),
                'description': request.data['description'].strip(),
                'category': category.id,
                'status': 'pending_approval',
                'is_available': True,
                'vendor': UUID('d3004d02-d2f7-4980-968b-860691790486')
            }

            # Add farmer_code if provided
            if request.data.get('farmer_code'):
                product_data['farmer_code'] = request.data['farmer_code'].strip()

            print("Creating product with data:", product_data)

            # Create product
            serializer = ProductSerializer(data=product_data)
            if not serializer.is_valid():
                print("Serializer validation errors:", serializer.errors)
                return Response({
                    'error': 'Validation error',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            print("Before serializer.save() - product_data being sent:", product_data)
            product = serializer.save()
            print("After serializer.save() - product status:", product.status)
            print("Product created successfully with ID:", product.id)

            # Handle images
            images = request.FILES.getlist('images')
            images_data = request.data.get('images', [])
            
            # If no files uploaded but we have image data
            if not images and images_data:
                try:
                    # Handle image data from request
                    for image_data in images_data:
                        if isinstance(image_data, dict) and 'image' in image_data:
                            # Create ProductImage with the provided URL
                            ProductImage.objects.create(
                                product=product,
                                image=image_data['image'],
                                is_main=image_data.get('is_main', False)
                            )
                    print(f"Created {len(images_data)} product images from data")
                except Exception as e:
                    print("Error creating images from data:", str(e))
                    return Response({
                        'error': 'Error creating images',
                        'details': str(e)
                    }, status=status.HTTP_400_BAD_REQUEST)
            # Handle file uploads
            elif images:
                for image in images:
                    ProductImage.objects.create(product=product, image=image)
                print(f"Created {len(images)} product images from files")
            else:
                print("No images provided")
                return Response({
                    'error': 'No images provided',
                    'details': 'At least one image is required'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Handle variations if provided
            variations_data = request.data.get('variations', [])
            print("Received variations data:", variations_data)
            if variations_data:
                try:
                    variations = json.loads(variations_data) if isinstance(variations_data, str) else variations_data
                    print("Parsed variations:", variations)
                    if not isinstance(variations, list):
                        print("Invalid variations format - not a list")
                        return Response({
                            'error': 'Invalid variations format',
                            'details': 'Variations must be a list'
                        }, status=status.HTTP_400_BAD_REQUEST)

                    for variation in variations:
                        variation['product'] = product.id
                        variation_serializer = ProductVariationSerializer(data=variation)
                        if variation_serializer.is_valid():
                            variation_serializer.save()
                            print(f"Created variation: {variation.get('name')}")
                        else:
                            print("Variation validation errors:", variation_serializer.errors)
                            return Response({
                                'error': 'Invalid variation data',
                                'details': variation_serializer.errors
                            }, status=status.HTTP_400_BAD_REQUEST)
                except json.JSONDecodeError:
                    print("Failed to parse variations JSON")
                    return Response({
                        'error': 'Invalid variations format',
                        'details': 'Could not parse variations JSON'
                    }, status=status.HTTP_400_BAD_REQUEST)

            print("=== Product Creation Complete ===\n")
            return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print("Error creating product:", str(e))
            print("Exception type:", type(e).__name__)
            import traceback
            print("Traceback:", traceback.format_exc())
            return Response({
                'error': 'Server error',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# UPDATE an existing product
class UpdateProduct(APIView):
    permission_classes = [AllowAny]
    
    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        
        # Extract variations and images from request data
        variations_data = request.data.pop('variations', [])
        images_data = request.data.pop('images', [])
        
        serializer = ProductSerializer(
            product,
            data=request.data,
            context={'variations': variations_data, 'images': images_data},
            partial=True
        )
        
        if serializer.is_valid():
            product = serializer.save()
            return Response(ProductSerializer(product).data)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AcceptProduct(APIView):
    permission_classes = [AllowAny]

    def patch(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        
        allowed_fields = {'status'}
        data = {key: value for key, value in request.data.items() if key in allowed_fields}
        
        if not data:
            return Response({'detail': 'No valid fields to update.'}, status=status.HTTP_400_BAD_REQUEST)
            
        serializer = ProductSerializer(product, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# DELETE a product
class DeleteProduct(APIView):
    permission_classes = [AllowAny]
    
    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Batch delete products
class BatchDeleteProducts(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        product_ids = request.data.get('ids', [])
        if not product_ids:
            return Response(
                {"error": "No product IDs provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Delete products
        deleted_count = Product.objects.filter(id__in=product_ids).delete()[0]
        
        return Response({
            "message": f"Successfully deleted {deleted_count} products",
            "deleted_count": deleted_count
        })

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        print("Fetching categories...")
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        print("Categories found:", len(queryset))
        return Response(serializer.data)

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
        return Response({
            'detail': f'Category {instance.name} deleted successfully.'
        }, status=status.HTTP_200_OK)
    
    
    
    
    