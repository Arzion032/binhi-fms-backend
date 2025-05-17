from django.urls import path
from products.views import AddProduct, DeleteProduct, GetProducts, UpdateProduct, AcceptProduct
from .views import CategoryViewSet
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('products/', GetProducts.as_view(), name='product-list'),
    path('products/create/', AddProduct.as_view(), name='product-create'),
    path('products/update/<slug:slug>/', UpdateProduct.as_view(), name='product-detail'),
    path('products/delete/<slug:slug>/', DeleteProduct.as_view(), name='product-update'),
    path('products/accept_product/<slug:slug>/', AcceptProduct.as_view(), name='accept=product'),
] + router.urls


