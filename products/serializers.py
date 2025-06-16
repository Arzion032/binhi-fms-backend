from rest_framework import serializers, viewsets
from .models import Category, Product, ProductImage, Review, ProductVariation, VariationImage
from users.models import CustomUser 
from django.utils.text import slugify
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['id', 'slug']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_main', 'uploaded_at']
        

class VariationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariationImage
        fields = ['id', 'image', 'is_main', 'uploaded_at']

class ProductVariationSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=True)
    images = VariationImageSerializer(many=True, required=False)
    
    class Meta:
        model = ProductVariation
        fields = ['id', 'name', 'images', 'unit_price', 'stock', 'unit_measurement', 'is_available', 'is_default', 'product']
        read_only_fields = ['id']

    def validate(self, data):
        # Validate uniqueness of the name for the given product
        if self.instance:
            # For updates, check if name is being changed
            if 'name' in data and data['name'] != self.instance.name:
                if ProductVariation.objects.filter(
                    product=self.instance.product,
                    name=data['name']
                ).exclude(id=self.instance.id).exists():
                    raise serializers.ValidationError({
                        'name': 'A variation with this name already exists for this product.'
                    })
        else:
            # For new variations, check if name already exists for the product
            if 'product' in data and 'name' in data:
                if ProductVariation.objects.filter(
                    product=data['product'],
                    name=data['name']
                ).exists():
                    raise serializers.ValidationError({
                        'name': 'A variation with this name already exists for this product.'
                    })
        return data

    def update(self, instance, validated_data):
        # Handle updating the variation fields
        images_data = validated_data.pop('images', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle images: update existing, create new, and delete removed images
        current_image_ids = set()
        for image_data in images_data:
            image_id = image_data.get('id', None)
            if image_id:
                try:
                    image_instance = VariationImage.objects.get(id=image_id, variation=instance)
                    image_serializer = VariationImageSerializer(image_instance, data=image_data, partial=True)
                    if image_serializer.is_valid(raise_exception=True):
                        image_serializer.save()
                    current_image_ids.add(image_id)
                except VariationImage.DoesNotExist:
                    # If the image doesn't exist, create it as a new image
                    image_serializer = VariationImageSerializer(data={**image_data, 'variation': instance.id})
                    if image_serializer.is_valid(raise_exception=True):
                        image_serializer.save()
                    current_image_ids.add(str(image_serializer.instance.id))
            else:
                # Create new image if no id is provided (means it's a new image)
                image_serializer = VariationImageSerializer(data={**image_data, 'variation': instance.id})
                if image_serializer.is_valid(raise_exception=True):
                    image_serializer.save()
                    current_image_ids.add(str(image_serializer.instance.id))

        # Delete images that are no longer associated with the variation
        VariationImage.objects.filter(variation=instance).exclude(id__in=list(current_image_ids)).delete()

        return instance


class ReviewSerializer(serializers.ModelSerializer):
    buyer_username = serializers.ReadOnlyField(source='buyer.username')

    class Meta:
        model = Review
        fields = [
            'id', 'product', 'buyer', 'buyer_username',
            'rating', 'comment', 'created_at', 'updated_at'
        ]

class ProductSerializer(serializers.ModelSerializer):
    variations = ProductVariationSerializer(many=True, required=False)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False, allow_null=True)
    images = ProductImageSerializer(many=True, required=False)
    category_name = serializers.ReadOnlyField(source='category.name')
    vendor_name = serializers.ReadOnlyField(source='vendor.username')
    vendor_code = serializers.ReadOnlyField(source='vendor.id')
    association = serializers.ReadOnlyField(source='vendor.association.name')
    association_id = serializers.ReadOnlyField(source='vendor.association.id')
    farmer_id = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'category', 'category_name',
            'vendor', 'vendor_name', 'vendor_code', 'association', 'association_id',
            'status', 'is_available',
            'created_at', 'updated_at', 'variations', 'images', 'farmer', 'farmer_id'

        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'vendor', 'vendor_name', 'vendor_code', 'association', 'association_id', 'category_name']

    def create(self, validated_data):
        variations_data = self.context.get('variations', [])
        images_data = self.context.get('images', [])
        
        # Remove variations from validated_data if present
        validated_data.pop('variations', None)
        
        product = Product.objects.create(**validated_data)
        
        # Create variations
        for variation_data in variations_data:
            ProductVariation.objects.create(product=product, **variation_data)
            
        # Create images
        for image_data in images_data:
            ProductImage.objects.create(product=product, **image_data)
            
        return product

    def update(self, instance, validated_data):
        # Separate variations and images data
        variations_data = self.context.get('variations', [])
        images_data = self.context.get('images', [])
        
        # Update the basic product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle variations: update existing, create new, delete removed
        current_variation_ids = set()
        for variation_data_raw in variations_data:
            variation_data = variation_data_raw.copy()  # Make a copy to modify
            variation_id = variation_data.pop('id', None)  # Pop id for update/create logic

            if variation_id:
                try:
                    variation = ProductVariation.objects.get(id=variation_id, product=instance)
                    variation_serializer = ProductVariationSerializer(variation, data=variation_data, partial=True)
                    if variation_serializer.is_valid(raise_exception=True):
                        variation_serializer.save()
                    current_variation_ids.add(variation_id)
                except ProductVariation.DoesNotExist:
                    # Handle new variation
                    variation_serializer = ProductVariationSerializer(data={**variation_data, 'product': instance.id})
                    if variation_serializer.is_valid(raise_exception=True):
                        new_variation = variation_serializer.save()
                        current_variation_ids.add(str(new_variation.id))
            else:
                # Create new variation
                variation_serializer = ProductVariationSerializer(data={**variation_data, 'product': instance.id})
                if variation_serializer.is_valid(raise_exception=True):
                    new_variation = variation_serializer.save()
                    current_variation_ids.add(str(new_variation.id))

        # Delete variations that were not updated
        ProductVariation.objects.filter(product=instance).exclude(id__in=list(current_variation_ids)).delete()

        # Handle images: update existing, create new, delete removed
        current_image_ids = set()
        for image_data_raw in images_data:
            image_data = image_data_raw.copy()
            image_id = image_data.pop('id', None)
            
            # Check if the 'image' field is a file object (new upload) or a URL string (existing)
            image_is_file = isinstance(image_data.get('image'), (InMemoryUploadedFile, UploadedFile))

            if image_id:
                try:
                    image_instance = ProductImage.objects.get(id=image_id, product=instance)
                    image_serializer = ProductImageSerializer(image_instance, data=image_data, partial=True)
                    if image_serializer.is_valid(raise_exception=True):
                        image_serializer.save()
                    current_image_ids.add(image_id)
                except ProductImage.DoesNotExist:
                    # If not found, create new image
                    if image_is_file:
                        image_serializer = ProductImageSerializer(data={**image_data, 'product': instance.id})
                        if image_serializer.is_valid(raise_exception=True):
                            new_image = image_serializer.save()
                            current_image_ids.add(str(new_image.id))
            else:
                # Create new image if it is a file
                if image_is_file:
                    image_serializer = ProductImageSerializer(data={**image_data, 'product': instance.id})
                    if image_serializer.is_valid(raise_exception=True):
                        new_image = image_serializer.save()
                        current_image_ids.add(str(new_image.id))

        # Delete images that were not included in the update
        ProductImage.objects.filter(product=instance).exclude(id__in=list(current_image_ids)).delete()

        return instance