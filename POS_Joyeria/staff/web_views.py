# staff/web_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib import messages

from utils.roles import role_required
from .models import StaffProfile
from .forms import StaffCreateForm, StaffEditForm


def _get_role_user(user):
    if user and user.is_authenticated and user.is_superuser:
        return "SuperAdmin"
    if user and user.is_authenticated:
        return user.groups.values_list("name", flat=True).first() or ""
    return ""


def _target_role(profile: StaffProfile) -> str:
    return profile.user.groups.values_list("name", flat=True).first() or ""


def _can_manage_target(request_user, profile: StaffProfile) -> bool:
    """
    - SuperAdmin: puede gestionar a cualquiera
    - AdminPOS: SOLO puede gestionar VendedorPOS
    """
    if request_user.is_superuser:
        return True
    return _target_role(profile) == "VendedorPOS"


@role_required(["AdminPOS"])  # AdminPOS + SuperAdmin (por el decorator)
def staff_list(request):
    activos = (
        StaffProfile.objects.select_related("user")
        .filter(user__is_active=True)
        .order_by("-id")
    )
    inactivos = (
        StaffProfile.objects.select_related("user")
        .filter(user__is_active=False)
        .order_by("-id")
    )

    return render(
        request,
        "staff/personal.html",
        {
            "activos": activos,
            "inactivos": inactivos,
            "role_user": _get_role_user(request.user),
        },
    )


@role_required(["AdminPOS"])
@require_http_methods(["GET", "POST"])
def staff_create(request):
    form = StaffCreateForm(request.POST or None, request_user=request.user)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Personal creado correctamente.")
        return redirect("staff_web:list")

    return render(
        request,
        "staff/formulario.html",
        {
            "form": form,
            "modo": "crear",
            "role_user": _get_role_user(request.user),
        },
    )


@role_required(["AdminPOS"])
@require_http_methods(["GET", "POST"])
def staff_edit(request, pk):
    profile = get_object_or_404(StaffProfile, pk=pk)

    # AdminPOS normal NO puede editar AdminPOS
    if not _can_manage_target(request.user, profile):
        messages.error(request, "No tienes permisos para editar a un AdminPOS.")
        return redirect("staff_web:list")

    user = profile.user

    form = StaffEditForm(
        request.POST or None,
        instance=profile,
        user_instance=user,
        request_user=request.user,
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Personal actualizado correctamente.")
        return redirect("staff_web:list")

    return render(
        request,
        "staff/formulario.html",
        {
            "form": form,
            "modo": "editar",
            "profile": profile,
            "role_user": _get_role_user(request.user),
        },
    )


@role_required(["AdminPOS"])
@require_POST
def staff_delete(request, pk):
    profile = get_object_or_404(StaffProfile, pk=pk)

    # No desactivar tu propio usuario
    if profile.user_id == request.user.id:
        messages.error(request, "No puedes desactivar tu propio usuario.")
        return redirect("staff_web:list")

    # AdminPOS normal NO puede desactivar AdminPOS
    if not _can_manage_target(request.user, profile):
        messages.error(request, "No tienes permisos para desactivar a un AdminPOS.")
        return redirect("staff_web:list")

    profile.user.is_active = False
    profile.user.save(update_fields=["is_active"])
    messages.success(request, f"Usuario '{profile.user.username}' desactivado correctamente.")
    return redirect("staff_web:list")


@role_required(["AdminPOS"])
@require_POST
def staff_activate(request, pk):
    profile = get_object_or_404(StaffProfile, pk=pk)

    # AdminPOS normal NO puede reactivar AdminPOS
    if not _can_manage_target(request.user, profile):
        messages.error(request, "No tienes permisos para reactivar a un AdminPOS.")
        return redirect("staff_web:list")

    profile.user.is_active = True
    profile.user.save(update_fields=["is_active"])
    messages.success(request, f"Usuario '{profile.user.username}' reactivado correctamente.")
    return redirect("staff_web:list")
