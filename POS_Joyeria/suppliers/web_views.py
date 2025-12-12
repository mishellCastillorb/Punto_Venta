from django.shortcuts import render, get_object_or_404, redirect
from .models import Supplier
from .forms import SupplierForm

def supplier_list(request):
    proveedores = Supplier.objects.all().order_by("-id")
    return render(request, "suppliers/proveedores.html", {"proveedores": proveedores})

def supplier_create(request):
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("suppliers_web:list")
    else:
        form = SupplierForm()

    return render(request, "suppliers/formulario.html", {
        "form": form,
        "modo": "crear",
    })

def supplier_update(request, pk):
    proveedor = get_object_or_404(Supplier, pk=pk)

    if request.method == "POST":
        form = SupplierForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            return redirect("suppliers_web:list")
    else:
        form = SupplierForm(instance=proveedor)

    return render(request, "suppliers/formulario.html", {
        "form": form,
        "modo": "editar",
        "proveedor": proveedor,
    })

def supplier_delete(request, pk):
    proveedor = get_object_or_404(Supplier, pk=pk)

    if request.method == "POST":
        proveedor.delete()
        return redirect("suppliers_web:list")

    # Si alguien entra por GET, lo regresamos
    return redirect("suppliers_web:list")
