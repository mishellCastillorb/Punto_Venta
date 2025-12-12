from django.urls import path
from . import web_views

app_name = "products_web"

urlpatterns = [
    # CATEGORÍAS
    path("categorias/", web_views.category_list, name="categories"),
    path("categorias/nueva/", web_views.category_create, name="category_create"),
    path("categorias/<int:pk>/editar/", web_views.category_edit, name="category_edit"),

    # MATERIALES
    path("materiales/", web_views.material_list, name="materials"),
    path("materiales/nuevo/", web_views.material_create, name="material_create"),
    path("materiales/<int:pk>/editar/", web_views.material_edit, name="material_edit"),

    # PRODUCTOS
    path("productos/", web_views.product_list, name="list"),
    path("productos/nuevo/", web_views.product_create, name="product_create"),
    path("productos/<int:pk>/editar/", web_views.product_edit, name="product_edit"),
]