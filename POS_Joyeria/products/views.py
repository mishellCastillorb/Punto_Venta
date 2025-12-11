from rest_framework import generics
from .models import Category, Material, Product
from .serializers import (
    CategorySerializer,
    MaterialSerializer,
    ProductSerializer,
)


# --------- CATEGORY --------- #

class CategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer


class CategoryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# --------- MATERIAL --------- #

class MaterialListCreateAPIView(generics.ListCreateAPIView):
    queryset = Material.objects.all().order_by("name")
    serializer_class = MaterialSerializer


class MaterialDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer


# --------- PRODUCT --------- #

class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all().order_by("name")
    serializer_class = ProductSerializer


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
