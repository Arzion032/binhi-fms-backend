from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

urlpatterns = [
    path("inventory/",
         views.inventory,
         name="inventory"),
    path("add_inventory_item/",
         views.add_item,
         name="add_inventory_item"),
    path("delete_inventory_item/",
         views.delete_item,
         name="delete_inventory_item"),

]