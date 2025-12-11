from django.test import TestCase
from django.contrib.auth.models import User

from client.models import Client
from products.models import Category, Material, Product
from suppliers.models import Supplier

from .models import Sale, SaleItem


class SaleModelTest(TestCase):

    def setUp(self):
        # Datos base para productos
        self.category = Category.objects.create(name="Anillos")
        self.material = Material.objects.create(name="Plata", purity="925")

        self.supplier = Supplier.objects.create(
            name="Proveedor Joyas",
            code="V01",
            phone="5550001111",
            email="proveedor@test.com"
        )
        self.producto1 = Product.objects.create(
            name="Anillo Plata",
            category=self.category,
            purchase_price=200,
            sale_price=500,
            weight=10,
            stock=20,
            supplier=self.supplier,
            material=self.material
        )
        self.producto2 = Product.objects.create(
            name="Anillo Oro",
            category=self.category,
            purchase_price=400,
            sale_price=900,
            weight=12,
            stock=10,
            supplier=self.supplier,
            material=self.material
        )
        # Usuario vendedor
        self.vendedor = User.objects.create(username="vendedor1")
        # Cliente registrado
        self.cliente = Client.objects.create(
            name="Juan",
            apellido_paterno="Pérez",
            apellido_materno="Gómez",
            phone="5559998888",
            email="juan@test.com",
            rfc="ABC123"
        )

    def test_crear_venta_con_cliente(self):
        venta = Sale.objects.create(
            client=self.cliente,
            seller=self.vendedor,
            payment_method="EFECTIVO",
            amount_paid=500,
            change=0
        )
        self.assertEqual(Sale.objects.count(), 1)
        self.assertEqual(venta.client.name, "Juan")

    def test_crear_venta_rapida(self):
        venta = Sale.objects.create(
            client_name="Cliente Rápido",
            client_phone="5551112222",
            seller=self.vendedor,
            payment_method="EFECTIVO",
            amount_paid=500,
        )
        self.assertIsNone(venta.client)
        self.assertEqual(venta.client_name, "Cliente Rápido")

    def test_calculo_total_venta(self):
        venta = Sale.objects.create(
            seller=self.vendedor,
            payment_method="EFECTIVO",
            amount_paid=2000,
        )
        SaleItem.objects.create(
            sale=venta,
            product=self.producto1,
            quantity=2,
            price=500  # subtotal = 1000
        )
        SaleItem.objects.create(
            sale=venta,
            product=self.producto2,
            quantity=1,
            price=900  # subtotal = 900
        )
        self.assertEqual(venta.total, 1900)

    def test_subtotal_item(self):
        venta = Sale.objects.create(
            seller=self.vendedor,
            payment_method="EFECTIVO",
            amount_paid=1000,
        )
        item = SaleItem.objects.create(
            sale=venta,
            product=self.producto1,
            quantity=3,
            price=500
        )
        self.assertEqual(item.subtotal, 1500)

    def test_eliminar_venta_elimina_items(self):
        # SI se borra la venta los procutos se regresan al stock
        venta = Sale.objects.create(
            seller=self.vendedor,
            payment_method="EFECTIVO",
        )
        SaleItem.objects.create(
            sale=venta,
            product=self.producto1,
            quantity=1,
            price=500
        )
        self.assertEqual(SaleItem.objects.count(), 1)
        venta.delete()
        self.assertEqual(SaleItem.objects.count(), 0)

        # Metodo para mostara el correcto fromato de la venta
    def test_str_venta(self):
        venta = Sale.objects.create(
            seller=self.vendedor,
            payment_method="EFECTIVO",
        )

        texto = str(venta)

        self.assertIn("Venta #", texto)
