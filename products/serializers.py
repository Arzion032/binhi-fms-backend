from rest_framework import serializers, viewsets
from .models import Category, Product, ProductImage, Review, ProductVariation
from users.models import CustomUser 
from django.utils.text import slugify

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['id', 'slug']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_main', 'uploaded_at']

class ProductVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariation
        fields = ['id', 'name', 'unit_price', 'stock', 'unit_measurement', 'is_available', 'is_default', 'product']

class ReviewSerializer(serializers.ModelSerializer):
    buyer_username = serializers.ReadOnlyField(source='buyer.username')

    class Meta:
        model = Review
        fields = [
            'id', 'product', 'buyer', 'buyer_username',
            'rating', 'comment', 'created_at', 'updated_at'
        ]

class ProductSerializer(serializers.ModelSerializer):
    variations = ProductVariationSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.ReadOnlyField(source='category.name')
    vendor_name = serializers.ReadOnlyField(source='vendor.username')
    vendor_code = serializers.ReadOnlyField(source='vendor.farmer_code')
    association = serializers.ReadOnlyField(source='vendor.association.name')

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'category', 'category_name',
            'vendor', 'vendor_name', 'vendor_code', 'association',
            'status', 'is_available', 'created_at', 'updated_at',
            'variations', 'images'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def create(self, validated_data):
        variations_data = self.context.get('variations', [])
        images_data = self.context.get('images', [])
        
        product = Product.objects.create(**validated_data)
        
        # Create variations
        for variation_data in variations_data:
            ProductVariation.objects.create(product=product, **variation_data)
            
        # Create images
        for image_data in images_data:
            ProductImage.objects.create(product=product, **image_data)
            
        return product

    def update(self, instance, validated_data):
        variations_data = self.context.get('variations', [])
        images_data = self.context.get('images', [])
        
        # Update product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update variations if provided
        if variations_data:
            instance.variations.all().delete()
            for variation_data in variations_data:
                ProductVariation.objects.create(product=instance, **variation_data)
                
        # Update images if provided
        if images_data:
            instance.images.all().delete()
            for image_data in images_data:
                ProductImage.objects.create(product=instance, **image_data)
                
        return instance
