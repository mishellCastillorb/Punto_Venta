from django.urls import path
from .views import EmployeeListCreateAPIView

urlpatterns = [
    path("", EmployeeListCreateAPIView.as_view(), name="employee-list-create"),
]
