from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from .models import Product, Category, ProductVariation, ProductImage
from .serializers import ProductSerializer, CategorySerializer, ProductVariationSerializer, ProductImageSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from users.models import CustomUser
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q
from association.models import Farmer
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
        search = request.query_params.get('search', None)
        summarize = request.query_params.get('summarize', 'false').lower() == 'true'
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 7))
        
        print(f"[Backend Log] Received category: {category}, search: {search}")

        # Start with all products
        products = Product.objects.all()
        print(f"[Backend Log] Products before filtering: {products.count()}")

        # Apply filters
        if user_id:
            products = products.filter(vendor__id=user_id)
        
        if status and status in self.VALID_STATUSES:
            products = products.filter(status=status)
            
        if category:
            products = products.filter(category__name=category)
            print(f"[Backend Log] Products after category filter: {products.count()}")
            
        if search:
            # Query the related UserProfile model for the full_name
            products = products.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(category__name__icontains=search) |
                Q(vendor__profile__full_name__icontains=search)
            )
            print(f"[Backend Log] Products after search filter: {products.count()}")

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
            required_fields = ['name', 'description', 'category', 'vendor_id']
            missing_fields = [
                field for field in required_fields 
                if field not in request.data or not str(request.data.get(field)).strip()
            ]
            if missing_fields:
                print("Missing required fields:", missing_fields)
                return Response({
                    'error': 'Missing required fields',
                    'details': f'Required fields missing: {", ".join(missing_fields)}',
                    'received_data': {k: v for k, v in request.data.items() if k in required_fields}
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validate category
            try:
                category = Category.objects.get(id=request.data['category'])
                print("Category found:", category.name)
            except (Category.DoesNotExist, ValueError) as e:
                print("Category error:", str(e))
                return Response({
                    'error': 'Invalid category',
                    'details': 'Category not found or invalid UUID',
                    'received_category': request.data.get('category')
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get vendor
            try:
                vendor = CustomUser.objects.get(id=request.data['vendor_id'])
                print("Vendor found:", vendor.username)
            except (CustomUser.DoesNotExist, ValueError) as e:
                print("Vendor error:", str(e))
                return Response({
                    'error': 'Invalid vendor',
                    'details': 'Vendor not found or invalid UUID',
                    'received_vendor_id': request.data.get('vendor_id')
                }, status=status.HTTP_400_BAD_REQUEST)
                
                # Get farmer
            try:
                farmer = Farmer.objects.get(id=request.data['farmer_id'])
                print("Vendor found:", farmer.full_name)
            except (Farmer.DoesNotExist, ValueError) as e:
                print("Vendor error:", str(e))
                return Response({
                    'error': 'Invalid farmer',
                    'details': 'Farmer not found or invalid UUID',
                    'received_farmer_id': request.data.get('farmer_id')
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validate images
            if not request.FILES.getlist('images'):
                return Response({
                    'error': 'Missing images',
                    'details': 'At least one image is required'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Prepare product data
            product_data = {
                'name': request.data['name'].strip(),
                'description': request.data['description'].strip(),
                'category': category,
                'vendor': vendor,
                'status': 'published',
                'farmer': farmer
            }


            # Add farmer_id if provided
            if request.data.get('farmer_id'):
                product_data['farmer_id'] = request.data['farmer_id'].strip()

            # Create product
            product = Product.objects.create(**product_data)
            print("Product created:", product.name)

            # Handle variations
            variations_data = request.data.get('variations')
            if variations_data:
                try:
                    variations = json.loads(variations_data)
                    for variation in variations:
                        variation['product'] = product
                        ProductVariation.objects.create(**variation)
                except json.JSONDecodeError:
                    print("Invalid variations JSON")
                    return Response({
                        'error': 'Invalid variations data',
                        'details': 'Variations data must be valid JSON'
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Handle images
            for image_file in request.FILES.getlist('images'):
                ProductImage.objects.create(product=product, image_file=image_file)

            # Serialize and return response
            serializer = ProductSerializer(product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print("Unexpected error:", str(e))
            return Response({
                'error': 'Server error',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# UPDATE an existing product
class UpdateProduct(APIView):
    permission_classes = [AllowAny]
    
    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        
        # Prepare data for serializer - request.data will be a QueryDict for multipart/form-data
        # We need to handle variations and images specially as they are stringified JSON arrays

        variations_data = []
        variations_raw = request.data.get('variations')
        if variations_raw:
            if isinstance(variations_raw, str):
                try:
                    parsed_variations = json.loads(variations_raw)
                    if isinstance(parsed_variations, list):
                        for item in parsed_variations:
                            if isinstance(item, dict):
                                variations_data.append(item)
                    elif isinstance(parsed_variations, dict):
                        variations_data.append(parsed_variations)
                except json.JSONDecodeError:
                    pass
            elif isinstance(variations_raw, list):
                for item in variations_raw:
                    if isinstance(item, str):
                        try:
                            parsed_item = json.loads(item)
                            if isinstance(parsed_item, dict):
                                variations_data.append(parsed_item)
                        except json.JSONDecodeError:
                            pass
                    elif isinstance(item, dict):
                        variations_data.append(item)

        images_data = []
        images_raw = request.data.get('images')
        if images_raw:
            if isinstance(images_raw, str):
                try:
                    parsed_images = json.loads(images_raw)
                    if isinstance(parsed_images, list):
                        for item in parsed_images:
                            if isinstance(item, dict):
                                images_data.append(item)
                    elif isinstance(parsed_images, dict):
                        images_data.append(parsed_images)
                except json.JSONDecodeError:
                    pass
            elif isinstance(images_raw, list):
                for item in images_raw:
                    if isinstance(item, str):
                        try:
                            parsed_item = json.loads(item)
                            if isinstance(parsed_item, dict):
                                images_data.append(parsed_item)
                        except json.JSONDecodeError:
                            pass
                    elif isinstance(item, dict):
                        images_data.append(item)
        
        # Handle new image files from request.FILES and attach them to the correct variation/image data
        for key, file in request.FILES.items():
            if key.startswith('variations_new_image_'):
                for variation in variations_data:
                    if variation.get('image_file_key') == key:
                        variation['image'] = file
                        break
            elif key.startswith('images_new_image_'):
                for image_item in images_data:
                    if image_item.get('image_file_key') == key:
                        image_item['image'] = file
                        break

        # Create a mutable copy of request.data for top-level fields for the serializer
        mutable_data = request.data.copy()
        # Remove variations and images from mutable_data as they are handled via context
        mutable_data.pop('variations', None)
        mutable_data.pop('images', None)

        print(f"[Debug] Full request.data: {request.data}")
        print(f"[Debug] Variations data before serializer: {variations_data}")
        print(f"[Debug] Type of variations_data: {type(variations_data)}")
        print(f"[Debug] Images data before serializer: {images_data}")
        print(f"[Debug] Type of images_data: {type(images_data)}")

        serializer = ProductSerializer(
            product,
            data=mutable_data,
            context={'variations': variations_data, 'images': images_data},
            partial=True
        )
        
        print(f"[Debug] Is serializer valid? {serializer.is_valid()}")
        if serializer.is_valid():
            print("[Debug] Serializer is valid, saving product.")
            product = serializer.save()

            # Handle variations: update existing, create new, delete removed
            current_variation_ids = set()
            for variation_data_raw in variations_data:
                variation_data = variation_data_raw.copy()  # Make a copy to modify
                variation_id = variation_data.pop('id', None)  # Pop id for update/create logic
                variation_data.pop('image_file_key', None)  # Remove image_file_key (if present from frontend)

                if variation_id:
                    try:
                        variation = ProductVariation.objects.get(id=variation_id, product=product)
                        variation_serializer = ProductVariationSerializer(instance=variation, data=variation_data, partial=True)
                        if variation_serializer.is_valid(raise_exception=True):
                            variation_serializer.save()
                        current_variation_ids.add(variation_id)
                    except ProductVariation.DoesNotExist:
                        print(f"Warning: Variation with ID {variation_id} not found for product {product.id}. Creating as new.")
                        variation_serializer = ProductVariationSerializer(data={**variation_data, 'product': product.id})
                        if variation_serializer.is_valid(raise_exception=True):
                            new_variation = variation_serializer.save()
                            current_variation_ids.add(str(new_variation.id))
                else:
                    variation_serializer = ProductVariationSerializer(data={**variation_data, 'product': product.id})
                    if variation_serializer.is_valid(raise_exception=True):
                        new_variation = variation_serializer.save()
                        current_variation_ids.add(str(new_variation.id))

            # Delete variations that were not in the updated data
            ProductVariation.objects.filter(product=product).exclude(id__in=list(current_variation_ids)).delete()

            # Handle images: update existing, create new, delete removed
            current_image_ids = set()
            for image_data_raw in images_data:
                image_data = image_data_raw.copy()
                image_id = image_data.pop('id', None)
                
                # Check if the 'image' field is a file object (new upload) or a URL string (existing)
                image_is_file = isinstance(image_data.get('image'), (InMemoryUploadedFile, UploadedFile))

                if image_id:
                    try:
                        image_instance = ProductImage.objects.get(id=image_id, product=product)
                        
                        serializer_data = image_data.copy()  # Start with all data
                        
                        if not image_is_file:  # If it's not a file (it's a URL string), remove the image field from data for partial update
                            serializer_data.pop('image', None)
                        
                        image_serializer = ProductImageSerializer(instance=image_instance, data=serializer_data, partial=True)
                        if image_serializer.is_valid(raise_exception=True):
                            image_serializer.save()
                        current_image_ids.add(image_id)
                    except ProductImage.DoesNotExist:
                        print(f"Warning: Image with ID {image_id} not found for product {product.id}. Creating as new.")
                        if image_is_file:  # Only create as new if there's a file to upload
                            image_serializer = ProductImageSerializer(data={**image_data, 'product': product.id})
                            if image_serializer.is_valid(raise_exception=True):
                                new_image = image_serializer.save()
                                current_image_ids.add(str(new_image.id))
                else:
                    # Create new image only if image_is_file is True (it's a new file upload)
                    if image_is_file:
                        image_serializer = ProductImageSerializer(data={**image_data, 'product': product.id})
                        if image_serializer.is_valid(raise_exception=True):
                            new_image = image_serializer.save()
                            current_image_ids.add(str(new_image.id))

            ProductImage.objects.filter(product=product).exclude(id__in=list(current_image_ids)).delete()

            return Response(ProductSerializer(product).data)
        else:
            print("[Debug] Serializer is NOT valid.")
            print("Serializer errors:", serializer.errors)
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

class BatchDeleteProducts(APIView):
    permission_classes = [AllowAny]

    def delete(self, request):
        try:
            print("\n=== Batch Delete Request ===")
            print("Query params:", request.query_params)

            # Get product IDs from query parameters (list of IDs)
            product_ids = request.query_params.getlist('product_ids')
            if not product_ids:
                return Response({
                    'error': 'No products selected',
                    'details': 'Please select at least one product to delete'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Convert string IDs to UUID objects
            try:
                conv_product_ids = [UUID(str(id)) for id in product_ids]
                print("Converted UUIDs:", conv_product_ids)
            except ValueError as e:
                return Response({
                    'error': 'Invalid product ID',
                    'details': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get all matching products
            products = Product.objects.filter(id__in=conv_product_ids)
            print("Found products:", products.count())

            deleted_count = 0
            failed_deletions = []

            for product in products:
                try:
                    # Delete associated variations and images
                    ProductVariation.objects.filter(product=product).delete()
                    ProductImage.objects.filter(product=product).delete()
                    product.delete()
                    deleted_count += 1
                except Exception as e:
                    print(f"Failed to delete product {product.id}:", str(e))
                    failed_deletions.append(str(product.id))

            response_data = {
                'message': f'Successfully deleted {deleted_count} products',
                'deleted_count': deleted_count
            }

            if failed_deletions:
                response_data['warning'] = f'Failed to delete {len(failed_deletions)} products due to database constraints'
                response_data['failed_ids'] = failed_deletions

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print("Error in batch delete:", str(e))
            import traceback
            print("Traceback:", traceback.format_exc())
            return Response({
                'error': 'Failed to delete products',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    