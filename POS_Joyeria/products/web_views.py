from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Material, Product
from .forms import CategoryForm, MaterialForm, ProductForm
from utils.roles import role_required


#Categorias sin js
@role_required(["AdminPOS", "VendedorPOS"])
def category_list(request):
    categorias = Category.objects.all().order_by("name")
    return render(request, "products/categorias.html", {
        "categorias": categorias
    })

@role_required(["AdminPOS"])
def category_create(request):
    form = CategoryForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("products_web:categories")

    return render(request, "products/form_categoria.html", {
        "form": form,
        "modo": "crear",
    })

#Materiales
@role_required(["AdminPOS", "VendedorPOS"])
def material_list(request):
    materiales = Material.objects.all().order_by("name")
    return render(request, "products/materiales.html", {
        "materiales": materiales
    })

@role_required(["AdminPOS"])
def material_create(request):
    form = MaterialForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("products_web:materials")

    return render(request, "products/form_material.html", {
        "form": form
    })

@role_required(["AdminPOS"])
def material_edit(request, pk):
    material = get_object_or_404(Material, pk=pk)
    form = MaterialForm(request.POST or None, instance=material)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("products_web:materials")

    return render(request, "products/form_material.html", {
        "form": form
    })




#Productos
@role_required(["AdminPOS", "VendedorPOS"])
def product_list(request):
    productos = Product.objects.select_related(
        "category", "material", "supplier"
    )
    return render(request, "products/productos.html", {
        "productos": productos
    })



@role_required(["AdminPOS"])
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("products_web:list")

    return render(request, "products/form_producto.html", {
        "form": form
    })
@role_required(["AdminPOS"])
def product_edit(request, pk):
    producto = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=producto)

    if request.method == "POST" and form.is_valid():
        compra = form.cleaned_data["purchase_price"]
        venta = form.cleaned_data["sale_price"]

        #Si el precio de venta es menor
        if venta < compra and "confirmar" not in request.POST:
            #Mostrar pantalla de confirmación
            return render(request, "products/confirm_precio.html", {
                "form": form,
                "producto": producto,
                "compra": compra,
                "venta": venta,
            })

        # Si confirmo its ok
        form.save()
        return redirect("products_web:list")

    return render(request, "products/form_producto.html", {
        "form": form,
        "modo": "editar",
    })


@role_required(["AdminPOS"])
def category_edit(request, pk):
    categoria = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=categoria)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("products_web:categories")

    return render(request, "products/form_categoria.html", {
        "form": form,
        "modo": "editar",
    })

