from django.urls import path
from .web_views import pos_view

app_name = "sales"

urlpatterns = [
    path("", pos_view, name="pos"),
]
