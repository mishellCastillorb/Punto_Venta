from django.test import TestCase
from suppliers.models import Supplier
from .models import Category, Material, Product


class ProductModelTest(TestCase):

    def setUp(self):
        self.cat_anillos = Category.objects.create(name="Anillos")
        self.cat_pulseras = Category.objects.create(name="Pulseras")

        self.mat_plata = Material.objects.create(
            name="Plata",
            purity="925"
        )

        self.proveedor = Supplier.objects.create(
            name="Proveedor Joyas",
            code="V01",
            phone="5550001111",
            email="joyas@test.com"
        )

    def test_codigo_primero_categoria(self):
        """El primer producto de una categoría genera código terminado en 001."""
        p = Product.objects.create(
            name="Anillo simple",
            category=self.cat_anillos,
            purchase_price=500,
            sale_price=800,
            weight=10,
            stock=5,
            supplier=self.proveedor,
            material=self.mat_plata,
        )
        self.assertEqual(p.code, "V01ANI001")

    def test_codigo_incrementa_en_categoria(self):
        """El segundo producto de la misma categoría incrementa el consecutivo."""
        Product.objects.create(
            name="Anillo 1",
            category=self.cat_anillos,
            purchase_price=500,
            sale_price=800,
            weight=10,
            stock=5,
            supplier=self.proveedor,
            material=self.mat_plata,
        )

        p2 = Product.objects.create(
            name="Anillo 2",
            category=self.cat_anillos,
            purchase_price=600,
            sale_price=900,
            weight=12,
            stock=3,
            supplier=self.proveedor,
            material=self.mat_plata,
        )

        self.assertEqual(p2.code, "V01ANI002")

    def test_codigo_independiente_por_categoria(self):
        """Categorías distintas inician desde 001 cada una."""
        # Creamos un anillo
        Product.objects.create(
            name="Anillo 1",
            category=self.cat_anillos,
            purchase_price=500,
            sale_price=800,
            weight=10,
            stock=5,
            supplier=self.proveedor,
            material=self.mat_plata,
        )

        # Primer producto en pulseras
        pulsera = Product.objects.create(
            name="Pulsera 1",
            category=self.cat_pulseras,
            purchase_price=300,
            sale_price=600,
            weight=8,
            stock=10,
            supplier=self.proveedor,
            material=self.mat_plata,
        )

        self.assertEqual(pulsera.code, "V01PUL001")

    def test_codigo_no_cambia_al_editar(self):
        """El código no debe cambiar si editamos el producto."""
        p = Product.objects.create(
            name="Anillo original",
            category=self.cat_anillos,
            purchase_price=500,
            sale_price=800,
            weight=10,
            stock=5,
            supplier=self.proveedor,
            material=self.mat_plata,
        )

        codigo_original = p.code

        # Editamos cosas que NO deben afectar el código
        p.name = "Anillo modificado"
        p.sale_price = 850
        p.save()

        p.refresh_from_db()
        self.assertEqual(p.code, codigo_original)
