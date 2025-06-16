from django.urls import path
from products.views import (
    AddProduct, DeleteProduct, GetProducts, UpdateProduct, AcceptProduct,
    BatchDeleteProducts
)
from .views import CategoryViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('', GetProducts.as_view(), name='product-list'),
    path('create/', AddProduct.as_view(), name='product-create'),
    path('update/<uuid:pk>/', UpdateProduct.as_view(), name='product-update'),
    path('delete/<uuid:pk>/', DeleteProduct.as_view(), name='product-delete'),
    path('batch-delete/', BatchDeleteProducts.as_view(), name='product-batch-delete'),
    path('products/accept/<uuid:pk>/', AcceptProduct.as_view(), name='product-accept'),
] + router.urls


