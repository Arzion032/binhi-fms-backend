from django.urls import path
from products.views import AddProduct, DeleteProduct, GetProducts, UpdateProduct



urlpatterns = [
    path('products/', GetProducts.as_view(), name='product-list'),
    path('products/create/', AddProduct.as_view(), name='product-create'),
    path('products/update/<uuid:pk>/', UpdateProduct.as_view(), name='product-detail'),
    path('products/delete/<uuid:pk>/', DeleteProduct.as_view(), name='product-update'),
]
