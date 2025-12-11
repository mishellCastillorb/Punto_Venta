from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Client
from .serializers import ClientSerializer

# Listar solo clientes activos /api/clients/list/
class ClientListView(generics.ListAPIView):
    serializer_class = ClientSerializer
    permission_classes = []

    def get_queryset(self):
        return Client.objects.filter(is_active=True)

# Crear cliente /api/clients/create/
class ClientCreateView(generics.CreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [] #permissions.IsAuthenticated

#Ver / editar cliente /api/clients/1/
class ClientDetailView(generics.RetrieveUpdateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = []

# Desactivar cliente con soft delete (no borrarlo directamente de la bd, solo ponerlo inactivo)
class ClientDeactivateView(APIView):
    permission_classes = []

    def delete(self, request, pk):
        client = get_object_or_404(Client, pk=pk)
        client.is_active = False
        client.save()
        return Response({"message": "Cliente desactivado"}, status=200)


