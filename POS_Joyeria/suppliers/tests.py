from django.test import TestCase
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Supplier
from .forms import SupplierForm
from .serializers import SupplierSerializer
from decimal import Decimal
from django.contrib.messages import get_messages

User = get_user_model()
# MODEL TESTS

class SupplierModelTest(TestCase):
    def test_crear_proveedor_ok_y_str(self):
        s = Supplier.objects.create(
            name="Proveedor 1",
            code="V01",
            phone="5551112222",
            email="proveedor1@test.com",
            notes="Proveedor principal",
        )
        self.assertEqual(Supplier.objects.count(), 1)
        self.assertEqual(str(s), "Proveedor 1")

    def test_unique_code_db(self):
        Supplier.objects.create(
            name="Proveedor 1",
            code="V01",
            phone="5551112222",
            email="p1@test.com",
        )
        with self.assertRaises(IntegrityError):
            Supplier.objects.create(
                name="Proveedor 2",
                code="V01",
                phone="5553334444",
                email="p2@test.com",
            )

    def test_unique_phone_db(self):
        Supplier.objects.create(
            name="Proveedor 1",
            code="V01",
            phone="5551112222",
            email="p1@test.com",
        )
        with self.assertRaises(IntegrityError):
            Supplier.objects.create(
                name="Proveedor 2",
                code="V02",
                phone="5551112222",
                email="p2@test.com",
            )

    def test_unique_email_db(self):
        Supplier.objects.create(
            name="Proveedor 1",
            code="V01",
            phone="5551112222",
            email="p1@test.com",
        )
        with self.assertRaises(IntegrityError):
            Supplier.objects.create(
                name="Proveedor 2",
                code="V02",
                phone="5553334444",
                email="p1@test.com",
            )

    def test_phone_validator_solo_digitos(self):
        s = Supplier(
            name="Proveedor 1",
            code="V01",
            phone="55-50A01111",  # invalido por regex validator
            email="p1@test.com",
        )
        with self.assertRaises(ValidationError):
            s.full_clean()


# FORM TESTS

class SupplierFormTest(TestCase):
    def test_form_crea_ok(self):
        form = SupplierForm(data={
            "name": "Joyas Eva",
            "code": "JE01",
            "phone": "5567253827",
            "email": "joyaseva@gmail.com",
            "notes": "Notas",
        })
        self.assertTrue(form.is_valid(), form.errors)
        obj = form.save()
        self.assertEqual(obj.code, "JE01")

    def test_form_requiere_campos_obligatorios(self):
        # Por modelo: name/code/phone/email son obligatorios
        form = SupplierForm(data={
            "name": "",
            "code": "",
            "phone": "",
            "email": "",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("code", form.errors)
        self.assertIn("phone", form.errors)
        self.assertIn("email", form.errors)

    def test_form_phone_invalido_por_regex(self):
        form = SupplierForm(data={
            "name": "Proveedor Tel Malo",
            "code": "PT1",
            "phone": "55-50A01111",
            "email": "pt1@gmail.com",
            "notes": "",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)

    def test_form_duplicados_unicos(self):
        Supplier.objects.create(
            name="Base",
            code="B01",
            phone="5550001111",
            email="base@test.com",
        )
        form = SupplierForm(data={
            "name": "Otro",
            "code": "B01",
            "phone": "5550001111",
            "email": "base@test.com",
            "notes": "",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("code", form.errors)
        self.assertIn("phone", form.errors)
        self.assertIn("email", form.errors)


# SERIALIZER TESTS

class SupplierSerializerTest(TestCase):
    def test_requeridos_y_mensajes(self):
        s = SupplierSerializer(data={
            "name": "",
            "code": "",
            "phone": "",
            "email": "",
        })
        self.assertFalse(s.is_valid())
        self.assertIn("name", s.errors)
        self.assertIn("code", s.errors)
        self.assertIn("phone", s.errors)
        self.assertIn("email", s.errors)

    def test_name_minimo_3(self):
        s = SupplierSerializer(data={
            "name": "Ab",
            "code": "P10",
            "phone": "5551234567",
            "email": "p10@test.com",
        })
        self.assertFalse(s.is_valid())
        self.assertIn("name", s.errors)
        self.assertIn("al menos 3", str(s.errors["name"][0]).lower())

    def test_unicidad_controlada_code_phone_email(self):
        Supplier.objects.create(
            name="Base",
            code="P01",
            phone="5550001111",
            email="prov1@test.com",
        )

        s = SupplierSerializer(data={
            "name": "Otro Proveedor",
            "code": "p01",               # case-insensitive
            "phone": "5550001111",       # exact
            "email": "PROV1@test.com",   # case-insensitive
        })
        self.assertFalse(s.is_valid())
        self.assertIn("code", s.errors)
        self.assertIn("phone", s.errors)
        self.assertIn("email", s.errors)

    def test_update_excluye_self_en_unicidad(self):
        prov = Supplier.objects.create(
            name="Proveedor Base",
            code="P20",
            phone="5550001111",
            email="p20@test.com",
        )
        s = SupplierSerializer(instance=prov, data={
            "name": "Proveedor Base Editado",
            "code": "p20",              # mismo pero distinto case
            "phone": "5550001111",
            "email": "P20@test.com",    # mismo pero distinto case
            "notes": "Editado",
        })
        self.assertTrue(s.is_valid(), s.errors)


# API TESTS (DRF)

class SupplierAPITestCase(APITestCase):
    def setUp(self):
        self.url_list = reverse("supplier-list-create")

    def test_crear_proveedor_valido(self):
        data = {
            "name": "Proveedor Uno",
            "code": "P01",
            "phone": "5550001111",
            "email": "prov1@test.com",
            "notes": "Mayorista",
        }
        response = self.client.post(self.url_list, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Supplier.objects.count(), 1)

    def test_rechaza_sin_campos_obligatorios(self):
        data = {"name": "", "code": "", "phone": "", "email": ""}
        response = self.client.post(self.url_list, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("code", response.data)
        self.assertIn("phone", response.data)
        self.assertIn("email", response.data)
        self.assertIn("name", response.data)

    def test_email_formato_invalido(self):
        data = {
            "name": "Proveedor Mail Malo",
            "code": "P13",
            "phone": "5551234567",
            "email": "no-es-correo",
        }
        response = self.client.post(self.url_list, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_rechaza_duplicados(self):
        Supplier.objects.create(
            name="Proveedor Base",
            code="P01",
            phone="5550001111",
            email="prov1@test.com",
        )
        data = {
            "name": "Proveedor Duplicado",
            "code": "p01",
            "phone": "5550001111",
            "email": "PROV1@test.com",
        }
        response = self.client.post(self.url_list, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("code", response.data)
        self.assertIn("phone", response.data)
        self.assertIn("email", response.data)

    def test_detail_get_put_delete(self):
        prov = Supplier.objects.create(
            name="Proveedor Base",
            code="P20",
            phone="5550001111",
            email="p20@test.com",
        )

        url_detail = reverse("supplier-detail", args=[prov.id])

        # GET
        r1 = self.client.get(url_detail, format="json")
        self.assertEqual(r1.status_code, status.HTTP_200_OK)
        self.assertEqual(r1.data["code"], "P20")

        # PUT
        data = {
            "name": "Proveedor Base Editado",
            "code": "P20",
            "phone": "5550001111",
            "email": "p20@test.com",
            "notes": "Editado",
        }
        r2 = self.client.put(url_detail, data, format="json")
        self.assertEqual(r2.status_code, status.HTTP_200_OK)
        prov.refresh_from_db()
        self.assertEqual(prov.name, "Proveedor Base Editado")

        # DELETE
        r3 = self.client.delete(url_detail)
        self.assertEqual(r3.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Supplier.objects.filter(id=prov.id).exists())


# WEB VIEWS TESTS (role_required AdminPOS)

class SupplierWebViewsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.g_admin, _ = Group.objects.get_or_create(name="AdminPOS")
        User = get_user_model()
        cls.admin = User.objects.create_user(username="adminpos", password="pass12345")
        cls.admin.groups.add(cls.g_admin)

        cls.s1 = Supplier.objects.create(
            name="Joyas Eva",
            code="JE",
            phone="5567253827",
            email="joyaseva@gmail.com",
            notes="Notas",
        )

    def login_admin(self):
        ok = self.client.login(username="adminpos", password="pass12345")
        self.assertTrue(ok)

    def test_list_renderiza_template_y_contexto(self):
        self.login_admin()

        url = reverse("suppliers_web:list")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "suppliers/proveedores.html")
        self.assertIn("proveedores", res.context)
        self.assertTrue(any(p.id == self.s1.id for p in res.context["proveedores"]))
        self.assertContains(res, "Joyas Eva")

    def test_create_get_renderiza_formulario(self):
        self.login_admin()

        url = reverse("suppliers_web:create")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "suppliers/formulario.html")
        self.assertIn("form", res.context)
        self.assertEqual(res.context.get("modo"), "crear")

    def test_create_post_valido_crea_y_redirige(self):
        self.login_admin()

        url = reverse("suppliers_web:create")
        payload = {
            "name": "Proveedor Nuevo",
            "code": "PN1",
            "phone": "9515786598",
            "email": "proveedor1@gmail.com",
            "notes": "Hola",
        }
        res = self.client.post(url, data=payload, follow=False)

        self.assertEqual(res.status_code, 302)
        self.assertEqual(res["Location"], reverse("suppliers_web:list"))
        self.assertTrue(Supplier.objects.filter(code="PN1").exists())

    def test_edit_get_renderiza_form_con_datos(self):
        self.login_admin()

        url = reverse("suppliers_web:edit", args=[self.s1.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "suppliers/formulario.html")
        self.assertIn("form", res.context)
        self.assertEqual(res.context["form"].instance.id, self.s1.id)

    def test_edit_post_valido_actualiza_y_redirige(self):
        self.login_admin()

        url = reverse("suppliers_web:edit", args=[self.s1.id])
        payload = {
            "name": "Joyas Eva Editado",
            "code": "JE",
            "phone": "5567253827",
            "email": "joyaseva@gmail.com",
            "notes": "Actualizado",
        }
        res = self.client.post(url, data=payload, follow=False)

        self.assertEqual(res.status_code, 302)
        self.assertEqual(res["Location"], reverse("suppliers_web:list"))

        self.s1.refresh_from_db()
        self.assertEqual(self.s1.name, "Joyas Eva Editado")
        self.assertEqual(self.s1.notes, "Actualizado")

    def test_delete_post_elimina_y_redirige(self):
        self.login_admin()

        url = reverse("suppliers_web:delete", args=[self.s1.id])
        res = self.client.post(url, follow=False)

        self.assertEqual(res.status_code, 302)
        self.assertEqual(res["Location"], reverse("suppliers_web:list"))
        self.assertFalse(Supplier.objects.filter(id=self.s1.id).exists())

    class SupplierWebViewsTestCase(TestCase):

        @classmethod
        def setUpTestData(cls):
            cls.g_admin, _ = Group.objects.get_or_create(name="AdminPOS")

            cls.admin = User.objects.create_user(
                username="admin",
                password="12345678",
                is_staff=True
            )
            cls.admin.groups.add(cls.g_admin)

            cls.supplier = Supplier.objects.create(
                name="Proveedor Test",
                code="P001",
                phone="5551112222",
                email="prove@test.com"
            )

            cls.url_list = reverse("suppliers_web:list")
            cls.url_delete = reverse("suppliers_web:delete", args=[cls.supplier.id])

        def setUp(self):
            self.client.force_login(self.admin)
