from rest_framework import serializers, viewsets
from .models import Category, Product, ProductImage, Review
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

    class Meta:
        model = Product
        fields = '__all__'
