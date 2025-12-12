from django.http import HttpResponseForbidden

def role_required(allowed_roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):

            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            if not request.user.is_authenticated:
                return HttpResponseForbidden("No autenticado")

            user_roles = request.user.groups.values_list("name", flat=True)

            if any(role in allowed_roles for role in user_roles):
                return view_func(request, *args, **kwargs)

            return HttpResponseForbidden("No tienes permisos")

        return _wrapped_view
    return decorator
