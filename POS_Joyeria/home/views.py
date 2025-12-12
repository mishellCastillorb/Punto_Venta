from utils.roles import role_required
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout


@role_required(["AdminPOS", "VendedorPOS"])
def home_pos(request):
    return render(request, "home/home_pos.html")


def post_login_redirect(request):
    user = request.user

    if not user.is_authenticated:
        return redirect("/admin/login/")

    #Admin o superuser
    if user.is_superuser or user.groups.filter(name="AdminPOS").exists():
        return redirect("home_pos")

    #Vendedor
    if user.groups.filter(name="VendedorPOS").exists():
        return redirect("home_pos")

    # Si no pertenece a ningun rol
    return redirect("/admin/logout/")


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
    user = request.user

    if not user.is_authenticated:
        return redirect("login_pos")

    if user.is_superuser or user.groups.filter(name="AdminPOS").exists():
        return redirect("home_pos")

    if user.groups.filter(name="VendedorPOS").exists():
        return redirect("home_pos")

    logout(request)
    messages.error(request, "No tienes rol asignado")
    return redirect("login_pos")


from utils.roles import role_required

@role_required(["AdminPOS", "VendedorPOS"])
def home_pos(request):
    return render(request, "home/home_pos.html")
