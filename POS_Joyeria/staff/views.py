from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from utils.roles import role_required


def login_pos(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Usuario o contraseña incorrectos")
            return redirect("login_pos")

        if not user.is_staff:
            messages.error(request, "No tienes acceso al POS")
            return redirect("login_pos")

        login(request, user)
        return redirect("post_login")

    return render(request, "home/login.html")


def logout_pos(request):
    logout(request)
    return redirect("login_pos")


def post_login_redirect(request):
    # si no está logueado -> login
    if not request.user.is_authenticated:
        return redirect("login_pos")

    # si tiene rol válido -> manda a productos por defecto
    if request.user.is_superuser or request.user.groups.filter(name__in=["AdminPOS", "VendedorPOS"]).exists():
        return redirect("products_web:list")

    # si no tiene rol -> lo sacamos
    logout(request)
    messages.error(request, "No tienes rol asignado")
    return redirect("login_pos")


@role_required(["AdminPOS", "VendedorPOS"])
def home_pos(request):
    return render(request, "home/home_pos.html")
