from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.utils.http import url_has_allowed_host_and_scheme
from django.urls import reverse


def post_login_redirect(request):
    if not request.user.is_authenticated:
        return redirect("login_pos")
    return redirect("products_web:list")


def login_pos(request):
    if request.user.is_authenticated:
        return redirect("products_web:list")

    next_url = request.GET.get("next", "")

    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""
        next_url = request.POST.get("next") or next_url or ""

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Usuario o contraseña incorrectos.")
            return render(request, "home/login.html", {"next": next_url})

        if not user.is_staff:
            messages.error(request, "No tienes acceso al POS.")
            return render(request, "home/login.html", {"next": next_url})

        login(request, user)

        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)

        return redirect("products_web:list")

    return render(request, "home/login.html", {"next": next_url})


def logout_pos(request):
    next_url = request.GET.get("next", "")
    logout(request)

    if next_url:
        return redirect(f"{reverse('login_pos')}?next={next_url}")

    return redirect("login_pos")
