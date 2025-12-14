from decimal import Decimal
from datetime import timedelta
from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from client.models import Client
from products.models import Category, Material, Product
from suppliers.models import Supplier
from .models import Sale, SaleItem
from .web_views import (
    SESSION_KEY,
    _d, _init_ticket, _is_adminpos,
    _get_product_price, _get_product_name, _get_product_stock, _set_product_stock,
    _get_product_image_url, _redirect_pos_with_q, _cliente_display_from_ticket, _build_ticket_context, _search_products
)


class SalesModelsTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Anillos")
        self.material = Material.objects.create(name="Plata", purity="925")
        self.supplier = Supplier.objects.create(
            name="Proveedor Joyas",
            code="V01",
            phone="5550001111",
            email="proveedor@test.com",
        )
        self.producto1 = Product.objects.create(
            name="Anillo Plata",
            code="ANP01",
            category=self.category,
            purchase_price=200,
            sale_price=Decimal("500.00"),
            weight=10,
            stock=20,
            supplier=self.supplier,
            material=self.material,
        )
        self.user = User.objects.create_user(username="vendedor1", password="12345678")

    def test_str_sale_con_folio(self):
        venta = Sale.objects.create(user=self.user, folio="V000001")
        self.assertEqual(str(venta), "V000001")

    def test_str_sale_sin_folio(self):
        venta = Sale.objects.create(user=self.user)
        self.assertIn("Venta #", str(venta))

    def test_saleitem_str(self):
        venta = Sale.objects.create(user=self.user, folio="V000010")
        item = SaleItem.objects.create(
            sale=venta,
            product=self.producto1,
            product_name="Anillo Plata",
            unit_price=Decimal("500.00"),
            qty=2,
            line_total=Decimal("1000.00"),
        )
        self.assertIn("Anillo Plata", str(item))
        self.assertIn("x2", str(item))


class SalesHelpersTest(TestCase):
    def test_d_parsea_y_default(self):
        self.assertEqual(_d("10.5"), Decimal("10.5"))
        self.assertEqual(_d("nope", default="7"), Decimal("7"))

    def test_init_ticket_formato(self):
        t = _init_ticket()
        self.assertIn("items", t)
        self.assertIn("cliente", t)
        self.assertEqual(t["metodo_pago"], "CASH")

    def test_is_adminpos(self):
        g = Group.objects.create(name="AdminPOS")
        u = User.objects.create_user(username="u1", password="12345678")
        su = User.objects.create_superuser(username="su", password="12345678", email="su@test.com")

        self.assertFalse(_is_adminpos(u))
        u.groups.add(g)
        self.assertTrue(_is_adminpos(u))
        self.assertTrue(_is_adminpos(su))

    def test_product_helpers_fallbacks(self):
        class PNoFields:
            def __str__(self):
                return "X"

        p = PNoFields()
        self.assertEqual(_get_product_price(p), Decimal("0"))
        self.assertEqual(_get_product_name(p), "X")
        self.assertIsNone(_get_product_stock(p))
        self.assertIsNone(_set_product_stock(p, 10))

    def test_get_product_stock_except(self):
        class PBadStock:
            stock = "no-int"

        self.assertEqual(_get_product_stock(PBadStock()), 0)

    def test_get_product_image_url_except(self):
        class BadImg:
            @property
            def url(self):
                raise ValueError("boom")

        class P:
            image = BadImg()

        self.assertIsNone(_get_product_image_url(P()))

    def test_redirect_pos_with_q(self):
        u = User.objects.create_user(username="vend", password="12345678")
        g = Group.objects.create(name="VendedorPOS")
        u.groups.add(g)

        self.client.force_login(u)
        # sin q
        res1 = self.client.post(reverse("sales:add", args=[999999]), data={"q": ""})
        self.assertEqual(res1.status_code, 302)

    def test_cliente_display_ramas(self):
        self.assertEqual(_cliente_display_from_ticket({"cliente": None}), "Sin cliente")
        self.assertIn("ID", _cliente_display_from_ticket({"cliente": {"id": 7}}))
        self.assertEqual(_cliente_display_from_ticket({"cliente": {"name": "Ana"}}), "Ana")
        self.assertEqual(_cliente_display_from_ticket({"cliente": {"name": "Ana", "phone": "555"}}), "Ana (555)")

    def test_build_ticket_context_clamps_y_totales(self):
        ticket = {
            "items": {"x": 2, "1": 0},
            "cliente": {"name": "Ana"},
            "descuento_pct": "-10",
            "metodo_pago": "INVALIDO",
            "cantidad_pagada": "",
        }
        tc = _build_ticket_context(ticket)
        self.assertEqual(tc["descuento_pct"], Decimal("0.00"))
        self.assertEqual(tc["metodo_pago"], "CASH")
        self.assertEqual(tc["cantidad_pagada"], Decimal("0.00"))

        ticket2 = {
            "items": {},
            "cliente": None,
            "descuento_pct": "999",
            "metodo_pago": "CARD",
            "cantidad_pagada": "0",
        }
        tc2 = _build_ticket_context(ticket2)
        self.assertEqual(tc2["descuento_pct"], Decimal("100.00"))

    def test_search_products_ramas(self):
        cat = Category.objects.create(name="Anillos")
        mat = Material.objects.create(name="Plata", purity="925")
        sup = Supplier.objects.create(name="Prov", code="P1", phone="555", email="p@test.com")

        Product.objects.create(
            name="Anillo ABC",
            code="ABC01",
            category=cat,
            purchase_price=10,
            sale_price=Decimal("100.00"),
            weight=1,
            stock=5,
            supplier=sup,
            material=mat,
        )
        Product.objects.create(
            name="123 Gold",
            code="NUM01",
            category=cat,
            purchase_price=10,
            sale_price=Decimal("100.00"),
            weight=1,
            stock=5,
            supplier=sup,
            material=mat,
        )

        self.assertEqual(_search_products(""), [])
        self.assertEqual(_search_products("  -  "), [])
        r_code = _search_products("abc")
        self.assertTrue(len(r_code) >= 1)

        r_num = _search_products("123")
        self.assertTrue(any("123" in x["name"] for x in r_num))


class SalesWebViewsTest(TestCase):
    def setUp(self):
        self.grp_admin = Group.objects.create(name="AdminPOS")
        self.grp_vendedor = Group.objects.create(name="VendedorPOS")

        self.user_admin = User.objects.create_user(username="admin1", password="12345678")
        self.user_admin.groups.add(self.grp_admin)

        self.user_vendedor = User.objects.create_user(username="vend1", password="12345678")
        self.user_vendedor.groups.add(self.grp_vendedor)

        self.user_sin_rol = User.objects.create_user(username="sinrol", password="12345678")

        self.category = Category.objects.create(name="Anillos")
        self.material = Material.objects.create(name="Plata", purity="925")
        self.supplier = Supplier.objects.create(
            name="Proveedor Joyas",
            code="V01",
            phone="5550001111",
            email="proveedor@test.com",
        )

        self.p1 = Product.objects.create(
            name="Anillo Plata",
            code="ANP01",
            category=self.category,
            purchase_price=200,
            sale_price=Decimal("500.00"),
            weight=10,
            stock=5,
            supplier=self.supplier,
            material=self.material,
        )
        self.p2 = Product.objects.create(
            name="Anillo Oro",
            code="ANO02",
            category=self.category,
            purchase_price=400,
            sale_price=Decimal("900.00"),
            weight=12,
            stock=2,
            supplier=self.supplier,
            material=self.material,
        )
        self.p_sin_stock = Product.objects.create(
            name="Sin Stock",
            code="SS01",
            category=self.category,
            purchase_price=100,
            sale_price=Decimal("100.00"),
            weight=1,
            stock=0,
            supplier=self.supplier,
            material=self.material,
        )

        self.client_reg = Client.objects.create(
            name="Juan",
            apellido_paterno="Pérez",
            apellido_materno="Gómez",
            phone="5559998888",
            email="juan@test.com",
            rfc="ABC123",
            is_active=True,
        )
        self.client_inactivo = Client.objects.create(
            name="Inactivo",
            apellido_paterno="X",
            apellido_materno="Y",
            phone="5550000000",
            email="ina@test.com",
            rfc="INA123",
            is_active=False,
        )

    def _login(self, user):
        self.client.force_login(user)

    def _set_ticket(self, *, items=None, cliente=None, descuento_pct="0", metodo_pago="CASH", cantidad_pagada=""):
        s = self.client.session
        s[SESSION_KEY] = {
            "items": items or {},
            "cliente": cliente,
            "descuento_pct": str(descuento_pct),
            "metodo_pago": metodo_pago,
            "cantidad_pagada": str(cantidad_pagada),
        }
        s.save()

    def test_pos_requires_role(self):
        url = reverse("sales:pos")
        self._login(self.user_sin_rol)
        res = self.client.get(url)
        self.assertIn(res.status_code, (302, 403))

        self.client.logout()
        self._login(self.user_vendedor)
        res2 = self.client.get(url)
        self.assertEqual(res2.status_code, 200)

    def test_pos_crea_ticket_en_sesion(self):
        self._login(self.user_vendedor)
        res = self.client.get(reverse("sales:pos"))
        self.assertEqual(res.status_code, 200)
        self.assertIn(SESSION_KEY, self.client.session)

    def test_add_to_ticket_stock_cero(self):
        self._login(self.user_vendedor)
        self._set_ticket(items={})
        res = self.client.post(reverse("sales:add", args=[self.p_sin_stock.id]), data={"q": ""})
        self.assertEqual(res.status_code, 302)
        s = self.client.session[SESSION_KEY]
        self.assertEqual(s["items"], {})

    def test_add_to_ticket_respeta_stock(self):
        self._login(self.user_vendedor)
        url_add = reverse("sales:add", args=[self.p2.id])
        self.client.post(url_add, data={"q": ""})
        self.client.post(url_add, data={"q": ""})
        self.client.post(url_add, data={"q": ""})
        s = self.client.session[SESSION_KEY]
        self.assertEqual(int(s["items"][str(self.p2.id)]), 2)

    def test_dec_key_no_existe(self):
        self._login(self.user_vendedor)
        self._set_ticket(items={})
        res = self.client.post(reverse("sales:dec", args=[self.p1.id]), data={"q": ""})
        self.assertEqual(res.status_code, 302)

    def test_dec_y_remove_ticket(self):
        self._login(self.user_vendedor)
        self._set_ticket(items={str(self.p1.id): 2})

        self.client.post(reverse("sales:dec", args=[self.p1.id]), data={"q": ""})
        s = self.client.session[SESSION_KEY]
        self.assertEqual(int(s["items"][str(self.p1.id)]), 1)

        self.client.post(reverse("sales:dec", args=[self.p1.id]), data={"q": ""})
        s2 = self.client.session[SESSION_KEY]
        self.assertNotIn(str(self.p1.id), s2["items"])

        self._set_ticket(items={str(self.p1.id): 1})
        self.client.post(reverse("sales:remove", args=[self.p1.id]), data={"q": ""})
        s3 = self.client.session[SESSION_KEY]
        self.assertNotIn(str(self.p1.id), s3["items"])

    def test_remove_ticket_sin_ticket_valido(self):
        self._login(self.user_vendedor)
        s = self.client.session
        if SESSION_KEY in s:
            del s[SESSION_KEY]
            s.save()
        res = self.client.post(reverse("sales:remove", args=[self.p1.id]), data={"q": ""})
        self.assertEqual(res.status_code, 302)

    def test_ajax_update_ticket_normaliza(self):
        self._login(self.user_vendedor)
        self._set_ticket(items={str(self.p1.id): 1})

        res = self.client.post(reverse("sales:ajax_update"), data={
            "descuento_pct": "-5",
            "metodo_pago": "INVALIDO",
            "cantidad_pagada": "",
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["metodo_pago"], "CASH")
        self.assertEqual(Decimal(data["descuento_pct"]), Decimal("0"))

    def test_ajax_update_ticket_clamp_100(self):
        self._login(self.user_vendedor)
        self._set_ticket(items={str(self.p1.id): 1})
        res = self.client.post(reverse("sales:ajax_update"), data={
            "descuento_pct": "999",
            "metodo_pago": "CASH",
            "cantidad_pagada": "0",
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Decimal(res.json()["descuento_pct"]), Decimal("100"))

    def test_client_quick_requiere_nombre(self):
        self._login(self.user_vendedor)
        self._set_ticket(items={str(self.p1.id): 1})
        res = self.client.post(reverse("sales:client_quick"), data={"name": "", "phone": "555", "q": ""})
        self.assertEqual(res.status_code, 302)
        self.assertIsNone(self.client.session[SESSION_KEY]["cliente"])

    def test_client_quick_ok(self):
        self._login(self.user_vendedor)
        self._set_ticket(items={str(self.p1.id): 1})
        res = self.client.post(reverse("sales:client_quick"), data={"name": "Rápido", "phone": "555", "q": ""})
        self.assertEqual(res.status_code, 302)
        self.assertEqual(self.client.session[SESSION_KEY]["cliente"]["name"], "Rápido")

    def test_client_clear(self):
        self._login(self.user_vendedor)
        self._set_ticket(items={str(self.p1.id): 1}, cliente={"id": self.client_reg.id})
        res = self.client.post(reverse("sales:client_clear"), data={"q": ""})
        self.assertEqual(res.status_code, 302)
        self.assertIsNone(self.client.session[SESSION_KEY]["cliente"])

    def test_client_select_asigna_cliente(self):
        self._login(self.user_vendedor)
        self._set_ticket(items={str(self.p1.id): 1})
        res = self.client.post(reverse("sales:client_select", args=[self.client_reg.id]), data={"q": ""})
        self.assertEqual(res.status_code, 302)
        self.assertEqual(self.client.session[SESSION_KEY]["cliente"]["id"], self.client_reg.id)

    def test_client_select_inactivo_404(self):
        self._login(self.user_vendedor)
        self._set_ticket(items={str(self.p1.id): 1})
        res = self.client.post(reverse("sales:client_select", args=[self.client_inactivo.id]), data={"q": ""})
        self.assertEqual(res.status_code, 404)

    def test_client_search_ramas(self):
        self._login(self.user_vendedor)

        r1 = self.client.get(reverse("sales:client_search"), data={"q": "a"})
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r1.json()["results"], [])

        r2 = self.client.get(reverse("sales:client_search"), data={"q": "--"})
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2.json()["results"], [])

        r3 = self.client.get(reverse("sales:client_search"), data={"q": "999"})
        self.assertEqual(r3.status_code, 200)
        self.assertTrue(len(r3.json()["results"]) >= 1)

    def test_cobrar_ticket_invalido(self):
        self._login(self.user_vendedor)
        s = self.client.session
        s[SESSION_KEY] = "no-dict"
        s.save()

        res = self.client.post(reverse("sales:cobrar"), data={
            "descuento_pct": "0", "metodo_pago": "CASH", "cantidad_pagada": "0"
        })
        self.assertEqual(res.status_code, 302)
        self.assertEqual(Sale.objects.count(), 0)

    def test_cobrar_sale_ok_cliente_registrado(self):
        self._login(self.user_vendedor)
        self._set_ticket(
            items={str(self.p1.id): 2},
            cliente={"id": self.client_reg.id},
            descuento_pct="0",
            metodo_pago="CASH",
            cantidad_pagada="1000",
        )

        stock_before = Product.objects.get(id=self.p1.id).stock
        res = self.client.post(reverse("sales:cobrar"), data={
            "descuento_pct": "0", "metodo_pago": "CASH", "cantidad_pagada": "1000"
        })
        self.assertEqual(res.status_code, 302)

        sale = Sale.objects.first()
        self.assertEqual(Sale.objects.count(), 1)
        self.assertEqual(sale.status, Sale.Status.PAID)
        self.assertTrue(sale.folio.startswith("V"))
        self.assertEqual(sale.client_id, self.client_reg.id)
        self.assertEqual(SaleItem.objects.filter(sale=sale).count(), 1)

        p_after = Product.objects.get(id=self.p1.id)
        self.assertEqual(p_after.stock, stock_before - 2)

        t = self.client.session[SESSION_KEY]
        self.assertEqual(t["items"], {})
        self.assertIsNone(t["cliente"])

    def test_cobrar_sale_ok_cliente_rapido(self):
        self._login(self.user_vendedor)
        self._set_ticket(
            items={str(self.p1.id): 1},
            cliente={"name": "Cliente Rápido", "phone": "5551112222"},
            descuento_pct="0",
            metodo_pago="CASH",
            cantidad_pagada="500",
        )
        res = self.client.post(reverse("sales:cobrar"), data={
            "descuento_pct": "0", "metodo_pago": "CASH", "cantidad_pagada": "500"
        })
        self.assertEqual(res.status_code, 302)
        sale = Sale.objects.first()
        self.assertIsNone(sale.client_id)
        self.assertEqual(sale.quick_client_name, "Cliente Rápido")
        self.assertEqual(sale.quick_client_phone, "5551112222")

    def test_cobrar_sale_falla_ticket_vacio(self):
        self._login(self.user_vendedor)
        self._set_ticket(items={}, cliente={"id": self.client_reg.id}, cantidad_pagada="0")
        res = self.client.post(reverse("sales:cobrar"), data={
            "descuento_pct": "0", "metodo_pago": "CASH", "cantidad_pagada": "0"
        })
        self.assertEqual(res.status_code, 302)
        self.assertEqual(Sale.objects.count(), 0)

    def test_cobrar_sale_falla_sin_cliente(self):
        self._login(self.user_vendedor)
        self._set_ticket(items={str(self.p1.id): 1}, cliente=None, cantidad_pagada="500")
        res = self.client.post(reverse("sales:cobrar"), data={
            "descuento_pct": "0", "metodo_pago": "CASH", "cantidad_pagada": "500"
        })
        self.assertEqual(res.status_code, 302)
        self.assertEqual(Sale.objects.count(), 0)

    def test_cobrar_sale_falla_faltante(self):
        self._login(self.user_vendedor)
        self._set_ticket(items={str(self.p1.id): 1}, cliente={"id": self.client_reg.id}, cantidad_pagada="10")
        res = self.client.post(reverse("sales:cobrar"), data={
            "descuento_pct": "0", "metodo_pago": "CASH", "cantidad_pagada": "10"
        })
        self.assertEqual(res.status_code, 302)
        self.assertEqual(Sale.objects.count(), 0)

    def test_cobrar_falla_por_stock_insuficiente(self):
        self._login(self.user_vendedor)
        self.p2.stock = 1
        self.p2.save()

        self._set_ticket(
            items={str(self.p2.id): 2},
            cliente={"id": self.client_reg.id},
            descuento_pct="0",
            metodo_pago="CASH",
            cantidad_pagada="9999",
        )
        res = self.client.post(reverse("sales:cobrar"), data={
            "descuento_pct": "0", "metodo_pago": "CASH", "cantidad_pagada": "9999"
        })
        self.assertEqual(res.status_code, 302)
        self.assertEqual(Sale.objects.count(), 0)

    def test_sale_success_back_url(self):
        self._login(self.user_vendedor)
        sale = Sale.objects.create(
            user=self.user_vendedor,
            status=Sale.Status.PAID,
            subtotal=Decimal("500.00"),
            discount_amount=Decimal("0.00"),
            total=Decimal("500.00"),
            payment_method=Sale.PaymentMethod.CASH,
            amount_paid=Decimal("500.00"),
            change_amount=Decimal("0.00"),
            client=self.client_reg,
            folio="V000123",
        )
        SaleItem.objects.create(
            sale=sale,
            product=self.p1,
            product_name=self.p1.name,
            unit_price=Decimal("500.00"),
            qty=1,
            line_total=Decimal("500.00"),
        )

        res = self.client.get(reverse("sales:detail", args=[sale.id]) + "?from=list")
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "V000123")

        res2 = self.client.get(reverse("sales:success", args=[sale.id]))
        self.assertEqual(res2.status_code, 200)

    def test_sales_list_periodos(self):
        self._login(self.user_vendedor)

        now = timezone.localtime(timezone.now())
        hoy = now

        v_hoy = Sale.objects.create(user=self.user_vendedor, status=Sale.Status.PAID, folio="VHOY", total=Decimal("1.00"))
        v_hoy.created_at = hoy
        v_hoy.save(update_fields=["created_at"])

        v_ayer = Sale.objects.create(user=self.user_vendedor, status=Sale.Status.PAID, folio="VAYER", total=Decimal("1.00"))
        v_ayer.created_at = hoy - timedelta(days=1)
        v_ayer.save(update_fields=["created_at"])

        r0 = self.client.get(reverse("sales:ventas_list"), data={"periodo": "cualquiera"})
        self.assertEqual(r0.status_code, 200)

        r1 = self.client.get(reverse("sales:ventas_list"))
        self.assertContains(r1, "VHOY")
        self.assertNotContains(r1, "VAYER")

        r2 = self.client.get(reverse("sales:ventas_list"), data={"periodo": "ayer"})
        self.assertContains(r2, "VAYER")

        r3 = self.client.get(reverse("sales:ventas_list"), data={"periodo": "semana"})
        self.assertContains(r3, "VAYER")
        self.assertContains(r3, "VHOY")

        r4 = self.client.get(reverse("sales:ventas_list"), data={"periodo": "mes"})
        self.assertContains(r4, "VAYER")
        self.assertContains(r4, "VHOY")

    def test_sales_list_filtra_por_vendedor(self):
        self._login(self.user_vendedor)

        Sale.objects.create(user=self.user_vendedor, status=Sale.Status.PAID, folio="V000001", total=Decimal("10.00"))
        Sale.objects.create(user=self.user_admin, status=Sale.Status.PAID, folio="V000002", total=Decimal("10.00"))

        res = self.client.get(reverse("sales:ventas_list"), data={"vendedor": "vend1", "periodo": "hoy"})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "V000001")
        self.assertNotContains(res, "V000002")


class SalesCancelTest(TestCase):
    def setUp(self):
        self.grp_admin = Group.objects.create(name="AdminPOS")
        self.grp_vendedor = Group.objects.create(name="VendedorPOS")

        self.admin = User.objects.create_user(username="admin1", password="12345678")
        self.admin.groups.add(self.grp_admin)

        self.vend = User.objects.create_user(username="vend1", password="12345678")
        self.vend.groups.add(self.grp_vendedor)

        self.cat = Category.objects.create(name="Anillos")
        self.mat = Material.objects.create(name="Plata", purity="925")
        self.sup = Supplier.objects.create(name="Prov", code="P1", phone="555", email="p@test.com")

        self.p1 = Product.objects.create(
            name="Anillo Plata",
            code="ANP01",
            category=self.cat,
            purchase_price=10,
            sale_price=Decimal("100.00"),
            weight=1,
            stock=5,
            supplier=self.sup,
            material=self.mat,
        )

        self.client_reg = Client.objects.create(
            name="Juan",
            apellido_paterno="Pérez",
            apellido_materno="Gómez",
            phone="5559998888",
            email="juan@test.com",
            rfc="ABC123",
            is_active=True,
        )

        self.sale = Sale.objects.create(
            user=self.vend,
            status=Sale.Status.PAID,
            subtotal=Decimal("200.00"),
            discount_amount=Decimal("0.00"),
            total=Decimal("200.00"),
            payment_method=Sale.PaymentMethod.CASH,
            amount_paid=Decimal("200.00"),
            change_amount=Decimal("0.00"),
            client=self.client_reg,
            folio="V000123",
        )
        SaleItem.objects.create(
            sale=self.sale,
            product=self.p1,
            product_name=self.p1.name,
            unit_price=Decimal("100.00"),
            qty=2,
            line_total=Decimal("200.00"),
        )

    def test_cancel_sale_admin_cancela_y_regresa_stock(self):
        self.client.force_login(self.admin)

        stock_before = Product.objects.get(id=self.p1.id).stock

        res = self.client.post(reverse("sales:cancel", args=[self.sale.id]))
        self.assertEqual(res.status_code, 302)

        self.sale.refresh_from_db()
        self.assertEqual(self.sale.status, Sale.Status.CANCELLED)

        p = Product.objects.get(id=self.p1.id)
        self.assertEqual(p.stock, stock_before + 2)

    def test_cancel_sale_vendedor_no_puede(self):
        self.client.force_login(self.vend)

        stock_before = Product.objects.get(id=self.p1.id).stock

        res = self.client.post(reverse("sales:cancel", args=[self.sale.id]))
        self.assertIn(res.status_code, (302, 403))

        self.sale.refresh_from_db()
        self.assertEqual(self.sale.status, Sale.Status.PAID)

        p = Product.objects.get(id=self.p1.id)
        self.assertEqual(p.stock, stock_before)