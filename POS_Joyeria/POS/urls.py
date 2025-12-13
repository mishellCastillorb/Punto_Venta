from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", include("home.urls")),

    # LOGIN / LOGOUT
    path("login/", auth_views.LoginView.as_view(
        template_name="home/login.html",
        redirect_authenticated_user=True
    ), name="login_pos"),

    path("logout/", auth_views.LogoutView.as_view(), name="logout_pos"),

    # API
    path("api/clients/", include("client.urls")),
    path("api/suppliers/", include("suppliers.urls")),
    path("api/products/", include("products.urls")),
    path("api/employees/", include("staff.urls")),

    # WEB
    path("clientes/", include("client.web_urls")),
    path("proveedores/", include("suppliers.web_urls")),
    path("productos/", include("products.web_urls")),
    path("personal/", include("staff.web_urls")),
    path("ventas/", include("sales.web_urls"))

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
