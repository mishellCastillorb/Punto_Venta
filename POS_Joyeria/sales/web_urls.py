from django.urls import path
from .web_views import pos_view, add_to_ticket

app_name = "sales"

urlpatterns = [
    path("", pos_view, name="pos"),
    path("add/<int:product_id>/", add_to_ticket, name="add"),
]
