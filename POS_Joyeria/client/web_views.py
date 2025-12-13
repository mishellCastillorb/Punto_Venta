from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_http_methods, require_POST

from .models import Client
from .forms import ClientForm
from utils.roles import role_required


def _is_adminpos(user):
    return bool(
        user
        and user.is_authenticated
        and (user.is_superuser or user.groups.filter(name="AdminPOS").exists())
    )


# LISTAR → AdminPOS y VendedorPOS
@role_required(["AdminPOS", "VendedorPOS"])
def client_list(request):
    activos = Client.objects.filter(is_active=True).order_by("-id")
    inactivos = Client.objects.filter(is_active=False).order_by("-id")

    return render(
        request,
        "client/clientes.html",
        {
            "activos": activos,
            "inactivos": inactivos,
            "is_adminpos": _is_adminpos(request.user),
        },
    )


# CREAR → AdminPOS y VendedorPOS
@role_required(["AdminPOS", "VendedorPOS"])
@require_http_methods(["GET", "POST"])
def client_create(request):
    form = ClientForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.is_active = True
        obj.save()
        return redirect("clients_web:list")

    return render(
        request,
        "client/formulario.html",
        {
            "form": form,
            "modo": "nuevo",
            "is_adminpos": _is_adminpos(request.user),
        },
    )


# EDITAR → AdminPOS y VendedorPOS
@role_required(["AdminPOS", "VendedorPOS"])
@require_http_methods(["GET", "POST"])
def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk)
    form = ClientForm(request.POST or None, instance=client)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("clients_web:list")

    return render(
        request,
        "client/formulario.html",
        {
            "form": form,
            "modo": "editar",
            "client": client,
            "is_adminpos": _is_adminpos(request.user),
        },
    )


# ELIMINAR (soft delete) → SOLO AdminPOS
@role_required(["AdminPOS"])
@require_POST
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    client.is_active = False
    client.save(update_fields=["is_active"])
    return redirect("clients_web:list")


# REACTIVAR → SOLO AdminPOS
@role_required(["AdminPOS"])
@require_POST
def client_activate(request, pk):
    client = get_object_or_404(Client, pk=pk)
    client.is_active = True
    client.save(update_fields=["is_active"])
    return redirect("clients_web:list")
