from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrderViewSet,
   # ConfirmCheckoutView,
    OrderHistoryView,
    OrderStatusPatchView,
    MarketTransactionStatusPatchView,
)

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    # PATCH (custom) status endpoints (keep these before router!)
    path('orders/<uuid:pk>/status/', OrderStatusPatchView.as_view(), name="order-status-patch"),
    path('transactions/<uuid:pk>/status/', MarketTransactionStatusPatchView.as_view(), name="market-transaction-status-patch"),

    # Other custom endpoints
#   path('confirm/', ConfirmCheckoutView.as_view(), name="checkout_view"),
    path('order-history/', OrderHistoryView.as_view(), name="order-history"),

    # DRF router URLs
    path('', include(router.urls)),
]
