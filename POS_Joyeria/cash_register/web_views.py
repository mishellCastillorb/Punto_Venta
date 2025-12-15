from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages

from sales.models import Sale
from .models import CashRegister
from utils.roles import role_required

#Estado de la caja (abierta/cerrada)
@role_required(["AdminPOS", "VendedorPOS"])
def cash_status(request):
    cash = CashRegister.objects.filter(is_closed=False).first()

    if not cash:
        return redirect("cash_register_web:open")

    return render(
        request,
        "cash_register/status.html",
        {"cash": cash}
    )
#Abir caja
@role_required(["AdminPOS", "VendedorPOS"])
def open_cash(request):
    if CashRegister.objects.filter(is_closed=False).exists():
        messages.warning(request, "Ya hay una caja abierta.")
        return redirect("cash_register_web:status")

    if request.method == "POST":
        opening_amount = request.POST.get("opening_amount")

        CashRegister.objects.create(
            opened_by=request.user,
            opening_amount=opening_amount
        )

        messages.success(request, "Caja abierta correctamente.")
        return redirect("cash_register_web:status")

    return render(request, "cash_register/open.html")

#Cerrar
@role_required(["AdminPOS", "VendedorPOS"])
def close_cash(request):
    cash = CashRegister.objects.filter(is_closed=False).first()

    if not cash:
        messages.error(request, "No hay caja abierta.")
        return redirect("cash_register_web:open")

    sales = Sale.objects.filter(
        status=Sale.Status.PAID,
        created_at__gte=cash.opened_at,
        created_at__lte=timezone.now()
    )

    cash_total = sum(s.total for s in sales if s.payment_method == "CASH")
    card_total = sum(s.total for s in sales if s.payment_method == "CARD")
    transfer_total = sum(s.total for s in sales if s.payment_method == "TRANSFER")
    total_sales = sum(s.total for s in sales)

    if request.method == "POST":
        closing_amount = float(request.POST.get("closing_amount"))

        cash.cash_total = cash_total
        cash.card_total = card_total
        cash.transfer_total = transfer_total
        cash.total_sales = total_sales

        cash.closing_amount = closing_amount
        cash.difference = closing_amount - cash_total

        cash.closed_by = request.user
        cash.closed_at = timezone.now()
        cash.is_closed = True
        cash.save()

        messages.success(request, "Caja cerrada correctamente.")
        return redirect("cash_register_web:status")

    return render(
        request,
        "cash_register/close.html",
        {
            "cash": cash,
            "cash_total": cash_total,
            "card_total": card_total,
            "transfer_total": transfer_total,
            "total_sales": total_sales,
        }
    )
