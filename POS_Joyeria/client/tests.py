from django.test import TestCase
from django.urls import reverse, resolve
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls.exceptions import Resolver404

from rest_framework.test import APITestCase
from rest_framework import status

from .models import Client
from .forms import ClientForm
from .serializers import ClientSerializer


# MODEL TESTS

class ClientModelTest(TestCase):
    def test_crear_cliente_ok(self):
        c = Client.objects.create(
            name="Juan",
            apellido_paterno="Pérez",
            apellido_materno="Gómez",
            phone="5551112222",
            email="juan@test.com",
            rfc="ABC9203041H2",
            es_mayorista=True,
            is_active=True,
        )
        self.assertEqual(Client.objects.count(), 1)
        self.assertEqual(c.name, "Juan")
        self.assertTrue(c.es_mayorista)

    def test_telefono_unico_db(self):
        Client.objects.create(name="C1", phone="5551112222")
        with self.assertRaises(IntegrityError):
            Client.objects.create(name="C2", phone="5551112222")

    def test_email_unico_db(self):
        Client.objects.create(name="C1", email="c1@test.com")
        with self.assertRaises(IntegrityError):
            Client.objects.create(name="C2", email="c1@test.com")

    def test_rfc_unico_db(self):
        Client.objects.create(name="C1", rfc="ABC9203041H2")
        with self.assertRaises(IntegrityError):
            Client.objects.create(name="C2", rfc="ABC9203041H2")

    def test_str_muestra_nombre_completo(self):
        c = Client.objects.create(name="Juan", apellido_paterno="Pérez", apellido_materno="Gómez")
        self.assertEqual(str(c), "Juan Pérez Gómez")


# FORM TESTS

class ClientFormTest(TestCase):
    def test_name_obligatorio_y_minimo(self):
        form = ClientForm(data={"name": "  "})
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("El nombre es obligatorio.", form.errors["name"][0])

        form = ClientForm(data={"name": "Jo"})
        self.assertFalse(form.is_valid())
        self.assertIn("El nombre debe tener al menos 3 caracteres.", form.errors["name"][0])

    def test_apellidos_opcionales_pero_minimo_3_si_vienen(self):
        form = ClientForm(data={"name": "Juan", "apellido_paterno": "Pe"})
        self.assertFalse(form.is_valid())
        self.assertIn("apellido_paterno", form.errors)

        form = ClientForm(data={"name": "Juan", "apellido_materno": "Go"})
        self.assertFalse(form.is_valid())
        self.assertIn("apellido_materno", form.errors)

    def test_phone_validaciones_y_unicidad_excluyendo_self(self):

        form = ClientForm(data={"name": "Juan", "phone": "55ABC"})
        self.assertFalse(form.is_valid())
        self.assertIn("El teléfono solo debe contener dígitos.", form.errors["phone"][0])

        form = ClientForm(data={"name": "Juan", "phone": "123456"})
        self.assertFalse(form.is_valid())
        self.assertIn("El teléfono debe tener al menos 7 dígitos.", form.errors["phone"][0])

        form = ClientForm(data={"name": "Juan", "phone": "1" * 16})
        self.assertFalse(form.is_valid())
        msg = str(form.errors["phone"][0]).lower()
        self.assertTrue(
            ("15" in msg) and (
                    ("como máximo" in msg) or ("at most" in msg) or ("max" in msg) or ("no debe exceder" in msg)
            ),
            msg
        )

        Client.objects.create(name="Ana", phone="5551112222")
        form = ClientForm(data={"name": "Beto", "phone": "5551112222"})
        self.assertFalse(form.is_valid())
        self.assertIn("Ya existe un cliente con ese teléfono.", form.errors["phone"][0])

        c = Client.objects.create(name="Carlos", phone="5553334444")
        form = ClientForm(data={"name": "Carlos Edit", "phone": "5553334444"}, instance=c)
        self.assertTrue(form.is_valid(), form.errors)

    def test_rfc_regex_y_unicidad_case_insensitive(self):

        form = ClientForm(data={"name": "Juan", "rfc": "ABC123"})
        self.assertFalse(form.is_valid())
        self.assertIn("El RFC debe tener 12 a 13 caracteres", form.errors["rfc"][0])

        form = ClientForm(data={"name": "Juan", "rfc": "ABC9203041H2"})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["rfc"], "ABC9203041H2")

        form = ClientForm(data={"name": "Juan", "rfc": "ABC9203041H2Z"})
        self.assertTrue(form.is_valid(), form.errors)

        Client.objects.create(name="Ximena", rfc="ABC9203041H2")
        form = ClientForm(data={"name": "Yahir", "rfc": "abc9203041h2"})
        self.assertFalse(form.is_valid())
        self.assertIn("Ya existe un cliente registrado con este RFC.", form.errors["rfc"][0])

        c = Client.objects.create(name="Zeta", rfc="ABC9203041H2Z")
        form = ClientForm(data={"name": "Zeta 2", "rfc": "abc9203041h2z"}, instance=c)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["rfc"], "ABC9203041H2Z")  # upper

    def test_email_formato_y_unicidad_case_insensitive(self):

        form = ClientForm(data={"name": "Juan", "email": "no-es-correo"})
        self.assertFalse(form.is_valid())
        self.assertIn("Ingresa un correo electrónico válido.", form.errors["email"][0])

        Client.objects.create(name="Ana", email="correo@test.com")
        form = ClientForm(data={"name": "Beto", "email": "CORREO@test.com"})
        self.assertFalse(form.is_valid())
        self.assertIn("Ya existe un cliente con ese correo.", form.errors["email"][0])

        c = Client.objects.create(name="Carlos", email="mismo@test.com")
        form = ClientForm(data={"name": "Carlos 2", "email": "MISMO@test.com"}, instance=c)
        self.assertTrue(form.is_valid(), form.errors)


# SERIALIZER TESTS

class ClientSerializerTest(TestCase):
    def test_name_trim_obligatorio_minimo(self):
        s = ClientSerializer(data={"name": "   "})
        self.assertFalse(s.is_valid())
        self.assertIn("name", s.errors)

        s = ClientSerializer(data={"name": "Jo"})
        self.assertFalse(s.is_valid())
        self.assertIn("El nombre debe tener al menos 3 caracteres.", s.errors["name"][0])

        s = ClientSerializer(data={"name": "   Juan   "})
        self.assertTrue(s.is_valid(), s.errors)
        self.assertEqual(s.validated_data["name"], "Juan")

    def test_apellidos_minimo_3_si_vienen(self):
        s = ClientSerializer(data={"name": "Juan", "apellido_paterno": "Pe"})
        self.assertFalse(s.is_valid())
        self.assertIn("apellido_paterno", s.errors)

        s = ClientSerializer(data={"name": "Juan", "apellido_materno": "Go"})
        self.assertFalse(s.is_valid())
        self.assertIn("apellido_materno", s.errors)

    def test_phone_digits_y_minimo(self):
        s = ClientSerializer(data={"name": "Juan", "phone": "55ABC"})
        self.assertFalse(s.is_valid())
        self.assertIn("phone", s.errors)

        s = ClientSerializer(data={"name": "Juan", "phone": "123456"})
        self.assertFalse(s.is_valid())
        self.assertIn("El teléfono debe tener al menos 7 dígitos.", s.errors["phone"][0])

        s = ClientSerializer(data={"name": "Juan", "phone": "5551112222"})
        self.assertTrue(s.is_valid(), s.errors)

    def test_email_unico_case_insensitive(self):
        Client.objects.create(name="Ana", email="correo@test.com")
        s = ClientSerializer(data={"name": "Beto", "email": "CORREO@test.com"})
        self.assertFalse(s.is_valid())
        self.assertIn("email", s.errors)

    def test_rfc_regex_y_unico_case_insensitive(self):
        s = ClientSerializer(data={"name": "Ana", "rfc": "ABC123"})
        self.assertFalse(s.is_valid())
        self.assertIn("rfc", s.errors)

        Client.objects.create(name="Carlos", rfc="ABC9203041H2")
        s = ClientSerializer(data={"name": "Beto", "rfc": "abc9203041h2"})
        self.assertFalse(s.is_valid())
        msg = str(s.errors["rfc"][0]).lower()
        self.assertTrue(
            ("ya existe" in msg) or ("12 a 13" in msg) or ("inválido" in msg),
            msg
        )

        s = ClientSerializer(data={"name": "Carlos", "rfc": "ABC9203041H2Z"})
        self.assertTrue(s.is_valid(), s.errors)


# API TESTS

class ClientApiViewsTest(APITestCase):
    def setUp(self):
        self.activo = Client.objects.create(
            name="Activo",
            email="a@test.com",
            phone="5551111111",
            is_active=True
        )
        self.inactivo = Client.objects.create(
            name="Inactivo",
            email="i@test.com",
            phone="5552222222",
            is_active=False
        )

        self.list_url = "/api/clients/list/"
        self.create_url = "/api/clients/create/"

    def test_list_view_solo_activos(self):
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["name"], "Activo")

    def test_create_view_crea_cliente(self):
        data = {"name": "Nuevo", "phone": "5553334444", "email": "nuevo@test.com"}
        resp = self.client.post(self.create_url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Client.objects.filter(email="nuevo@test.com").exists())

    def test_detail_retrieve_y_update(self):
        url = f"/api/clients/{self.activo.pk}/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["name"], "Activo")

        resp2 = self.client.patch(url, {"name": "Activo Edit"}, format="json")
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.activo.refresh_from_db()
        self.assertEqual(self.activo.name, "Activo Edit")

    @staticmethod
    def _first_existing_path(paths):
        for p in paths:
            try:
                resolve(p)
                return p
            except Resolver404:
                continue
        return None

    def test_deactivate_view_soft_delete(self):
        candidates = [
            f"/api/clients/{self.activo.pk}/deactivate/",
            f"/api/clients/{self.activo.pk}/deactivate",
            f"/api/clients/deactivate/{self.activo.pk}/",
            f"/api/clients/deactivate/{self.activo.pk}",
            f"/api/clients/{self.activo.pk}/delete/",
            f"/api/clients/{self.activo.pk}/delete",
        ]
        url = self._first_existing_path(candidates)

        self.assertIsNotNone(
            url,
            f"No encontré endpoint de deactivate. Probé: {candidates}. "
            f"Pon aquí la ruta real que tengas en client/urls.py"
        )

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.activo.refresh_from_db()
        self.assertFalse(self.activo.is_active)


class ClientWebViewsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.g_admin, _ = Group.objects.get_or_create(name="AdminPOS")
        cls.g_vendedor, _ = Group.objects.get_or_create(name="VendedorPOS")

        User = get_user_model()

        cls.admin = User.objects.create_user(username="adminpos", password="pass12345")
        cls.admin.groups.add(cls.g_admin)

        cls.vendedor = User.objects.create_user(username="vendedorpos", password="pass12345")
        cls.vendedor.groups.add(cls.g_vendedor)

        cls.superuser = User.objects.create_superuser(
            username="root", password="pass12345", email="root@test.com"
        )

        cls.activo = Client.objects.create(
            name="Juan",
            apellido_paterno="Pérez",
            apellido_materno="Gómez",
            phone="5551112222",
            email="juan@test.com",
            rfc="ABC9203041H2",
            es_mayorista=True,
            is_active=True,
        )
        cls.inactivo = Client.objects.create(
            name="Ana",
            phone="5559998888",
            email="ana@test.com",
            is_active=False,
        )

    def test_list_renderiza_y_context_is_adminpos_para_admin(self):
        self.client.login(username="adminpos", password="pass12345")

        url = reverse("clients_web:list")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "client/clientes.html")
        self.assertIn("activos", res.context)
        self.assertIn("inactivos", res.context)
        self.assertTrue(res.context["is_adminpos"])

    def test_list_context_is_adminpos_false_para_vendedor(self):
        self.client.login(username="vendedorpos", password="pass12345")

        url = reverse("clients_web:list")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.context["is_adminpos"])

    def test_list_context_is_adminpos_true_para_superuser(self):
        self.client.login(username="root", password="pass12345")

        url = reverse("clients_web:list")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.context["is_adminpos"])

    def test_create_get_muestra_form(self):
        self.client.login(username="adminpos", password="pass12345")

        url = reverse("clients_web:create")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "client/formulario.html")
        self.assertIn("form", res.context)

    def test_create_post_valido_crea_y_redirige(self):
        self.client.login(username="adminpos", password="pass12345")

        url = reverse("clients_web:create")
        payload = {
            "name": "Nuevo",
            "apellido_paterno": "López",
            "apellido_materno": "Ruiz",
            "phone": "5553334444",
            "email": "nuevo@test.com",
            "rfc": "ABC9203041H2Z",
            "es_mayorista": "on",
        }
        res = self.client.post(url, data=payload, follow=False)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res["Location"], reverse("clients_web:list"))
        self.assertTrue(Client.objects.filter(email="nuevo@test.com", is_active=True).exists())

    def test_edit_get_y_post_actualiza(self):
        self.client.login(username="adminpos", password="pass12345")

        url = reverse("clients_web:edit", args=[self.activo.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context["form"].instance.id, self.activo.id)

        payload = {
            "name": "Juan Editado",
            "apellido_paterno": "Pérez",
            "apellido_materno": "Gómez",
            "phone": "5551112222",
            "email": "juan@test.com",
            "rfc": "ABC9203041H2",
            "es_mayorista": "on",
        }
        res2 = self.client.post(url, data=payload, follow=False)
        self.assertEqual(res2.status_code, 302)
        self.activo.refresh_from_db()
        self.assertEqual(self.activo.name, "Juan Editado")

    def test_delete_post_soft_delete(self):
        self.client.login(username="adminpos", password="pass12345")

        url = reverse("clients_web:delete", args=[self.activo.id])
        res = self.client.post(url, follow=False)
        self.assertEqual(res.status_code, 302)

        self.activo.refresh_from_db()
        self.assertFalse(self.activo.is_active)

    def test_activate_post_reactiva(self):
        self.client.login(username="adminpos", password="pass12345")

        url = reverse("clients_web:activate", args=[self.inactivo.id])
        res = self.client.post(url, follow=False)
        self.assertEqual(res.status_code, 302)

        self.inactivo.refresh_from_db()
        self.assertTrue(self.inactivo.is_active)
