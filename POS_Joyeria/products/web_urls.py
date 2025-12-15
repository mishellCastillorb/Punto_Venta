from django.urls import path
from . import web_views
from .web_views import delete_product

app_name = "products_web"

urlpatterns = [
    # CATEGORÍAS
    path("categorias/", web_views.category_list, name="categories"),
    path("categorias/nueva/", web_views.category_create, name="category_create"),
    path("categorias/<int:pk>/editar/", web_views.category_edit, name="category_edit"),
    path("categorias/<int:pk>/eliminar/", web_views.category_delete, name="category_delete"),


    # MATERIALES
    path("materiales/", web_views.material_list, name="materials"),
    path("materiales/nuevo/", web_views.material_create, name="material_create"),
    path("materiales/<int:pk>/editar/", web_views.material_edit, name="material_edit"),
    path("materiales/<int:pk>/eliminar/", web_views.material_delete, name="material_delete"),

    # PRODUCTOS
    path("", web_views.product_list, name="list"),  # /productos/
    path("nuevo/", web_views.product_create, name="product_create"),
    path("<int:pk>/editar/", web_views.product_edit, name="product_edit"),
    path("eliminar/<int:product_id>/", delete_product, name="delete"),
]