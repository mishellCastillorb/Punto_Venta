# products/web_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import Category, Material, Product
from .forms import CategoryForm, MaterialForm, ProductForm
from utils.roles import role_required


def _is_adminpos(user):
    return bool(
        user
        and user.is_authenticated
        and (user.is_superuser or user.groups.filter(name="AdminPOS").exists())
    )



# CATEGORÍAS
@role_required(["AdminPOS", "VendedorPOS"])
def category_list(request):
    categorias = Category.objects.all().order_by("name")
    return render(
        request,
        "products/categorias.html",
        {
            "categorias": categorias,
            "is_adminpos": _is_adminpos(request.user),
        },
    )


@role_required(["AdminPOS"])
def category_create(request):
    form = CategoryForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("products_web:categories")

    return render(
        request,
        "products/form_categoria.html",
        {
            "form": form,
            "modo": "crear",
            "is_adminpos": _is_adminpos(request.user),
        },
    )


@role_required(["AdminPOS"])
def category_edit(request, pk):
    categoria = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=categoria)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("products_web:categories")

    return render(
        request,
        "products/form_categoria.html",
        {
            "form": form,
            "modo": "editar",
            "is_adminpos": _is_adminpos(request.user),
            "categoria": categoria,
        },
    )


@role_required(["AdminPOS"])
@require_POST
def category_delete(request, pk):
    categoria = get_object_or_404(Category, pk=pk)
    categoria.delete()
    return redirect("products_web:categories")


# MATERIALES
@role_required(["AdminPOS", "VendedorPOS"])
def material_list(request):
    materiales = Material.objects.all().order_by("name")
    return render(
        request,
        "products/materiales.html",
        {
            "materiales": materiales,
            "is_adminpos": _is_adminpos(request.user),
        },
    )


@role_required(["AdminPOS"])
def material_create(request):
    form = MaterialForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("products_web:materials")

    return render(
        request,
        "products/form_material.html",
        {
            "form": form,
            "modo": "crear",
            "is_adminpos": _is_adminpos(request.user),
        },
    )


@role_required(["AdminPOS"])
def material_edit(request, pk):
    material = get_object_or_404(Material, pk=pk)
    form = MaterialForm(request.POST or None, instance=material)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("products_web:materials")

    return render(
        request,
        "products/form_material.html",
        {
            "form": form,
            "modo": "editar",
            "is_adminpos": _is_adminpos(request.user),
            "material": material,
        },
    )


@role_required(["AdminPOS"])
@require_POST
def material_delete(request, pk):
    material = get_object_or_404(Material, pk=pk)
    material.delete()
    return redirect("products_web:materials")


# PRODUCTOS
@role_required(["AdminPOS", "VendedorPOS"])
def product_list(request):
    productos = (
        Product.objects
        .select_related("category", "material", "supplier")
        .order_by("-id")
    )
    return render(
        request,
        "products/productos.html",
        {
            "productos": productos,
            "is_adminpos": _is_adminpos(request.user),
        },
    )


@role_required(["AdminPOS"])
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("products_web:list")

    return render(
        request,
        "products/form_producto.html",
        {
            "form": form,
            "modo": "crear",
            "is_adminpos": _is_adminpos(request.user),
        },
    )


@role_required(["AdminPOS"])
def product_edit(request, pk):
    producto = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=producto)

    if request.method == "POST" and form.is_valid():
        compra = form.cleaned_data.get("purchase_price")
        venta = form.cleaned_data.get("sale_price")

        if compra is not None and venta is not None:
            if venta < compra and "confirmar" not in request.POST:
                return render(
                    request,
                    "products/confirm_precio.html",
                    {
                        "form": form,
                        "producto": producto,
                        "compra": compra,
                        "venta": venta,
                        "is_adminpos": _is_adminpos(request.user),
                    },
                )

        form.save()
        return redirect("products_web:list")

    return render(
        request,
        "products/form_producto.html",
        {
            "form": form,
            "modo": "editar",
            "producto": producto,
            "is_adminpos": _is_adminpos(request.user),
        },
    )
