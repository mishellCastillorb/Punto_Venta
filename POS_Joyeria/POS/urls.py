

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('api/clients/', include('client.urls')),
    path('api/suppliers/', include('suppliers.urls')),
    path('api/products/', include('products.urls')),
    path('api/employees/', include('staff.urls')),

    # WEB (sin JS)
    path('proveedores/', include('suppliers.web_urls')),
]
