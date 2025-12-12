# suppliers/views.py
from rest_framework import generics
from .models import Supplier
from .serializers import SupplierSerializer


class SupplierListCreateAPIView(generics.ListCreateAPIView):
    # GET: lista proveedores
    # POST: crea proveedor
    queryset = Supplier.objects.all().order_by("-id")
    serializer_class = SupplierSerializer


class SupplierRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    # GET: detalle proveedor
    # PUT/PATCH: actualizar proveedor
    # DELETE: eliminar proveedor
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
