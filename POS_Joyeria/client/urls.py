from django.urls import path
from .views import ClientListCreateAPIView

urlpatterns = [
    path("", ClientListCreateAPIView.as_view(), name="client-list-create"),
]
