

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('api/clients/', include('client.urls')),
    path('api/suppliers/', include('suppliers.urls')),
    path('api/products/', include('products.urls')),
    path('api/employees/', include('staff.urls')),

    path("", include("home.urls")),
    path("products/", include("products.urls")),
   # path("sales/", include("sales.urls")),
    path("staff/", include("staff.urls")),
    path("suppliers/", include("suppliers.urls")),

    # WEB (sin JS)
    path('proveedores/', include('suppliers.web_urls')),
    path("products/", include("products.web_urls")),
    path('clientes/', include('client.web_urls')),
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )