from django.urls import path
from . import web_views

app_name = "cash_register_web"

urlpatterns = [
    path("", web_views.cash_status, name="status"),
    path("abrir/", web_views.open_cash, name="open"),
    path("cerrar/", web_views.close_cash, name="close"),
]
