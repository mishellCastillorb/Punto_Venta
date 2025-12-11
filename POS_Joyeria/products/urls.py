from django.urls import path
from .views import (
    ProductListCreateAPIView,
    ProductDetailAPIView,
    CategoryListCreateAPIView,
    CategoryDetailAPIView,
    MaterialListCreateAPIView,
    MaterialDetailAPIView,
)

urlpatterns = [
    # Productos
    path("", ProductListCreateAPIView.as_view(), name="product-list-create"),
    path("<int:pk>/", ProductDetailAPIView.as_view(), name="product-detail"),

    # Categorías
    path("categories/", CategoryListCreateAPIView.as_view(), name="category-list-create"),
    path("categories/<int:pk>/", CategoryDetailAPIView.as_view(), name="category-detail"),

    # Materiales
    path("materials/", MaterialListCreateAPIView.as_view(), name="material-list-create"),
    path("materials/<int:pk>/", MaterialDetailAPIView.as_view(), name="material-detail"),
]
