from functools import wraps
from django.shortcuts import redirect, render
from django.urls import reverse


def role_required(allowed_roles):
    """
    allowed_roles: lista de nombres de grupos permitidos, ej:
      ["AdminPOS"] o ["AdminPOS", "VendedorPOS"]
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):

            next_url = request.get_full_path()

            # 1) No autenticado -> login con next
            if not request.user.is_authenticated:
                login_url = reverse("login_pos")
                return redirect(f"{login_url}?next={next_url}")

            # 2) Superuser siempre pasa
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # 3) Roles por grupos
            user_roles = request.user.groups.values_list("name", flat=True)
            if any(role in allowed_roles for role in user_roles):
                return view_func(request, *args, **kwargs)

            # 4) Sin permisos -> pantalla no_permisos (pasamos next)
            return render(request, "home/no_permisos.html", {"next": next_url}, status=403)

        return _wrapped_view

    return decorator
