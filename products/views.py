from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from .models import Product, Category, ProductVariation, ProductImage, VariationImage
from .serializers import ProductSerializer, CategorySerializer, ProductVariationSerializer, ProductImageSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from users.models import CustomUser
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q
from association.models import Farmer
from django.core.files.base import ContentFile
from uuid import UUID
import json, uuid, base64,re

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
                print("Farmer found:", farmer.full_name)
            except (Farmer.DoesNotExist, ValueError) as e:
                print("Farmer error:", str(e))
                return Response({
                    'error': 'Invalid farmer',
                    'details': 'Farmer not found or invalid UUID',
                    'received_farmer_id': request.data.get('farmer_id')
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validate images
            if not request.FILES.getlist('prod_images'):
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
            
            variations_raw = request.data.get('variations')  # This is the raw string

            if variations_raw:
                try:
                    # Step 1: Extract image base64 data from raw string
                    image_list = []
                    cleaned_variations = []

                    # Match each variation object manually
                    variation_pattern = re.finditer(r'\{.*?\}', variations_raw)

                    for match in variation_pattern:
                        variation_str = match.group()

                        # Extract image base64 list (assuming only 1 image per variation)
                        image_match = re.search(r'"images"\s*:\s*\[\s*"([^"]+)"\s*\]', variation_str)
                        image_base64 = image_match.group(1) if image_match else None
                        image_list.append(image_base64)

                        # Remove the "images" key entirely from the string
                        cleaned_str = re.sub(r'"images"\s*:\s*\[\s*"[^"]*"\s*\],?', '', variation_str)
                        cleaned_variations.append(cleaned_str)

                    # Step 2: Parse cleaned variation JSONs
                    parsed_variations = [json.loads(v) for v in cleaned_variations]
                    var_image_file = request.FILES.getlist('var_images')

                    # Step 3: Save variations and their images
                    for idx, variation in enumerate(parsed_variations):
                        variation['product'] = product
                        created_variation = ProductVariation.objects.create(**variation)

                        try:
                            VariationImage.objects.create(
                                variation=created_variation,
                                image_file=var_image_file[idx],  # Index matches image
                                is_main=True
                            )
                        except Exception as e:
                            print(f"Image save error: {e}")

                except Exception as e:
                    print(f"Variation processing error: {e}")
                    return Response({'error': 'Invalid variation data', 'detail': str(e)}, status=400)

                # Handle images
                for index, image_file in enumerate(request.FILES.getlist('prod_images')):
                    ProductImage.objects.create(
                        product=product,
                        image_file=image_file,
                        is_main=(index == 0)
        )

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

    def patch(self, request, pk):
        print(request.data)
        product = get_object_or_404(Product, pk=pk)

        variations_data = []
        # images_data = []  # ❌ Commented: Not handling images

        # --- Handle Variations ---
        variations_raw = request.data.get('variations')
        if variations_raw:
            if isinstance(variations_raw, str):
                try:
                    parsed = json.loads(variations_raw)
                    if isinstance(parsed, list):
                        variations_data.extend([v for v in parsed if isinstance(v, dict)])
                    elif isinstance(parsed, dict):
                        variations_data.append(parsed)
                except json.JSONDecodeError:
                    pass
            elif isinstance(variations_raw, list):
                for v in variations_raw:
                    if isinstance(v, str):
                        try:
                            v = json.loads(v)
                        except json.JSONDecodeError:
                            continue
                    if isinstance(v, dict):
                        variations_data.append(v)

        # --- Handle Images (optional) ---
        # images_raw = request.data.get('images')
        # if images_raw:
        #     if isinstance(images_raw, str):
        #         try:
        #             parsed = json.loads(images_raw)
        #             if isinstance(parsed, list):
        #                 images_data.extend([img for img in parsed if isinstance(img, dict)])
        #             elif isinstance(parsed, dict):
        #                 images_data.append(parsed)
        #         except json.JSONDecodeError:
        #             pass
        #     elif isinstance(images_raw, list):
        #         for img in images_raw:
        #             if isinstance(img, str):
        #                 try:
        #                     img = json.loads(img)
        #                 except json.JSONDecodeError:
        #                     continue
        #             if isinstance(img, dict):
        #                 images_data.append(img)

        # --- Attach uploaded image files ---
        for key, file in request.FILES.items():
            if key.startswith('variations_new_image_'):
                for variation in variations_data:
                    if variation.get('image_file_key') == key:
                        variation['image'] = file
                        break
            # elif key.startswith('images_new_image_'):
            #     for image in images_data:
            #         if image.get('image_file_key') == key:
            #             image['image'] = file
            #             break

        # Remove variations/images from request.data
        mutable_data = request.data.copy()
        mutable_data.pop('variations', None)
        mutable_data.pop('images', None)

        context = {'variations': variations_data}
        # if images_data:
        #     context['images'] = images_data

        serializer = ProductSerializer(product, data=mutable_data, context=context, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        product = serializer.save()

        # --- Update or create variations ---
        current_variation_ids = set()
        for variation in variations_data:
            data = variation.copy()
            variation_id = data.pop('id', None)
            data.pop('image_file_key', None)

            if variation_id:
                try:
                    instance = ProductVariation.objects.get(id=variation_id, product=product)
                    v_serializer = ProductVariationSerializer(instance, data=data, partial=True)
                    if v_serializer.is_valid(raise_exception=True):
                        v_serializer.save()
                    current_variation_ids.add(variation_id)
                except ProductVariation.DoesNotExist:
                    v_serializer = ProductVariationSerializer(data={**data, 'product': product.id})
                    if v_serializer.is_valid(raise_exception=True):
                        new_var = v_serializer.save()
                        current_variation_ids.add(str(new_var.id))
            else:
                v_serializer = ProductVariationSerializer(data={**data, 'product': product.id})
                if v_serializer.is_valid(raise_exception=True):
                    new_var = v_serializer.save()
                    current_variation_ids.add(str(new_var.id))

        #ProductVariation.objects.filter(product=product).exclude(id__in=current_variation_ids).delete()

        # --- Update or create images (disabled) ---
        # if images_data:
        #     current_image_ids = set()
        #     for image in images_data:
        #         data = image.copy()
        #         image_id = data.pop('id', None)
        #         image_file = data.get('image')
        #         is_file = isinstance(image_file, (InMemoryUploadedFile, UploadedFile))

        #         if image_id:
        #             try:
        #                 instance = ProductImage.objects.get(id=image_id, product=product)
        #                 if not is_file:
        #                     data.pop('image', None)
        #                 i_serializer = ProductImageSerializer(instance, data=data, partial=True)
        #                 if i_serializer.is_valid(raise_exception=True):
        #                     i_serializer.save()
        #                 current_image_ids.add(image_id)
        #             except ProductImage.DoesNotExist:
        #                 if is_file:
        #                     i_serializer = ProductImageSerializer(data={**data, 'product': product.id})
        #                     if i_serializer.is_valid(raise_exception=True):
        #                         new_img = i_serializer.save()
        #                         current_image_ids.add(str(new_img.id))
        #         else:
        #             if is_file:
        #                 i_serializer = ProductImageSerializer(data={**data, 'product': product.id})
        #                 if i_serializer.is_valid(raise_exception=True):
        #                     new_img = i_serializer.save()
        #                     current_image_ids.add(str(new_img.id))

        #     ProductImage.objects.filter(product=product).exclude(id__in=current_image_ids).delete()

        return Response(ProductSerializer(product).data)


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
    