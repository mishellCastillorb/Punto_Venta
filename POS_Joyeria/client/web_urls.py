from django.urls import path
from . import web_views

app_name = "clients_web"

urlpatterns = [
    path("", web_views.client_list, name="list"),
    path("nuevo/", web_views.client_create, name="create"),
    path("<int:pk>/editar/", web_views.client_edit, name="edit"),
    path("<int:pk>/eliminar/", web_views.client_delete, name="delete"),
    path("<int:pk>/activar/", web_views.client_activate, name="activate"),
]
