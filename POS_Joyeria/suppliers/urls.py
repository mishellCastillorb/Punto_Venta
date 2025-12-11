from django.urls import path
from .views import SupplierListCreateAPIView

urlpatterns = [
    path("", SupplierListCreateAPIView.as_view(), name="supplier-list-create"),
]
