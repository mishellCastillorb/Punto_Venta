from io import BytesIO
from PIL import Image
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase
from rest_framework import status
from suppliers.models import Supplier
from .models import Category, Material, Product
from .forms import CategoryForm, MaterialForm, ProductForm
from .serializers import ProductSerializer


# Helpers

def make_image_file(name="test.jpg"):
    f = BytesIO()
    img = Image.new("RGB", (1, 1), "white")
    img.save(f, "JPEG")
    f.seek(0)
    return SimpleUploadedFile(name, f.read(), content_type="image/jpeg")


# MODEL TESTS

class ProductModelTest(TestCase):
    def setUp(self):
        self.cat_anillos = Category.objects.create(name="Anillos")
        self.cat_pulseras = Category.objects.create(name="Pulseras")
        self.mat_plata = Material.objects.create(name="Plata", purity="925")
        self.proveedor = Supplier.objects.create(
            name="Proveedor Joyas",
            code="V01",
            phone="5550001111",
            email="joyas@test.com",
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


# FORM TESTS

class CategoryFormTest(TestCase):
    def test_nombre_obligatorio_y_minimo(self):
        form = CategoryForm(data={"name": "   "})
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

        form = CategoryForm(data={"name": "Ab"})
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_trim_y_crea(self):
        form = CategoryForm(data={"name": "  Anillos  "})
        self.assertTrue(form.is_valid(), form.errors)
        obj = form.save()
        self.assertEqual(obj.name, "Anillos")

    def test_unicidad_case_insensitive(self):
        Category.objects.create(name="Anillos")
        form = CategoryForm(data={"name": "anillos"})
        self.assertFalse(form.is_valid())
        self.assertIn("Ya existe una categoría con ese nombre.", form.errors["name"][0])

    def test_update_excluye_self(self):
        c = Category.objects.create(name="Anillos")
        form = CategoryForm(data={"name": "ANILLOS"}, instance=c)
        self.assertTrue(form.is_valid(), form.errors)


class MaterialFormTest(TestCase):

    def test_crea_ok(self):
        form = MaterialForm(data={"name": "Plata", "purity": "925"})
        self.assertTrue(form.is_valid(), form.errors)
        obj = form.save()
        self.assertEqual(obj.name, "Plata")

    def test_update_excluye_self(self):
        m = Material.objects.create(name="Oro", purity="14k")
        form = MaterialForm(data={"name": "ORO", "purity": "14k"}, instance=m)
        self.assertTrue(form.is_valid(), form.errors)


class ProductFormTest(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Anillos")
        self.mat = Material.objects.create(name="Plata", purity="925")
        self.sup = Supplier.objects.create(
            name="Proveedor Joyas", code="V01", phone="5550001111", email="p@test.com"
        )

    def test_valido_crea(self):
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


# SERIALIZER TESTS

class ProductSerializerTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Anillos")
        self.material = Material.objects.create(name="Plata", purity="925")
        self.supplier = Supplier.objects.create(
            name="Proveedor Joyas",
            code="V01",
            phone="5550001111",
            email="proveedor@test.com",
        )

    def test_post_requiere_imagen(self):
        data = {
            "name": "Anillo",
            "category": self.category.id,
            "supplier": self.supplier.id,
            "material": self.material.id,
            "purchase_price": "500.00",
            "sale_price": "800.00",
            "weight": "10.00",
            "stock": 5,
        }
        s = ProductSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn("image", s.errors)

    def test_post_valores_negativos(self):
        data = {
            "name": "Anillo",
            "category": self.category.id,
            "supplier": self.supplier.id,
            "material": self.material.id,
            "purchase_price": "-1.00",
            "sale_price": "-1.00",
            "weight": "-1.00",
            "stock": -1,
            "image": make_image_file(),
        }
        s = ProductSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn("purchase_price", s.errors)
        self.assertIn("sale_price", s.errors)
        self.assertIn("weight", s.errors)
        self.assertIn("stock", s.errors)

    def test_update_no_exige_imagen(self):
        p = Product.objects.create(
            name="Anillo base",
            category=self.category,
            supplier=self.supplier,
            material=self.material,
            purchase_price=500,
            sale_price=800,
            weight=10,
            stock=5,
            image="products/test.jpg",
        )
        s = ProductSerializer(instance=p, data={"sale_price": "900.00"}, partial=True)
        self.assertTrue(s.is_valid(), s.errors)


# API TESTS

class CategoryAPITest(APITestCase):
    def test_crear_categoria(self):
        url = reverse("category-list-create")
        resp = self.client.post(url, {"name": "Anillos"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 1)

    def test_listar_categorias(self):
        Category.objects.create(name="Anillos")
        Category.objects.create(name="Pulseras")
        url = reverse("category-list-create")
        resp = self.client.get(url, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)


class MaterialAPITest(APITestCase):
    def test_crear_material(self):
        url = reverse("material-list-create")
        resp = self.client.post(url, {"name": "Plata", "purity": "925"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Material.objects.count(), 1)

    def test_listar_materiales(self):
        Material.objects.create(name="Plata", purity="925")
        Material.objects.create(name="Oro", purity="14k")
        url = reverse("material-list-create")
        resp = self.client.get(url, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
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
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
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
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("category", resp.data)

    def test_error_sin_imagen_en_post(self):
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
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("image", resp.data)

    def test_error_valores_negativos(self):
        url = reverse("product-list-create")
        data = {
            "name": "Anillo raro",
            "category": self.category.id,
            "purchase_price": "-10.00",
            "sale_price": "-1.00",
            "weight": "-5.00",
            "stock": -1,
            "supplier": self.supplier.id,
            "material": self.material.id,
            "image": make_image_file(),
        }
        resp = self.client.post(url, data, format="multipart")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("purchase_price", resp.data)
        self.assertIn("sale_price", resp.data)
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
            "image": make_image_file(),
        }
        resp = self.client.put(url, data, format="multipart")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

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
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)


# WEB VIEWS TESTS

class ProductsWebViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.g_admin, _ = Group.objects.get_or_create(name="AdminPOS")
        cls.g_vendedor, _ = Group.objects.get_or_create(name="VendedorPOS")

        User = get_user_model()
        cls.admin = User.objects.create_user(username="adminpos", password="pass12345")
        cls.admin.groups.add(cls.g_admin)

        cls.vendedor = User.objects.create_user(username="vendedorpos", password="pass12345")
        cls.vendedor.groups.add(cls.g_vendedor)

        cls.cat = Category.objects.create(name="Anillos")
        cls.mat = Material.objects.create(name="Plata", purity="925")
        cls.sup = Supplier.objects.create(
            name="Proveedor Joyas", code="V01", phone="5550001111", email="p@test.com"
        )
        cls.prod = Product.objects.create(
            name="Anillo base",
            category=cls.cat,
            purchase_price=500,
            sale_price=800,
            weight=10,
            stock=5,
            supplier=cls.sup,
            material=cls.mat,
            image="products/test.jpg",
        )

    def test_category_list_200_para_vendedor(self):
        self.client.login(username="vendedorpos", password="pass12345")
        url = reverse("products_web:categories")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Anillos")

    def test_category_create_post_ok_redirect_admin(self):
        self.client.login(username="adminpos", password="pass12345")
        url = reverse("products_web:category_create")
        res = self.client.post(url, {"name": "Pulseras"}, follow=False)
        self.assertEqual(res.status_code, 302)
        self.assertTrue(Category.objects.filter(name="Pulseras").exists())

    def test_category_delete_post_admin(self):
        self.client.login(username="adminpos", password="pass12345")
        c = Category.objects.create(name="Cadenas")
        url = reverse("products_web:category_delete", args=[c.id])
        res = self.client.post(url, follow=False)
        self.assertEqual(res.status_code, 302)
        self.assertFalse(Category.objects.filter(id=c.id).exists())

    def test_material_list_200_para_vendedor(self):
        self.client.login(username="vendedorpos", password="pass12345")
        url = reverse("products_web:materials")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Plata")

    def test_material_create_post_ok_redirect_admin(self):
        self.client.login(username="adminpos", password="pass12345")
        url = reverse("products_web:material_create")
        res = self.client.post(url, {"name": "Oro", "purity": "14k"}, follow=False)
        self.assertEqual(res.status_code, 302)
        self.assertTrue(Material.objects.filter(name="Oro").exists())

    def test_material_delete_post_admin(self):
        self.client.login(username="adminpos", password="pass12345")
        m = Material.objects.create(name="Titanio", purity="999")
        url = reverse("products_web:material_delete", args=[m.id])
        res = self.client.post(url, follow=False)
        self.assertEqual(res.status_code, 302)
        self.assertFalse(Material.objects.filter(id=m.id).exists())

    def test_product_list_200_para_vendedor(self):
        self.client.login(username="vendedorpos", password="pass12345")
        url = reverse("products_web:list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Anillo base")

    def test_product_create_post_ok_redirect_admin(self):
        self.client.login(username="adminpos", password="pass12345")
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
            "image": make_image_file(),
        }
        res = self.client.post(url, data=payload, follow=False)
        self.assertEqual(res.status_code, 302)
        self.assertTrue(Product.objects.filter(name="Anillo nuevo").exists())

    def test_product_edit_precio_venta_menor_muestra_confirm(self):
        self.client.login(username="adminpos", password="pass12345")
        url = reverse("products_web:product_edit", args=[self.prod.id])
        payload = {
            "name": "Anillo base",
            "category": self.cat.id,
            "supplier": self.sup.id,
            "material": self.mat.id,
            "purchase_price": "500.00",
            "sale_price": "100.00",
            "weight": "10.00",
            "stock": 5,
            "image": make_image_file(),
        }
        res = self.client.post(url, data=payload)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "products/confirm_precio.html")

    def test_product_edit_confirmar_si_venta_menor_guarda(self):
        self.client.login(username="adminpos", password="pass12345")
        url = reverse("products_web:product_edit", args=[self.prod.id])
        payload = {
            "name": "Anillo base",
            "category": self.cat.id,
            "supplier": self.sup.id,
            "material": self.mat.id,
            "purchase_price": "500.00",
            "sale_price": "100.00",
            "weight": "10.00",
            "stock": 5,
            "confirmar": "1",
            "image": make_image_file(),
        }
        res = self.client.post(url, data=payload, follow=False)
        self.assertEqual(res.status_code, 302)


def test_category_no_permite_nombre_duplicado_case_insensitive(self):
    Category.objects.create(name="Anillo")
    form = CategoryForm(data={"name": "  anillo  "})
    self.assertFalse(form.is_valid())
    self.assertIn("Ya existe una categoría con ese nombre.", form.errors["name"][0])

def test_material_permite_mismo_nombre_con_distinta_pureza(self):
    Material.objects.create(name="Oro", purity="10K")
    form = MaterialForm(data={"name": "Oro", "purity": "14K"})
    self.assertTrue(form.is_valid(), form.errors)

def test_material_no_permite_duplicado_name_purity_case_insensitive(self):
    Material.objects.create(name="Oro", purity="14K")
    form = MaterialForm(data={"name": "  oro  ", "purity": "  14k  "})
    self.assertFalse(form.is_valid())
    self.assertTrue("purity" in form.errors or "name" in form.errors)

def test_supplier_delete_protected_muestra_mensaje(self):
    self.client.force_login(self.admin)  # el que tenga rol
    sup = Supplier.objects.create(name="Prov", code="P1", phone="555", email="p@test.com")
    Product.objects.create(
        name="X",
        code="X01",
        category=self.category,
        purchase_price=10,
        sale_price=Decimal("100.00"),
        weight=1,
        stock=1,
        supplier=sup,
        material=self.material,
    )
    res = self.client.post(reverse("suppliers_web:delete", args=[sup.id]))
    self.assertEqual(res.status_code, 302)

    msgs = [m.message for m in get_messages(res.wsgi_request)]
    self.assertTrue(any("No se puede eliminar" in m for m in msgs), msgs)