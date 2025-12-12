from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Material, Product
from .forms import CategoryForm, MaterialForm, ProductForm

#Categorias sin js
def category_list(request):
    categorias = Category.objects.all().order_by("name")
    return render(request, "products/categorias.html", {
        "categorias": categorias
    })

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
def material_list(request):
    materiales = Material.objects.all().order_by("name")
    return render(request, "products/materiales.html", {
        "materiales": materiales
    })

def material_create(request):
    form = MaterialForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("products_web:materials")

    return render(request, "products/form_material.html", {
        "form": form
    })

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
def product_list(request):
    productos = Product.objects.select_related(
        "category", "material", "supplier"
    )
    return render(request, "products/productos.html", {
        "productos": productos
    })

def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("products_web:list")

    return render(request, "products/form_producto.html", {
        "form": form
    })
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

