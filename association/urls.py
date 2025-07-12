from django.urls import path
from .views import (
    AssociationListCreateView,
    AssociationRetrieveUpdateDeleteView,
    FarmerListCreateView,
    FarmerRetrieveUpdateDeleteView,
)

urlpatterns = [
    # Associations
    path('associations/', AssociationListCreateView.as_view(), name='association-list-create'),
    path('associations/<uuid:pk>/', AssociationRetrieveUpdateDeleteView.as_view(), name='association-detail'),

    # Farmers
    path('farmers/', FarmerListCreateView.as_view(), name='farmer-list-create'),
    path('farmers/<str:pk>/', FarmerRetrieveUpdateDeleteView.as_view(), name='farmer-detail'),
]
