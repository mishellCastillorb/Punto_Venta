from decimal import Decimal
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.utils import timezone
from datetime import timedelta
from utils.roles import role_required
from products.models import Product
from client.models import Client
from .models import Sale, SaleItem

SESSION_KEY = "pos_ticket"


def _d(v, default="0"):
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal(default)


def _init_ticket():
    return {
        "items": {},
        "cliente": None,           # {"id": X} o {"name": "...", "phone": "..."}
        "descuento_pct": "0",
        "metodo_pago": "CASH",     # CASH / CARD / TRANSFER
        "cantidad_pagada": "",
    }

def _is_adminpos(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name="AdminPOS").exists()

def _get_product_price(p):
    for attr in ("sale_price", "precio_venta", "price", "precio"):
        if hasattr(p, attr):
            return _d(getattr(p, attr) or "0")
    return Decimal("0")


def _get_product_name(p):
    name = getattr(p, "name", None)
    if name is None:
        name = getattr(p, "nombre", None)
    return name or str(p)

def _get_product_stock(p):
    for attr in ("stock", "existencias", "quantity", "cantidad"):
        if hasattr(p, attr):
            try:
                return int(getattr(p, attr) or 0)
            except Exception:
                return 0
    return None

def _set_product_stock(p, new_value: int):
    for attr in ("stock", "existencias", "quantity", "cantidad"):
        if hasattr(p, attr):
            setattr(p, attr, int(new_value))
            return attr
    return None

def _get_product_image_url(p):
    img = getattr(p, "image", None)
    if img is None:
        img = getattr(p, "imagen", None)
    try:
        return img.url if img else None
    except Exception:
        return None

def _redirect_pos_with_q(request):
    q = (request.POST.get("q") or "").strip()
    url = reverse("sales:pos")
    if q:
        url = f"{url}?q={q}"
    return redirect(url)

def _cliente_display_from_ticket(ticket):
    c = ticket.get("cliente")
    if isinstance(c, dict):
        if c.get("id"):
            return f"Cliente registrado (ID {c.get('id')})"
        name = (c.get("name") or "").strip()
        phone = (c.get("phone") or "").strip()
        if name and phone:
            return f"{name} ({phone})"
        if name:
            return name
    return "Sin cliente"

def _build_ticket_context(ticket):
    items_dict = ticket.get("items") or {}
    descuento_pct = _d(ticket.get("descuento_pct") or "0")
    if descuento_pct < 0:
        descuento_pct = Decimal("0")
    if descuento_pct > 100:
        descuento_pct = Decimal("100")
    metodo_pago = (ticket.get("metodo_pago") or "CASH").upper()
    if metodo_pago not in ("CASH", "CARD", "TRANSFER"):
        metodo_pago = "CASH"
    cantidad_pagada_raw = (ticket.get("cantidad_pagada") or "").strip()
    cantidad_pagada = _d(cantidad_pagada_raw, default="0") if cantidad_pagada_raw else Decimal("0")
    product_ids = []
    for pid in items_dict.keys():
        try:
            product_ids.append(int(pid))
        except Exception:
            continue
    products = Product.objects.filter(id__in=product_ids)
    products_by_id = {p.id: p for p in products}
    ticket_items, subtotal = [], Decimal("0")
    for pid_str, qty in items_dict.items():
        try:
            pid, qty_int = int(pid_str), int(qty)
        except Exception:
            continue
        if qty_int < 1:
            qty_int = 1
        p = products_by_id.get(pid)
        if not p:
            continue
        price = _get_product_price(p)
        name = _get_product_name(p)
        line_total = price * Decimal(qty_int)
        subtotal += line_total
        ticket_items.append({
            "id": pid,
            "name": name,
            "price": price.quantize(Decimal("0.01")),
            "qty": qty_int,
            "line_total": line_total.quantize(Decimal("0.01")),
        })
    subtotal = subtotal.quantize(Decimal("0.01"))
    descuento_monto = (subtotal * (descuento_pct / Decimal("100"))).quantize(Decimal("0.01")) if subtotal > 0 else Decimal("0.00")
    total = (subtotal - descuento_monto).quantize(Decimal("0.01"))

    # CAMBIO
    cambio = Decimal("0.00")
    faltante = Decimal("0.00")
    if cantidad_pagada < total:
        faltante = (total - cantidad_pagada).quantize(Decimal("0.01"))
    else:
        cambio = (cantidad_pagada - total).quantize(Decimal("0.01"))
    has_items = len(ticket_items) > 0
    can_charge = has_items and (faltante == Decimal("0.00")) and (total >= Decimal("0.00"))

    return {
        "ticket_items": ticket_items,
        "subtotal": subtotal,
        "descuento_pct": descuento_pct.quantize(Decimal("0.01")),
        "descuento_monto": descuento_monto,
        "total": total,
        "metodo_pago": metodo_pago,
        "cantidad_pagada": cantidad_pagada.quantize(Decimal("0.01")),
        "cantidad_pagada_raw": cantidad_pagada_raw,
        "cambio": cambio,
        "faltante": faltante,
        "cliente_display": _cliente_display_from_ticket(ticket),
        "can_charge": can_charge,
        "has_items": has_items,
    }

def _search_products(q):
    q = (q or "").strip()
    if not q:
        return []
    qs = Product.objects.all()
    q_up = q.upper()
    is_digits_only = q.isdigit()
    has_letters = any(ch.isalpha() for ch in q)
    results = []
    if has_letters and not is_digits_only:
        if hasattr(Product, "code"):
            results = list(qs.filter(code__istartswith=q_up)[:20])
        elif hasattr(Product, "codigo"):
            results = list(qs.filter(codigo__istartswith=q_up)[:20])

    if not results:
        tokens = [t.strip() for t in q.split() if len(t.strip()) >= 3] or [t.strip() for t in q.split() if len(t.strip()) >= 2]
        if not tokens:
            return []

        name_q = Q()
        for t in tokens:
            if hasattr(Product, "name"):
                name_q |= Q(name__icontains=t)
            if hasattr(Product, "nombre"):
                name_q |= Q(nombre__icontains=t)

        results = list(qs.filter(name_q)[:20])

    out = []
    for p in results:
        out.append({
            "id": p.id,
            "name": _get_product_name(p),
            "price": _get_product_price(p).quantize(Decimal("0.01")),
            "stock": _get_product_stock(p),
            "image_url": _get_product_image_url(p),
        })
    return out

@role_required(["AdminPOS", "VendedorPOS"])
def pos_view(request):
    ticket = request.session.get(SESSION_KEY)
    if not isinstance(ticket, dict) or "items" not in ticket:
        ticket = _init_ticket()
        request.session[SESSION_KEY] = ticket
        request.session.modified = True

    q = (request.GET.get("q") or "").strip()
    search_results = _search_products(q)
    tc = _build_ticket_context(ticket)

    context = {
        "is_adminpos": _is_adminpos(request.user),
        "sale_number": "Pendiente",
        "q": q,
        "search_results": search_results,
        **tc,
    }
    return render(request, "sales/pos.html", context)


@require_POST
@role_required(["AdminPOS", "VendedorPOS"])
def add_to_ticket(request, product_id: int):
    ticket = request.session.get(SESSION_KEY)
    if not isinstance(ticket, dict) or "items" not in ticket:
        ticket = _init_ticket()

    items = ticket.get("items") or {}
    key = str(product_id)
    current = int(items.get(key) or 0)
    new_qty = current + 1

    try:
        p = Product.objects.get(id=product_id)
        stock = _get_product_stock(p)

        if stock is not None:
            if stock <= 0:
                messages.error(request, "Este producto no tiene stock disponible.")
                return _redirect_pos_with_q(request)

            if new_qty > stock:
                messages.error(request, f"Stock máximo alcanzado (disponible: {stock}).")
                new_qty = stock
    except Product.DoesNotExist:
        return redirect(reverse("sales:pos"))

    items[key] = max(new_qty, 1)
    ticket["items"] = items
    request.session[SESSION_KEY] = ticket
    request.session.modified = True

    return _redirect_pos_with_q(request)


@require_POST
@role_required(["AdminPOS", "VendedorPOS"])
def dec_ticket_item(request, product_id: int):
    ticket = request.session.get(SESSION_KEY)
    if not isinstance(ticket, dict) or "items" not in ticket:
        return _redirect_pos_with_q(request)

    items = ticket.get("items") or {}
    key = str(product_id)

    if key not in items:
        return _redirect_pos_with_q(request)

    current = int(items.get(key) or 0)
    new_qty = current - 1

    if new_qty <= 0:
        items.pop(key, None)
    else:
        items[key] = new_qty

    ticket["items"] = items
    request.session[SESSION_KEY] = ticket
    request.session.modified = True

    return _redirect_pos_with_q(request)

@require_POST
@role_required(["AdminPOS", "VendedorPOS"])
def remove_from_ticket(request, product_id: int):
    ticket = request.session.get(SESSION_KEY)
    if not isinstance(ticket, dict) or "items" not in ticket:
        return _redirect_pos_with_q(request)

    items = ticket.get("items") or {}
    items.pop(str(product_id), None)

    ticket["items"] = items
    request.session[SESSION_KEY] = ticket
    request.session.modified = True

    return _redirect_pos_with_q(request)

@require_POST
@role_required(["AdminPOS", "VendedorPOS"])
def ajax_update_ticket(request):
    ticket = request.session.get(SESSION_KEY)
    if not isinstance(ticket, dict) or "items" not in ticket:
        ticket = _init_ticket()

    descuento_pct = (request.POST.get("descuento_pct") or "").strip()
    metodo_pago = (request.POST.get("metodo_pago") or "CASH").upper().strip()
    cantidad_pagada = (request.POST.get("cantidad_pagada") or "").strip()

    d_pct = _d(descuento_pct, default="0")
    if d_pct < 0:
        d_pct = Decimal("0")
    if d_pct > 100:
        d_pct = Decimal("100")

    if metodo_pago not in ("CASH", "CARD", "TRANSFER"):
        metodo_pago = "CASH"

    ticket["descuento_pct"] = str(d_pct)
    ticket["metodo_pago"] = metodo_pago
    ticket["cantidad_pagada"] = cantidad_pagada  # ✅ SIEMPRE

    request.session[SESSION_KEY] = ticket
    request.session.modified = True

    tc = _build_ticket_context(ticket)

    return JsonResponse({
        "ok": True,
        "has_items": tc["has_items"],
        "subtotal": str(tc["subtotal"]),
        "descuento_pct": str(tc["descuento_pct"]),
        "descuento_monto": str(tc["descuento_monto"]),
        "total": str(tc["total"]),
        "metodo_pago": tc["metodo_pago"],
        "cantidad_pagada": str(tc["cantidad_pagada"]),
        "cambio": str(tc["cambio"]),
        "faltante": str(tc["faltante"]),
        "can_charge": tc["can_charge"],
    })

@require_POST
@role_required(["AdminPOS", "VendedorPOS"])
def client_quick(request):
    ticket = request.session.get(SESSION_KEY)
    if not isinstance(ticket, dict) or "items" not in ticket:
        ticket = _init_ticket()

    name = (request.POST.get("name") or "").strip()
    phone = (request.POST.get("phone") or "").strip()

    if not name:
        messages.error(request, "El nombre del cliente rápido es obligatorio.")
        return _redirect_pos_with_q(request)

    ticket["cliente"] = {"name": name, "phone": phone}
    request.session[SESSION_KEY] = ticket
    request.session.modified = True

    messages.success(request, "Cliente rápido asignado.")
    return _redirect_pos_with_q(request)

@require_POST
@role_required(["AdminPOS", "VendedorPOS"])
def client_clear(request):
    ticket = request.session.get(SESSION_KEY)
    if not isinstance(ticket, dict) or "items" not in ticket:
        ticket = _init_ticket()

    ticket["cliente"] = None
    request.session[SESSION_KEY] = ticket
    request.session.modified = True

    messages.success(request, "Cliente removido.")
    return _redirect_pos_with_q(request)

@role_required(["AdminPOS", "VendedorPOS"])
def client_search(request):
    q = (request.GET.get("q") or "").strip()
    if not q or len(q) < 2:
        return JsonResponse({"ok": True, "results": []})

    q_digits = "".join(ch for ch in q if ch.isdigit())
    has_phone_query = len(q_digits) >= 3

    tokens = [t for t in q.split() if t]
    qq = Q()

    if any(ch.isalpha() for ch in q):
        for t in tokens:
            qq |= (
                Q(name__icontains=t) |
                Q(apellido_paterno__icontains=t) |
                Q(apellido_materno__icontains=t)
            )

    if has_phone_query:
        qq |= Q(phone__icontains=q_digits)

    if qq == Q():
        return JsonResponse({"ok": True, "results": []})

    clients = Client.objects.filter(qq, is_active=True).order_by("name")[:20]
    out = []
    for c in clients:
        full_name = " ".join(x for x in [c.name, c.apellido_paterno, c.apellido_materno] if x).strip()
        out.append({
            "id": c.id,
            "name": full_name or c.name,
            "phone": c.phone or "",
        })
    return JsonResponse({"ok": True, "results": out})

@require_POST
@role_required(["AdminPOS", "VendedorPOS"])
def client_select(request, client_id: int):
    ticket = request.session.get(SESSION_KEY)
    if not isinstance(ticket, dict) or "items" not in ticket:
        ticket = _init_ticket()

    c = get_object_or_404(Client, id=client_id, is_active=True)
    ticket["cliente"] = {"id": c.id}

    request.session[SESSION_KEY] = ticket
    request.session.modified = True

    messages.success(request, "Cliente registrado asignado.")
    return _redirect_pos_with_q(request)

@require_POST
@role_required(["AdminPOS", "VendedorPOS"])
def cobrar_sale(request):
    ticket = request.session.get(SESSION_KEY)
    if not isinstance(ticket, dict) or "items" not in ticket:
        messages.error(request, "El ticket no es válido.")
        return redirect(reverse("sales:pos"))

    descuento_pct = (request.POST.get("descuento_pct") or "").strip()
    metodo_pago = (request.POST.get("metodo_pago") or "CASH").upper().strip()
    cantidad_pagada = (request.POST.get("cantidad_pagada") or "").strip()

    d_pct = _d(descuento_pct, default="0")
    if d_pct < 0:
        d_pct = Decimal("0")
    if d_pct > 100:
        d_pct = Decimal("100")

    if metodo_pago not in ("CASH", "CARD", "TRANSFER"):
        metodo_pago = "CASH"

    ticket["descuento_pct"] = str(d_pct)
    ticket["metodo_pago"] = metodo_pago
    ticket["cantidad_pagada"] = cantidad_pagada

    request.session[SESSION_KEY] = ticket
    request.session.modified = True

    tc = _build_ticket_context(ticket)

    if not tc["has_items"]:
        messages.error(request, "El ticket está vacío.")
        return redirect(reverse("sales:pos"))

    c = ticket.get("cliente")
    if not isinstance(c, dict) or (not c.get("id") and not (c.get("name") or "").strip()):
        messages.error(request, "Debes asignar un cliente para poder cobrar.")
        return redirect(reverse("sales:pos"))

    if tc["faltante"] != Decimal("0.00"):
        messages.error(request, "Falta dinero para completar el pago.")
        return redirect(reverse("sales:pos"))

    items = tc["ticket_items"]

    try:
        with transaction.atomic():
            product_ids = [it["id"] for it in items]
            products = list(Product.objects.select_for_update().filter(id__in=product_ids))
            products_by_id = {p.id: p for p in products}

            for it in items:
                p = products_by_id.get(it["id"])
                if not p:
                    raise ValueError("Producto no encontrado.")

                stock = _get_product_stock(p)
                if stock is not None and it["qty"] > stock:
                    raise ValueError(f"Stock insuficiente para: {_get_product_name(p)} (disp: {stock}).")

            sale = Sale.objects.create(
                user=request.user,
                status=Sale.Status.PAID,
                discount_pct=tc["descuento_pct"],
                subtotal=tc["subtotal"],
                discount_amount=tc["descuento_monto"],
                total=tc["total"],
                payment_method=tc["metodo_pago"],
                amount_paid=tc["cantidad_pagada"],
                change_amount=tc["cambio"],
            )

            if c.get("id"):
                sale.client_id = int(c["id"])
            else:
                sale.quick_client_name = (c.get("name") or "").strip()
                sale.quick_client_phone = (c.get("phone") or "").strip()
            sale.save(update_fields=["client", "quick_client_name", "quick_client_phone"])

            for it in items:
                p = products_by_id[it["id"]]
                unit_price = _get_product_price(p).quantize(Decimal("0.01"))
                line_total = (unit_price * Decimal(it["qty"])).quantize(Decimal("0.01"))

                SaleItem.objects.create(
                    sale=sale,
                    product=p,
                    product_name=_get_product_name(p),
                    unit_price=unit_price,
                    qty=it["qty"],
                    line_total=line_total,
                )

                stock = _get_product_stock(p)
                if stock is not None:
                    new_stock = stock - int(it["qty"])
                    stock_field = _set_product_stock(p, new_stock)
                    if stock_field:
                        p.save(update_fields=[stock_field])

            sale.folio = f"V{sale.id:06d}"
            sale.save(update_fields=["folio"])

    except ValueError as e:
        messages.error(request, str(e))
        return redirect(reverse("sales:pos"))

    request.session[SESSION_KEY] = _init_ticket()
    request.session.modified = True

    return redirect(reverse("sales:success", args=[sale.id]))

@role_required(["AdminPOS", "VendedorPOS"])
def sale_success(request, sale_id: int):
    sale = get_object_or_404(Sale.objects.prefetch_related("items").select_related("client", "user"), id=sale_id)

    if sale.client_id:
        c = sale.client
        cliente_display = " ".join([x for x in [c.name, c.apellido_paterno, c.apellido_materno] if x]).strip()
        cliente_phone = c.phone or ""
    else:
        cliente_display = sale.quick_client_name or "Sin cliente"
        cliente_phone = sale.quick_client_phone or ""

    back_to_list = request.GET.get("from") == "list"
    back_url = reverse("sales:ventas_list") if back_to_list else reverse("sales:pos")
    back_label = "← Volver a ventas" if back_to_list else "Volver al POS"

    return render(request, "sales/sale_success.html", {
        "sale": sale,
        "cliente_display": cliente_display,
        "cliente_phone": cliente_phone,
        "back_url": back_url,
        "back_label": back_label,
    })


@role_required(["AdminPOS", "VendedorPOS"])
def sales_list(request):
    qs = Sale.objects.select_related("user").order_by("-created_at")

    folio = (request.GET.get("folio") or "").strip()
    vendedor = (request.GET.get("vendedor") or "").strip()
    date_from = (request.GET.get("from") or "").strip()
    date_to = (request.GET.get("to") or "").strip()

    if folio:
        qs = qs.filter(folio__icontains=folio)

    if vendedor:
        qs = qs.filter(user__username__icontains=vendedor)

    d1 = parse_date(date_from) if date_from else None
    d2 = parse_date(date_to) if date_to else None

    if d1:
        qs = qs.filter(created_at__date__gte=d1)
    if d2:
        qs = qs.filter(created_at__date__lte=d2)

    return render(request, "sales/lista_ventas.html", {
        "sales": qs[:500],
        "filters": {"folio": folio, "vendedor": vendedor, "from": date_from, "to": date_to},
    })

@role_required(["AdminPOS", "VendedorPOS"])
def sales_list(request):
    qs = Sale.objects.select_related("user").order_by("-created_at")

    vendedor = (request.GET.get("vendedor") or "").strip()
    periodo = (request.GET.get("periodo") or "hoy").strip()  # hoy|ayer|semana|mes

    if vendedor:
        qs = qs.filter(user__username__icontains=vendedor)

    # Filtro periodo
    now = timezone.localtime(timezone.now())
    today = now.date()

    if periodo == "ayer":
        d = today - timedelta(days=1)
        qs = qs.filter(created_at__date=d)

    elif periodo == "semana":
        # inicio de semana (lunes)
        start = today - timedelta(days=today.weekday())
        qs = qs.filter(created_at__date__gte=start, created_at__date__lte=today)

    elif periodo == "mes":
        start = today.replace(day=1)
        qs = qs.filter(created_at__date__gte=start, created_at__date__lte=today)

    else:
        # hoy (default)
        qs = qs.filter(created_at__date=today)
        periodo = "hoy"

    return render(request, "sales/lista_ventas.html", {
        "sales": qs[:500],
        "filters": {"vendedor": vendedor, "periodo": periodo},
    })

@require_POST
@role_required(["AdminPOS"])
def cancel_sale(request, sale_id: int):
    sale = get_object_or_404(
        Sale.objects.select_related("user").prefetch_related("items__product"),
        id=sale_id
    )

    if sale.status == Sale.Status.CANCELLED:
        messages.info(request, "Esta venta ya estaba cancelada.")
        return redirect(reverse("sales:ventas_list"))

    if sale.status != Sale.Status.PAID:
        messages.error(request, "Solo se pueden cancelar ventas pagadas.")
        return redirect(reverse("sales:ventas_list"))

    try:
        with transaction.atomic():
            sale = Sale.objects.select_for_update().get(id=sale_id)

            if sale.status == Sale.Status.CANCELLED:
                messages.info(request, "Esta venta ya estaba cancelada.")
                return redirect(reverse("sales:ventas_list"))

            items = list(SaleItem.objects.select_related("product").select_for_update().filter(sale=sale))

            # Regresar stock por cada item
            for it in items:
                p = it.product
                stock = _get_product_stock(p)

                if stock is not None:
                    new_stock = int(stock) + int(it.qty)
                    stock_field = _set_product_stock(p, new_stock)
                    if stock_field:
                        p.save(update_fields=[stock_field])

            sale.status = Sale.Status.CANCELLED
            sale.save(update_fields=["status"])

        messages.success(request, f"Venta {sale.folio or sale.id} cancelada y stock restaurado.")
    except Exception:
        messages.error(request, "No se pudo cancelar la venta. Intenta de nuevo.")

    return redirect(reverse("sales:ventas_list"))
