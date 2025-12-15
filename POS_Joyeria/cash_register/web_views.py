from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from django.db.models import Sum, Count
from sales.models import Sale
from .models import CashRegister
from utils.roles import role_required
from decimal import Decimal

PAYMENT_LABELS = {
    "CASH": "Efectivo",
    "CARD": "Tarjeta",
    "TRANSFER": "Transferencia",
}

#Estado de la caja (abierta/cerrada)
@role_required(["AdminPOS", "VendedorPOS"])
def cash_status(request):
    cash = CashRegister.objects.filter(is_closed=False).first()

    if not cash:
        return redirect("cash_register_web:open")

    sales = Sale.objects.filter(
        status=Sale.Status.PAID,
        created_at__gte=cash.opened_at,
        created_at__lte=timezone.now()
    )

    if not request.user.groups.filter(name="AdminPOS").exists():
        sales = sales.filter(user=request.user)

    resumen = sales.aggregate(
        total=Sum("total"),
        cantidad=Count("id")
    )
    por_pago_raw = sales.values("payment_method").annotate(
        total=Sum("total"),
        cantidad=Count("id")
    )
    por_pago = []
    for p in por_pago_raw:
        por_pago.append({
            "label": PAYMENT_LABELS.get(
                p["payment_method"],
                p["payment_method"]
            ),
            "total": p["total"],
            "cantidad": p["cantidad"],
        })

    por_vendedor = sales.values(
        "user__username"
    ).annotate(
        total=Sum("total"),
        cantidad=Count("id")
    )

    return render(
        request,
        "cash_register/status.html",
        {
            "cash": cash,
            "resumen": resumen,
            "por_pago": por_pago,
            "por_vendedor": por_vendedor,
        }
    )

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

    cash_total = sum(
        (s.total for s in sales if s.payment_method == "CASH"),
        Decimal("0")
    )
    card_total = sum(
        (s.total for s in sales if s.payment_method == "CARD"),
        Decimal("0")
    )
    transfer_total = sum(
        (s.total for s in sales if s.payment_method == "TRANSFER"),
        Decimal("0")
    )
    total_sales = sum(
        (s.total for s in sales),
        Decimal("0")
    )

    if request.method == "POST":
        # convertir a dec
        closing_amount = Decimal(
            request.POST.get("closing_amount", "0")
        ).quantize(Decimal("0.01"))

        # VALIDACIÓN AQUI
        if closing_amount < 0:
            messages.error(
                request,
                "El monto de cierre no puede ser negativo."
            )
            return redirect("cash_register_web:close")

        # cálculos seguros
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