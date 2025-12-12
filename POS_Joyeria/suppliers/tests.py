from django.test import TestCase
from django.db.utils import IntegrityError
from django.urls import reverse

from rest_framework.test import APITestCase

from .models import Supplier


# -------------------- MODEL TESTS --------------------

class SupplierModelTest(TestCase):

    def test_crear_proveedor(self):
        supplier = Supplier.objects.create(
            name="Proveedor 1",
            code="V01",
            phone="5551112222",
            email="proveedor1@test.com",
            notes="Proveedor principal de anillos."
        )

        self.assertEqual(Supplier.objects.count(), 1)
        self.assertEqual(supplier.code, "V01")
        self.assertEqual(str(supplier), "Proveedor 1")

    def test_codigo_unico_db(self):
        Supplier.objects.create(
            name="Proveedor 1",
            code="V01",
            phone="5551112222",
            email="proveedor1@test.com",
        )

        with self.assertRaises(IntegrityError):
            Supplier.objects.create(
                name="Proveedor 2",
                code="V01",  # mismo código
                phone="5553334444",
                email="proveedor2@test.com",
            )

    def test_telefono_unico_db(self):
        Supplier.objects.create(
            name="Proveedor 1",
            code="V01",
            phone="5551112222",
            email="proveedor1@test.com",
        )

        with self.assertRaises(IntegrityError):
            Supplier.objects.create(
                name="Proveedor 2",
                code="V02",
                phone="5551112222",  # mismo teléfono
                email="proveedor2@test.com",
            )

    def test_correo_unico_db(self):
        Supplier.objects.create(
            name="Proveedor 1",
            code="V01",
            phone="5551112222",
            email="proveedor1@test.com",
        )

        with self.assertRaises(IntegrityError):
            Supplier.objects.create(
                name="Proveedor 2",
                code="V02",
                phone="5553334444",
                email="proveedor1@test.com",  # mismo correo
            )

class SupplierAPITestCase(APITestCase):

    def setUp(self):
        self.url_list = reverse("supplier-list-create")

    def test_crear_proveedor_valido(self):
        data = {
            "name": "Proveedor Uno",
            "code": "P01",
            "phone": "5550001111",
            "email": "prov1@test.com",
            "notes": "Mayorista de plata",
        }

        response = self.client.post(self.url_list, data, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Supplier.objects.count(), 1)

    def test_rechaza_sin_code_phone_email(self):
        data = {
            "name": "Proveedor Incompleto",
            "code": "",
            "phone": "",
            "email": "",
        }

        response = self.client.post(self.url_list, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("code", response.data)
        self.assertIn("phone", response.data)
        self.assertIn("email", response.data)

    def test_nombre_demasiado_corto(self):
        data = {
            "name": "Ab",
            "code": "P10",
            "phone": "5551234567",
            "email": "p10@test.com",
        }
        response = self.client.post(self.url_list, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.data)

    def test_rechaza_code_duplicado(self):
        Supplier.objects.create(
            name="Proveedor Base",
            code="P01",
            phone="5550001111",
            email="prov1@test.com",
        )

        data = {
            "name": "Proveedor Duplicado",
            "code": "P01",
            "phone": "5550002222",
            "email": "otro@test.com",
        }

        response = self.client.post(self.url_list, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("code", response.data)

    def test_rechaza_phone_duplicado(self):
        Supplier.objects.create(
            name="Proveedor Base",
            code="P01",
            phone="5550001111",
            email="prov1@test.com",
        )

        data = {
            "name": "Proveedor Duplicado",
            "code": "P02",
            "phone": "5550001111",  # mismo teléfono
            "email": "otro@test.com",
        }

        response = self.client.post(self.url_list, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("phone", response.data)

    def test_rechaza_email_duplicado(self):
        Supplier.objects.create(
            name="Proveedor Base",
            code="P01",
            phone="5550001111",
            email="prov1@test.com",
        )

        data = {
            "name": "Proveedor Duplicado",
            "code": "P02",
            "phone": "5550002222",
            "email": "prov1@test.com",  # mismo correo
        }

        response = self.client.post(self.url_list, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_email_formato_invalido(self):
        data = {
            "name": "Proveedor Mail Malo",
            "code": "P13",
            "phone": "5551234567",
            "email": "no-es-correo",
        }
        response = self.client.post(self.url_list, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_actualizar_mantiene_unicos_correctamente(self):
        prov = Supplier.objects.create(
            name="Proveedor Base",
            code="P20",
            phone="5550001111",
            email="p20@test.com",
        )

        url_detail = reverse("supplier-detail", args=[prov.id])
        data = {
            "name": "Proveedor Base Editado",
            "code": "P20",
            "phone": "5550001111",
            "email": "p20@test.com",
            "notes": "Editado",
        }
        response = self.client.put(url_detail, data, format="json")
        self.assertEqual(response.status_code, 200)
        prov.refresh_from_db()
        self.assertEqual(prov.name, "Proveedor Base Editado")


class SupplierWebViewsTestCase(TestCase):
    def setUp(self):
        self.s1 = Supplier.objects.create(
            name="Joyas Eva",
            code="JE",
            phone="5567253827",
            email="joyaseva@gmail.com",
            notes="Notas"
        )

    def test_list_muestra_template_y_contexto(self):
        url = reverse("suppliers_web:list")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "suppliers/proveedores.html")

        self.assertIn("proveedores", res.context)
        self.assertTrue(any(p.id == self.s1.id for p in res.context["proveedores"]))

        self.assertContains(res, "Proveedores")
        self.assertContains(res, "Joyas Eva")

    def test_list_sin_registros_muestra_mensaje(self):
        Supplier.objects.all().delete()

        url = reverse("suppliers_web:list")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "suppliers/proveedores.html")
        self.assertContains(res, "No hay proveedores", status_code=200)

    #  CREATE
    def test_create_get_renderiza_formulario(self):
        url = reverse("suppliers_web:create")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "suppliers/formulario.html")
        self.assertIn("form", res.context)
        self.assertEqual(res.context.get("modo"), "crear")

    def test_create_post_valido_crea_y_redirige(self):
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

    def test_create_post_phone_no_numerico_muestra_error(self):
        url = reverse("suppliers_web:create")
        payload = {
            "name": "Proveedor Tel Malo",
            "code": "PT1",
            "phone": "55-50A01111",  # inválido
            "email": "pt1@gmail.com",
            "notes": "",
        }
        res = self.client.post(url, data=payload)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "suppliers/formulario.html")
        self.assertTrue(res.context["form"].errors)
        self.assertIn("phone", res.context["form"].errors)

    def test_create_post_phone_corto_muestra_error(self):
        url = reverse("suppliers_web:create")
        payload = {
            "name": "Proveedor Tel Corto",
            "code": "PT2",
            "phone": "123456",  # 6 dígitos
            "email": "pt2@gmail.com",
            "notes": "",
        }
        res = self.client.post(url, data=payload)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "suppliers/formulario.html")
        self.assertTrue(res.context["form"].errors)
        self.assertIn("phone", res.context["form"].errors)

    def test_create_post_duplicados_muestra_errores(self):
        url = reverse("suppliers_web:create")
        payload = {
            "name": "Otro",
            "code": self.s1.code,
            "phone": self.s1.phone,
            "email": self.s1.email,
            "notes": "",
        }

        res = self.client.post(url, data=payload)

        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "suppliers/formulario.html")
        self.assertTrue(res.context["form"].errors)

    # EDIT
    def test_edit_get_renderiza_form_con_datos(self):
        url = reverse("suppliers_web:edit", args=[self.s1.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "suppliers/formulario.html")
        self.assertIn("form", res.context)

        form = res.context["form"]
        self.assertEqual(form.instance.id, self.s1.id)

    def test_edit_post_valido_actualiza_y_redirige(self):
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

    def test_edit_post_invalido_se_queda_en_form(self):
        url = reverse("suppliers_web:edit", args=[self.s1.id])
        payload = {
            "name": "",
            "code": "JE",
            "phone": "5567253827",
            "email": "joyaseva@gmail.com",
            "notes": "",
        }

        res = self.client.post(url, data=payload)

        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "suppliers/formulario.html")
        self.assertTrue(res.context["form"].errors)

    #  DELETE
    def test_delete_post_elimina_y_redirige(self):
        url = reverse("suppliers_web:delete", args=[self.s1.id])
        res = self.client.post(url, follow=False)

        self.assertEqual(res.status_code, 302)
        self.assertEqual(res["Location"], reverse("suppliers_web:list"))
        self.assertFalse(Supplier.objects.filter(id=self.s1.id).exists())
