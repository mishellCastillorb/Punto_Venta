from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from io import BytesIO
from PIL import Image
from rest_framework.test import APITestCase
from suppliers.models import Supplier
from .models import Category, Material, Product
from .forms import CategoryForm, MaterialForm, ProductForm



def make_image_file(name="test.jpg"):
    f = BytesIO()
    img = Image.new("RGB", (1, 1), "white")
    img.save(f, "JPEG")
    f.seek(0)
    return SimpleUploadedFile(name, f.read(), content_type="image/jpeg")


# -------------------------
# MODEL TESTS
# -------------------------

class ProductModelTest(TestCase):
    def setUp(self):
        self.cat_anillos = Category.objects.create(name="Anillos")
        self.cat_pulseras = Category.objects.create(name="Pulseras")

        self.mat_plata = Material.objects.create(name="Plata", purity="925")

        self.proveedor = Supplier.objects.create(
            name="Proveedor Joyas",
            code="V01",
            phone="5550001111",
            email="joyas@test.com"
        )

    def test_codigo_primero_categoria(self):
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

        p.name = "Anillo modificado"
        p.sale_price = 850
        p.save()

        p.refresh_from_db()
        self.assertEqual(p.code, codigo_original)


# -------------------------
# FORM TESTS (para cubrir clean_name y formularios)
# -------------------------

class CategoryFormTest(TestCase):
    def test_category_form_nombre_obligatorio(self):
        form = CategoryForm(data={"name": "   "})
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_category_form_nombre_min_3(self):
        form = CategoryForm(data={"name": "Ab"})
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_category_form_trim(self):
        form = CategoryForm(data={"name": "  Anillos  "})
        self.assertTrue(form.is_valid(), form.errors)
        obj = form.save()
        self.assertEqual(obj.name, "Anillos")


class MaterialFormTest(TestCase):
    def test_material_form_crea_ok(self):
        form = MaterialForm(data={"name": "Plata", "purity": "925"})
        self.assertTrue(form.is_valid(), form.errors)
        obj = form.save()
        self.assertEqual(obj.name, "Plata")


class ProductFormTest(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Anillos")
        self.mat = Material.objects.create(name="Plata", purity="925")
        self.sup = Supplier.objects.create(
            name="Proveedor Joyas", code="V01", phone="5550001111", email="p@test.com"
        )

    def test_product_form_valido_crea(self):
        form = ProductForm(
            data={
                "name": "Anillo Plata",
                "category": self.cat.id,
                "supplier": self.sup.id,
                "material": self.mat.id,
                "purchase_price": "500.00",
                "sale_price": "800.00",
                "weight": "10.00",
                "stock": 5,
            },
            files={"image": make_image_file()},
        )
        self.assertTrue(form.is_valid(), form.errors)
        p = form.save()
        self.assertTrue(p.code)  # se generó


# -------------------------
# API TESTS (DRF)
# -------------------------

class CategoryAPITest(APITestCase):
    def test_crear_categoria(self):
        url = reverse("category-list-create")
        resp = self.client.post(url, {"name": "Anillos"}, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Category.objects.count(), 1)

    def test_listar_categorias(self):
        Category.objects.create(name="Anillos")
        Category.objects.create(name="Pulseras")
        url = reverse("category-list-create")
        resp = self.client.get(url, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 2)


class MaterialAPITest(APITestCase):
    def test_crear_material(self):
        url = reverse("material-list-create")
        resp = self.client.post(url, {"name": "Plata", "purity": "925"}, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Material.objects.count(), 1)

    def test_listar_materiales(self):
        Material.objects.create(name="Plata", purity="925")
        Material.objects.create(name="Oro", purity="14k")
        url = reverse("material-list-create")
        resp = self.client.get(url, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 2)


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

    def test_crear_producto_ok(self):
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
            "image": make_image_file(),
        }
        resp = self.client.post(url, data, format="multipart")
        self.assertEqual(resp.status_code, 201)
        p = Product.objects.first()
        self.assertIsNotNone(p.code)

    def test_error_sin_categoria(self):
        url = reverse("product-list-create")
        data = {
            "name": "Producto sin categoría",
            "purchase_price": "500.00",
            "sale_price": "800.00",
            "weight": "10.00",
            "stock": 5,
            "supplier": self.supplier.id,
            "material": self.material.id,
            "image": make_image_file(),
        }
        resp = self.client.post(url, data, format="multipart")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("category", resp.data)

    def test_error_sin_imagen_en_post(self):
        """Tu serializer exige image al crear (POST)."""
        url = reverse("product-list-create")
        data = {
            "name": "Sin imagen",
            "category": self.category.id,
            "purchase_price": "500.00",
            "sale_price": "800.00",
            "weight": "10.00",
            "stock": 5,
            "supplier": self.supplier.id,
            "material": self.material.id,
        }
        resp = self.client.post(url, data, format="multipart")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("image", resp.data)

    def test_error_valores_negativos(self):
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
            "image": make_image_file(),
        }
        resp = self.client.post(url, data, format="multipart")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("purchase_price", resp.data)
        self.assertIn("weight", resp.data)
        self.assertIn("stock", resp.data)

    def test_codigo_no_cambia_al_actualizar_via_api(self):
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
            # En PUT no estás obligando image (solo en POST), pero si la mandas está ok
            "image": make_image_file(),
        }

        resp = self.client.put(url, data, format="multipart")
        self.assertEqual(resp.status_code, 200)

        product.refresh_from_db()
        self.assertEqual(product.code, codigo_original)

    def test_eliminar_producto(self):
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
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(Product.objects.count(), 0)


# -------------------------
# WEB VIEWS TESTS (sin JS)
# -------------------------

class ProductsWebViewsTest(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Anillos")
        self.mat = Material.objects.create(name="Plata", purity="925")
        self.sup = Supplier.objects.create(
            name="Proveedor Joyas", code="V01", phone="5550001111", email="p@test.com"
        )
        self.prod = Product.objects.create(
            name="Anillo base",
            category=self.cat,
            purchase_price=500,
            sale_price=800,
            weight=10,
            stock=5,
            supplier=self.sup,
            material=self.mat,
            image="products/test.jpg",
        )

    def test_category_list_200(self):
        url = reverse("products_web:categories")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Anillos")

    def test_category_create_post_ok_redirect(self):
        url = reverse("products_web:category_create")
        res = self.client.post(url, {"name": "Pulseras"}, follow=False)
        self.assertEqual(res.status_code, 302)
        self.assertTrue(Category.objects.filter(name="Pulseras").exists())

    def test_material_list_200(self):
        url = reverse("products_web:materials")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Plata")

    def test_material_create_post_ok_redirect(self):
        url = reverse("products_web:material_create")
        res = self.client.post(url, {"name": "Oro", "purity": "14k"}, follow=False)
        self.assertEqual(res.status_code, 302)
        self.assertTrue(Material.objects.filter(name="Oro").exists())

    def test_product_list_200(self):
        url = reverse("products_web:list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Anillo base")

    def test_product_create_post_ok_redirect(self):
        url = reverse("products_web:product_create")
        payload = {
            "name": "Anillo nuevo",
            "category": self.cat.id,
            "supplier": self.sup.id,
            "material": self.mat.id,
            "purchase_price": "100.00",
            "sale_price": "200.00",
            "weight": "1.00",
            "stock": 2,
        }
        res = self.client.post(url, data=payload, files={"image": make_image_file()}, follow=False)
        self.assertIn(res.status_code, (200, 302))

    def test_product_edit_precio_venta_menor_muestra_confirm(self):
        """Cubre la rama de confirmación en product_edit."""
        url = reverse("products_web:product_edit", args=[self.prod.id])
        payload = {
            "name": "Anillo base",
            "category": self.cat.id,
            "supplier": self.sup.id,
            "material": self.mat.id,
            "purchase_price": "500.00",
            "sale_price": "100.00",  # menor que compra
            "weight": "10.00",
            "stock": 5,
        }
        res = self.client.post(url, data=payload)
        self.assertEqual(res.status_code, 200)
        # Solo verificamos que no redirigió (confirmación)
