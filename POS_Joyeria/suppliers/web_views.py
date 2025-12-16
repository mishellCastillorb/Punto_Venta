# suppliers/web_views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib import messages
from .models import Supplier
from .forms import SupplierForm
from utils.roles import role_required
from django.db.models.deletion import ProtectedError
from django.urls import reverse
from products.models import Product


def _role_flags(user):
    is_adminpos = bool(
        user
        and user.is_authenticated
        and (user.is_superuser or user.groups.filter(name="AdminPOS").exists())
    )
    is_vendedor = bool(
        user
        and user.is_authenticated
        and user.groups.filter(name="VendedorPOS").exists()
    )
    return {"is_adminpos": is_adminpos, "is_vendedor": is_vendedor}


# LISTAR: Admin y Vendedor (ambos pueden ver proveedores)
@role_required(["AdminPOS", "VendedorPOS"])
def supplier_list(request):
    proveedores = Supplier.objects.all().order_by("-id")
    return render(
        request,
        "suppliers/proveedores.html",
        {
            "proveedores": proveedores,
            **_role_flags(request.user),
        },
    )


# CREAR: SOLO Admin (según tu tabla)
@role_required(["AdminPOS"])
@require_http_methods(["GET", "POST"])
def supplier_create(request):
    form = SupplierForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("suppliers_web:list")

    return render(
        request,
        "suppliers/formulario.html",
        {
            "form": form,
            "modo": "crear",
            **_role_flags(request.user),
        },
    )


# EDITAR: SOLO Admin (según tu tabla)
@role_required(["AdminPOS"])
@require_http_methods(["GET", "POST"])
def supplier_update(request, pk):
    proveedor = get_object_or_404(Supplier, pk=pk)
    form = SupplierForm(request.POST or None, instance=proveedor)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("suppliers_web:list")

    return render(
        request,
        "suppliers/formulario.html",
        {
            "form": form,
            "modo": "editar",
            "proveedor": proveedor,
            **_role_flags(request.user),
        },
    )


@role_required(["AdminPOS"])
@require_POST
def supplier_delete(request, pk):
    proveedor = get_object_or_404(Supplier, pk=pk)
    proveedor.delete()
    return redirect("suppliers_web:list")

@require_POST
@role_required(["AdminPOS"])
def supplier_delete(request, pk):
    proveedor = get_object_or_404(Supplier, pk=pk)

    try:
        proveedor.delete()
        messages.success(request, "Proveedor eliminado correctamente.")
    except ProtectedError:
        usados_en = Product.objects.filter(supplier=proveedor).values_list("name", flat=True)[:5]
        usados_txt = ", ".join(usados_en) if usados_en else "productos existentes"

        messages.error(
            request,
            "No se puede eliminar el proveedor porque ya está asociado a productos"
        )

    return redirect(reverse("suppliers_web:list"))