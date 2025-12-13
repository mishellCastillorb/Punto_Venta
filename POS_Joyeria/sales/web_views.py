from django.shortcuts import render
from utils.roles import role_required


@role_required(["AdminPOS", "VendedorPOS"])
def pos_view(request):
    # Commit 1: solo pantalla base, sin lógica ni consultas a BD
    return render(request, "sales/pos.html")
