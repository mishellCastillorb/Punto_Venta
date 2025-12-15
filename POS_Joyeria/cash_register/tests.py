from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
import uuid
from cash_register.models import CashRegister
from sales.models import Sale

User = get_user_model()


class CashRegisterModelTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username="admin", password="12345")

    def test_str_abierta(self):
        cash = CashRegister.objects.create(opened_by=self.admin, opening_amount="100.00")
        self.assertIn("Caja #", str(cash))
        self.assertIn("ABIERTA", str(cash))

    def test_str_cerrada(self):
        cash = CashRegister.objects.create(opened_by=self.admin, opening_amount="100.00", is_closed=True)
        self.assertIn("CERRADA", str(cash))


class CashRegisterViewsTest(TestCase):
    def setUp(self):
        self.g_admin = Group.objects.create(name="AdminPOS")
        self.g_vendedor = Group.objects.create(name="VendedorPOS")

        self.admin = User.objects.create_user(username="admin", password="12345")
        self.vendedor1 = User.objects.create_user(username="vend1", password="12345")
        self.vendedor2 = User.objects.create_user(username="vend2", password="12345")

        self.admin.groups.add(self.g_admin)
        self.vendedor1.groups.add(self.g_vendedor)
        self.vendedor2.groups.add(self.g_vendedor)

        self.url_status = reverse("cash_register_web:status")
        self.url_open = reverse("cash_register_web:open")
        self.url_close = reverse("cash_register_web:close")

    def _open_cash(self, opened_by, opening_amount="100.00"):
        return CashRegister.objects.create(opened_by=opened_by, opening_amount=opening_amount)

    def _sale(self, user, total, method="CASH", status=None, created_at=None):
        if status is None:
            status = Sale.Status.PAID
        sale = Sale.objects.create(
            user=user,
            total=Decimal(str(total)),
            payment_method=method,
            status=status,
            folio=f"TST-{uuid.uuid4().hex[:10].upper()}",
        )
        if created_at is not None:
            Sale.objects.filter(pk=sale.pk).update(created_at=created_at)
            sale.refresh_from_db()
        return sale

    def test_open_cash_get_renderiza_form(self):
        self.client.force_login(self.admin)
        res = self.client.get(self.url_open)
        self.assertEqual(res.status_code, 200)
        # plantilla esperada
        self.assertTemplateUsed(res, "cash_register/open.html")

    def test_open_cash_post_crea_caja_y_redirige_status(self):
        self.client.force_login(self.admin)
        res = self.client.post(self.url_open, {"opening_amount": "250.00"})
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, self.url_status)

        cash = CashRegister.objects.filter(is_closed=False).first()
        self.assertIsNotNone(cash)
        self.assertEqual(cash.opened_by, self.admin)
        self.assertEqual(cash.opening_amount, Decimal("250.00"))

    def test_open_cash_si_ya_hay_caja_abierta_no_crea_otra(self):
        self._open_cash(self.admin, "100.00")

        self.client.force_login(self.admin)
        res = self.client.post(self.url_open, {"opening_amount": "999.00"})
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, self.url_status)

        self.assertEqual(CashRegister.objects.filter(is_closed=False).count(), 1)

    def test_status_sin_caja_redirige_a_open(self):
        self.client.force_login(self.admin)
        res = self.client.get(self.url_status)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, self.url_open)

    def test_status_admin_ve_todas_las_ventas_y_vendedor_solo_las_suyas(self):
        cash = self._open_cash(self.admin, "100.00")
        t0 = cash.opened_at


        self._sale(self.vendedor1, "50.00", method="CASH", created_at=t0)
        self._sale(self.vendedor2, "70.00", method="CARD", created_at=t0)

        self.client.force_login(self.admin)
        res_admin = self.client.get(self.url_status)
        self.assertEqual(res_admin.status_code, 200)
        resumen_admin = res_admin.context["resumen"]
        self.assertEqual(resumen_admin["cantidad"], 2)
        self.assertEqual(resumen_admin["total"], Decimal("120.00"))

        self.client.force_login(self.vendedor1)
        res_v1 = self.client.get(self.url_status)
        self.assertEqual(res_v1.status_code, 200)
        resumen_v1 = res_v1.context["resumen"]
        self.assertEqual(resumen_v1["cantidad"], 1)
        self.assertEqual(resumen_v1["total"], Decimal("50.00"))

    def test_close_cash_sin_caja_redirige_a_open(self):
        self.client.force_login(self.admin)
        res = self.client.get(self.url_close)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, self.url_open)

    def test_close_cash_get_muestra_totales_calculados(self):
        cash = self._open_cash(self.admin, "100.00")
        t0 = cash.opened_at

        self._sale(self.admin, "10.00", method="CASH", created_at=t0)
        self._sale(self.admin, "20.00", method="CARD", created_at=t0)
        self._sale(self.admin, "30.00", method="TRANSFER", created_at=t0)

        self.client.force_login(self.admin)
        res = self.client.get(self.url_close)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "cash_register/close.html")

        self.assertEqual(res.context["cash_total"], Decimal("10.00"))
        self.assertEqual(res.context["card_total"], Decimal("20.00"))
        self.assertEqual(res.context["transfer_total"], Decimal("30.00"))
        self.assertEqual(res.context["total_sales"], Decimal("60.00"))

    def test_close_cash_post_rechaza_monto_negativo_y_no_cierra(self):
        cash = self._open_cash(self.admin, "100.00")
        self.client.force_login(self.admin)

        res = self.client.post(self.url_close, {"closing_amount": "-1"})
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, self.url_close)

        cash.refresh_from_db()
        self.assertFalse(cash.is_closed)
        self.assertIsNone(cash.closed_at)
        self.assertIsNone(cash.closing_amount)

    def test_close_cash_post_cierra_y_guarda_totales_y_diferencia(self):
        cash = self._open_cash(self.admin, "100.00")
        t0 = cash.opened_at

        self._sale(self.admin, "60.00", method="CASH", created_at=t0)
        self._sale(self.admin, "40.00", method="CARD", created_at=t0)

        self.client.force_login(self.admin)
        res = self.client.post(self.url_close, {"closing_amount": "55.00"})
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, self.url_status, fetch_redirect_response=False)

        cash.refresh_from_db()
        self.assertTrue(cash.is_closed)
        self.assertEqual(cash.cash_total, Decimal("60.00"))
        self.assertEqual(cash.card_total, Decimal("40.00"))
        self.assertEqual(cash.transfer_total, Decimal("0.00"))
        self.assertEqual(cash.total_sales, Decimal("100.00"))

        self.assertEqual(cash.closing_amount, Decimal("55.00"))
        self.assertEqual(cash.difference, Decimal("-5.00"))
        self.assertEqual(cash.closed_by, self.admin)
        self.assertIsNotNone(cash.closed_at)
