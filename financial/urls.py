from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

urlpatterns = [
    path("federation_balance/",
         views.federation_balance_view,
         name="federation_balance_view"),
    path("transactions",
         views.transactions,
         name="transactions"),
    path("add_transaction/",
         views.add_transaction,
         name="add_transaction"),
    path("del_transaction/",
         views.del_transaction,
         name="del_transaction"),
]