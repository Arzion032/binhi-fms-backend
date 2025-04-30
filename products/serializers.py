from rest_framework import serializers
from .models import Category, Product, ProductImage, Review
from users.models import CustomUser 
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description',
            'created_at', 'updated_at'
        ]

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = [
            'id', 'product', 'image_url', 'uploaded_at'
        ]

class ReviewSerializer(serializers.ModelSerializer):
    buyer_username = serializers.ReadOnlyField(source='buyer.username')

    class Meta:
        model = Review
        fields = [
            'id', 'product', 'buyer', 'buyer_username',
            'rating', 'comment', 'created_at', 'updated_at'
        ]

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    vendor_username = serializers.ReadOnlyField(source='vendor.username')
    images = ProductImageSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description',
            'price', 'stock', 'category', 'category_id',
            'vendor', 'vendor_username', 'status',
            'created_at', 'updated_at', 'is_available',
            'images', 'reviews'
        ]
