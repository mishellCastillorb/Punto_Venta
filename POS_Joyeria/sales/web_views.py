from decimal import Decimal
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from utils.roles import role_required
from products.models import Product

SESSION_KEY = "pos_ticket"

def _d(v, default="0"):
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal(default)

def _init_ticket():
    return {"items": {}, "cliente": None, "descuento": "0", "metodo_pago": None, "cantidad_pagada": None}

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
    return None  # si tu Product no tiene stock, no validamos aquí

def _build_ticket_context(ticket):
    items_dict = ticket.get("items") or {}
    descuento = _d(ticket.get("descuento") or "0")

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
        ticket_items.append({"id": pid, "name": name, "price": price, "qty": qty_int, "line_total": line_total})

    if descuento < 0:
        descuento = Decimal("0")
    if descuento > subtotal:
        descuento = subtotal
    total = subtotal - descuento

    cliente_display = "Sin cliente"
    c = ticket.get("cliente")
    if isinstance(c, dict):
        if c.get("id"):
            cliente_display = f"Cliente registrado (ID {c.get('id')})"
        else:
            nombre = (c.get("nombre") or "").strip()
            tel = (c.get("telefono") or "").strip()
            if nombre and tel:
                cliente_display = f"{nombre} ({tel})"
            elif nombre:
                cliente_display = nombre

    return ticket_items, subtotal, descuento, total, cliente_display
def _get_product_image_url(p):
    img = getattr(p, "image", None)
    if img is None:
        img = getattr(p, "imagen", None)
    try:
        return img.url if img else None
    except Exception:
        return None

def _search_products(q):
    if not q:
        return []
    qs = Product.objects.all()
    results = []
    # Buscar por código primero
    try:
        results = list(qs.filter(code__icontains=q)[:20])
    except Exception:
        try:
            results = list(qs.filter(codigo__icontains=q)[:20])
        except Exception:
            results = []
    # Si no encontró, buscar por nombre
    if not results:
        try:
            results = list(qs.filter(name__icontains=q)[:20])
        except Exception:
            try:
                results = list(qs.filter(nombre__icontains=q)[:20])
            except Exception:
                results = []
    # Transformar a dict para template
    out = []
    for p in results:
        out.append({
            "id": p.id,
            "name": _get_product_name(p),
            "price": _get_product_price(p),
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

    ticket_items, subtotal, descuento, total, cliente_display = _build_ticket_context(ticket)

    context = {
        "is_adminpos": _is_adminpos(request.user),
        "ticket_items": ticket_items,
        "subtotal": subtotal,
        "descuento": descuento,
        "total": total,
        "cliente_display": cliente_display,
        "sale_number": "Pendiente",
        "q": q,
        "search_results": search_results,
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
    if new_qty < 1:
        new_qty = 1

    # Validación stock (si existe)
    try:
        p = Product.objects.get(id=product_id)
        stock = _get_product_stock(p)
        if stock is not None and new_qty > stock:
            # No sube más del stock disponible
            new_qty = stock if stock > 0 else current
    except Product.DoesNotExist:
        return redirect(reverse("sales:pos"))

    items[key] = new_qty
    ticket["items"] = items
    request.session[SESSION_KEY] = ticket
    request.session.modified = True

    q = (request.POST.get("q") or "").strip()
    url = reverse("sales:pos")
    if q:
        url = f"{url}?q={q}"
    return redirect(url)
