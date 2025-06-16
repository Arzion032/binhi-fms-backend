from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

urlpatterns = [
    path("inventory/",
         views.inventory,
         name="inventory"),
    path("add_item/",
         views.add_item,
         name="add_inventory_item"),
    path("delete_item/",
         views.delete_item,
         name="delete_inventory_item"),
    path('update_item/<slug:slug>/', 
         views.update_item, 
         name='update_inventory_item'),
    path('rent_item/', 
         views.rent_item, 
         name='rent_inventory_item'),
    path('return_item/<uuid:rental_id>/', 
         views.return_item, 
         name='return_inventory_item'),
    path('inventory/rentals/list/', 
         views.list_rentals, 
         name='list_rentals'),
]