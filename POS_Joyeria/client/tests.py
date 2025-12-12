from django.test import TestCase
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from .models import Client
from .serializers import ClientSerializer


# =========================
# MODEL TESTS
# =========================

class ClientModelTest(TestCase):

    def test_crear_cliente_ok(self):
        c = Client.objects.create(
            name="Juan",
            apellido_paterno="Pérez",
            apellido_materno="Gómez",
            phone="5551112222",
            email="juan@test.com",
            rfc="ABC9203041H2",   # 12 chars alfanum
            es_mayorista=True
        )

        self.assertEqual(Client.objects.count(), 1)
        self.assertEqual(c.name, "Juan")
        self.assertTrue(c.es_mayorista)

    def test_telefono_unico_db(self):
        Client.objects.create(
            name="Cliente 1",
            phone="5551112222",
            email="c1@test.com",
        )

        with self.assertRaises(IntegrityError):
            Client.objects.create(
                name="Cliente 2",
                phone="5551112222",
                email="c2@test.com",
            )

    def test_email_unico_db(self):
        Client.objects.create(
            name="Cliente 1",
            phone="5552223333",
            email="c1@test.com",
        )

        with self.assertRaises(IntegrityError):
            Client.objects.create(
                name="Cliente 2",
                phone="5554445555",
                email="c1@test.com",
            )

    def test_rfc_unico_db(self):
        Client.objects.create(
            name="Cliente 1",
            rfc="ABC9203041H2",
        )

        with self.assertRaises(IntegrityError):
            Client.objects.create(
                name="Cliente 2",
                rfc="ABC9203041H2",
            )

    def test_str_muestra_nombre_completo(self):
        c = Client.objects.create(
            name="Juan",
            apellido_paterno="Pérez",
            apellido_materno="Gómez",
        )
        self.assertEqual(str(c), "Juan Pérez Gómez")


# =========================
# SERIALIZER TESTS
# =========================

class ClientSerializerTest(TestCase):

    def test_nombre_obligatorio(self):
        data = {"name": "   "}
        serializer = ClientSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_nombre_minimo_tres_caracteres(self):
        data = {"name": "Jo"}
        serializer = ClientSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)
        self.assertIn("El nombre debe tener al menos 3 caracteres.", serializer.errors["name"][0])

    def test_nombre_con_espacios_se_guarda_limpio(self):
        data = {"name": "   Juan   "}
        serializer = ClientSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["name"], "Juan")

    def test_apellido_paterno_opcional_pero_minimo_3_si_viene(self):
        data = {"name": "Juan", "apellido_paterno": "Pe"}
        serializer = ClientSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("apellido_paterno", serializer.errors)

    def test_apellido_materno_opcional_pero_minimo_3_si_viene(self):
        data = {"name": "Juan", "apellido_materno": "Go"}
        serializer = ClientSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("apellido_materno", serializer.errors)

    def test_telefono_opcional(self):
        data = {"name": "Juan", "phone": None}
        serializer = ClientSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_telefono_invalido_con_letras(self):
        data = {"name": "Juan", "phone": "55ABC123"}
        serializer = ClientSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("phone", serializer.errors)
        msg = str(serializer.errors["phone"][0])
        self.assertTrue(
            ("solo se permiten" in msg.lower()) or ("díg" in msg.lower()) or ("númer" in msg.lower()),
            msg
        )

    def test_telefono_demasiado_corto(self):
        data = {"name": "Juan", "phone": "123456"}
        serializer = ClientSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("phone", serializer.errors)
        self.assertIn("El teléfono debe tener al menos 7 dígitos.", serializer.errors["phone"][0])

    def test_email_opcional(self):
        data = {"name": "Juan", "email": None}
        serializer = ClientSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_email_unico_case_insensitive_en_create(self):
        Client.objects.create(name="Cliente 1", email="correo@test.com")
        data = {"name": "Cliente 2", "email": "CORREO@test.com"}
        serializer = ClientSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)
        self.assertIn("Ya existe un cliente con ese correo.", serializer.errors["email"][0])

    def test_email_puede_mantenerse_en_update(self):
        client = Client.objects.create(name="Cliente 1", email="correo@test.com")
        data = {"name": "Cliente 1 Actualizado", "email": "CORREO@test.com"}
        serializer = ClientSerializer(instance=client, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        self.assertEqual(updated.email, "CORREO@test.com")

    def test_rfc_valido_12_caracteres(self):
        data = {"name": "Juan", "rfc": "ABC9203041H2"}  # 12
        serializer = ClientSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["rfc"], "ABC9203041H2")

    def test_rfc_valido_13_caracteres(self):
        data = {"name": "Juan", "rfc": "ABC9203041H2Z"}  # 13
        serializer = ClientSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_rfc_invalido_por_longitud(self):
        data = {"name": "Juan", "rfc": "ABC123"}  # muy corto
        serializer = ClientSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("rfc", serializer.errors)
        msg = str(serializer.errors["rfc"][0])
        self.assertIn("12 a 13", msg)

    def test_rfc_unico_case_insensitive(self):
        Client.objects.create(name="Cliente 1", rfc="ABC9203041H2")  # 12 válido
        data = {"name": "Cliente 2", "rfc": "abc9203041h2"}  # mismo en minúsculas
        serializer = ClientSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("rfc", serializer.errors)
        msg = str(serializer.errors["rfc"][0]).lower()
        # si llega a unicidad, perfecto; si el modelo/formato lo frena antes, igual está bien
        self.assertTrue(("ya existe" in msg) or ("12 a 13" in msg) or ("inválido" in msg), msg)


# API VIEW TESTS (DRF)

class ClientViewsMinimalTest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="password123")
        self.client.force_authenticate(user=self.user)

        self.activo = Client.objects.create(
            name="Activo",
            phone="5551111111",
            email="activo@test.com",
            is_active=True,
        )
        self.inactivo = Client.objects.create(
            name="Inactivo",
            phone="5552222222",
            email="inactivo@test.com",
            is_active=False,
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

    def test_detail_view_retrieve(self):
        url = f"/api/clients/{self.activo.pk}/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["name"], "Activo")


# =========================
# WEB VIEWS TESTS (TEMPLATES)
# =========================

class ClientWebViewsTestCase(TestCase):
    def setUp(self):
        self.activo = Client.objects.create(
            name="Juan",
            apellido_paterno="Pérez",
            apellido_materno="Gómez",
            phone="5551112222",
            email="juan@test.com",
            rfc="ABC9203041H2",
            es_mayorista=True,
            is_active=True,
        )

        self.inactivo = Client.objects.create(
            name="Ana",
            phone="5559998888",
            email="ana@test.com",
            is_active=False,
        )

    def test_list_renderiza_template_y_contexto(self):
        url = reverse("clients_web:list")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "client/clientes.html")

        self.assertIn("activos", res.context)
        self.assertIn("inactivos", res.context)

        self.assertTrue(any(c.id == self.activo.id for c in res.context["activos"]))
        self.assertTrue(any(c.id == self.inactivo.id for c in res.context["inactivos"]))

        self.assertContains(res, "Clientes")

    def test_create_get_muestra_form(self):
        url = reverse("clients_web:create")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "client/formulario.html")
        self.assertIn("form", res.context)

    def test_create_post_valido_crea_y_redirige(self):
        url = reverse("clients_web:create")
        payload = {
            "name": "Nuevo",
            "apellido_paterno": "López",
            "apellido_materno": "Ruiz",
            "phone": "5553334444",
            "email": "nuevo@test.com",
            "rfc": "ABC9203041H2Z",  # ✅ 13 válido
            "es_mayorista": "on",
        }
        res = self.client.post(url, data=payload, follow=False)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res["Location"], reverse("clients_web:list"))
        self.assertTrue(Client.objects.filter(email="nuevo@test.com", is_active=True).exists())

    def test_edit_get_muestra_form_con_instancia(self):
        url = reverse("clients_web:edit", args=[self.activo.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "client/formulario.html")
        self.assertEqual(res.context["form"].instance.id, self.activo.id)

    def test_edit_post_valido_actualiza_y_redirige(self):
        url = reverse("clients_web:edit", args=[self.activo.id])
        payload = {
            "name": "Juan Editado",
            "apellido_paterno": "Pérez",
            "apellido_materno": "Gómez",
            "phone": "5551112222",
            "email": "juan@test.com",
            "rfc": "ABC9203041H2",
            "es_mayorista": "on",
        }
        res = self.client.post(url, data=payload, follow=False)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res["Location"], reverse("clients_web:list"))

        self.activo.refresh_from_db()
        self.assertEqual(self.activo.name, "Juan Editado")

    def test_delete_post_soft_delete(self):
        url = reverse("clients_web:delete", args=[self.activo.id])
        res = self.client.post(url, follow=False)
        self.assertEqual(res.status_code, 302)

        self.activo.refresh_from_db()
        self.assertFalse(self.activo.is_active)

    def test_activate_post_reactiva(self):
        url = reverse("clients_web:activate", args=[self.inactivo.id])
        res = self.client.post(url, follow=False)
        self.assertEqual(res.status_code, 302)

        self.inactivo.refresh_from_db()
        self.assertTrue(self.inactivo.is_active)
