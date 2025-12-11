from django.test import TestCase
from suppliers.models import Supplier
from .models import Category, Material, Product
from rest_framework.test import APITestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image



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



# INIICIO DE LAS PRUBAS DE NIVERL SERIALIZERS


class CategoryAPITest(APITestCase):

    def test_crear_categoria(self):
        """Se puede crear una categoría vía API."""
        url = reverse("category-list-create")
        data = {"name": "Anillos"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(Category.objects.first().name, "Anillos")

    def test_listar_categorias(self):
        """Se pueden listar categorías vía API."""
        Category.objects.create(name="Anillos")
        Category.objects.create(name="Pulseras")

        url = reverse("category-list-create")
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)


class MaterialAPITest(APITestCase):

    def test_crear_material(self):
        """Se puede crear un material vía API."""
        url = reverse("material-list-create")
        data = {
            "name": "Plata",
            "purity": "925"
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Material.objects.count(), 1)
        self.assertEqual(Material.objects.first().name, "Plata")

    def test_listar_materiales(self):
        """Se pueden listar materiales vía API."""
        Material.objects.create(name="Plata", purity="925")
        Material.objects.create(name="Oro", purity="14k")

        url = reverse("material-list-create")
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

class ProductAPITest(APITestCase):

    def setUp(self):
        self.category = Category.objects.create(name="Anillos")
        self.material = Material.objects.create(name="Plata", purity="925")
        self.supplier = Supplier.objects.create(
            name="Proveedor Joyas",
            code="V01",
            phone="5550001111",
            email="proveedor@test.com"
        )

    def _crear_imagen_dummy(self):
        # Crea una imagen RGB de 1x1 píxel en memoria
        file_obj = BytesIO()
        image = Image.new("RGB", (1, 1), "white")
        image.save(file_obj, "JPEG")
        file_obj.seek(0)

        return SimpleUploadedFile(
            "test.jpg",
            file_obj.read(),
            content_type="image/jpeg"
        )

    def test_crear_producto_ok(self):
        """Se puede crear un producto válido vía API."""
        url = reverse("product-list-create")

        data = {
            "name": "Anillo Plata",
            "category": self.category.id,
            "purchase_price": "500.00",
            "sale_price": "800.00",
            "weight": "10.00",
            "stock": 5,
            "supplier": self.supplier.id,
            "material": self.material.id,
            "is_active": True,
            "image": self._crear_imagen_dummy(),
        }

        response = self.client.post(url, data, format="multipart")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 1)
        product = Product.objects.first()
        self.assertEqual(product.name, "Anillo Plata")
        self.assertIsNotNone(product.code)

    def test_error_sin_categoria(self):
        """No permite crear producto sin categoría."""
        url = reverse("product-list-create")

        data = {
            "name": "Producto sin categoría",
            "purchase_price": "500.00",
            "sale_price": "800.00",
            "weight": "10.00",
            "stock": 5,
            "supplier": self.supplier.id,
            "material": self.material.id,
            "image": self._crear_imagen_dummy(),
        }

        response = self.client.post(url, data, format="multipart")

        self.assertEqual(response.status_code, 400)
        self.assertIn("category", response.data)

    def test_error_valores_negativos(self):
        """No permite valores negativos en precios, stock o peso."""
        url = reverse("product-list-create")

        data = {
            "name": "Anillo raro",
            "category": self.category.id,
            "purchase_price": "-10.00",
            "sale_price": "800.00",
            "weight": "-5.00",
            "stock": -1,
            "supplier": self.supplier.id,
            "material": self.material.id,
            "image": self._crear_imagen_dummy(),
        }

        response = self.client.post(url, data, format="multipart")

        self.assertEqual(response.status_code, 400)
        self.assertIn("purchase_price", response.data)
        self.assertIn("weight", response.data)
        self.assertIn("stock", response.data)

    def test_codigo_no_cambia_al_actualizar_via_api(self):
        """El código no cambia cuando se actualiza el producto vía API."""
        # Creamos primero el producto (modelo)
        product = Product.objects.create(
            name="Anillo original",
            category=self.category,
            purchase_price=500,
            sale_price=800,
            weight=10,
            stock=5,
            supplier=self.supplier,
            material=self.material,
            image="products/test.jpg",
        )

        codigo_original = product.code

        url = reverse("product-detail", args=[product.id])

        data = {
            "name": "Anillo actualizado",
            "category": self.category.id,
            "purchase_price": "600.00",
            "sale_price": "900.00",
            "weight": "12.00",
            "stock": 10,
            "supplier": self.supplier.id,
            "material": self.material.id,
            "is_active": True,
            "image": self._crear_imagen_dummy(),  # reenviamos imagen
        }

        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, 200)

        product.refresh_from_db()
        self.assertEqual(product.code, codigo_original)
        self.assertEqual(product.name, "Anillo actualizado")

    def test_eliminar_producto(self):
        """Se puede eliminar un producto vía API."""
        product = Product.objects.create(
            name="Anillo a borrar",
            category=self.category,
            purchase_price=500,
            sale_price=800,
            weight=10,
            stock=5,
            supplier=self.supplier,
            material=self.material,
            image="products/test.jpg",
        )

        url = reverse("product-detail", args=[product.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Product.objects.count(), 0)
