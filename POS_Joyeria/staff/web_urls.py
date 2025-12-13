from django.urls import path
from . import web_views

app_name = "staff_web"

urlpatterns = [
    path("", web_views.staff_list, name="list"),
    path("nuevo/", web_views.staff_create, name="create"),
    path("<int:pk>/editar/", web_views.staff_edit, name="edit"),
    path("<int:pk>/eliminar/", web_views.staff_delete, name="delete"),
    path("<int:pk>/activar/", web_views.staff_activate, name="activate"),
]
