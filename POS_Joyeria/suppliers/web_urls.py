from django.urls import path
from .web_views import supplier_list, supplier_create, supplier_update, supplier_delete

app_name = "suppliers_web"

urlpatterns = [
    path('', supplier_list, name='list'),                 # /proveedores/
    path('nuevo/', supplier_create, name='create'),       # /proveedores/nuevo/
    path('<int:pk>/editar/', supplier_update, name='edit'),   # /proveedores/1/editar/
    path('<int:pk>/eliminar/', supplier_delete, name='delete')# /proveedores/1/eliminar/
]
