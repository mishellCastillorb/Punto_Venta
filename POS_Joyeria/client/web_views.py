from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_http_methods, require_POST

from .models import Client
from .forms import ClientForm

from utils.roles import role_required

@role_required(["AdminPOS", "VendedorPOS"])
def client_list(request):
    """
    Lista clientes activos e inactivos.
    """
    activos = Client.objects.filter(is_active=True).order_by("-id")
    inactivos = Client.objects.filter(is_active=False).order_by("-id")

    return render(
        request,
        "client/clientes.html",
        {
            "activos": activos,
            "inactivos": inactivos,
        },
    )

@role_required(["AdminPOS", "VendedorPOS"])
@require_http_methods(["GET", "POST"])
def client_create(request):
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.is_active = True  # siempre activo al crear
            obj.save()
            return redirect("clients_web:list")
    else:
        form = ClientForm()

    return render(
        request,
        "client/formulario.html",
        {
            "form": form,
            "modo": "nuevo",
        },
    )

@role_required(["AdminPOS", "VendedorPOS"])
@require_http_methods(["GET", "POST"])
def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk)

    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect("clients_web:list")
    else:
        form = ClientForm(instance=client)

    return render(
        request,
        "client/formulario.html",
        {
            "form": form,
            "modo": "editar",
            "client": client,
        },
    )

@role_required(["AdminPOS", "VendedorPOS"])
@require_POST
def client_delete(request, pk):
    """
    Soft delete: desactivar cliente
    """
    client = get_object_or_404(Client, pk=pk)
    client.is_active = False
    client.save(update_fields=["is_active"])
    return redirect("clients_web:list")

@role_required(["AdminPOS", "VendedorPOS"])
@require_POST
def client_activate(request, pk):
    """
    Reactivar cliente
    """
    client = get_object_or_404(Client, pk=pk)
    client.is_active = True
    client.save(update_fields=["is_active"])
    return redirect("clients_web:list")
