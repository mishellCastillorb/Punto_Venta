from django.urls import path
from .views import ClientListView, ClientCreateView, ClientDetailView, ClientDeactivateView

urlpatterns = [
    path("list/", ClientListView.as_view()), #GET
    path("create/", ClientCreateView.as_view()), #POST
    path("<int:pk>/", ClientDetailView.as_view()), #GET Y PUT
    path("<int:pk>/delete/", ClientDeactivateView.as_view()),  #soft delete
]
