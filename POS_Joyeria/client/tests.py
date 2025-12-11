from django.test import TestCase
from django.db.utils import IntegrityError
from .models import Client
from .serializers import ClientSerializer
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

class ClientModelTest(TestCase):

    def test_crear_cliente_ok(self):
        """Se puede crear un cliente con datos básicos."""
        c = Client.objects.create(
            name="Juan",
            apellido_paterno="Pérez",
            apellido_materno="Gómez",
            phone="5551112222",
            email="juan@test.com",
            address="Calle 1",
            rfc="ABC123456789",
            es_mayorista=True
        )

        self.assertEqual(Client.objects.count(), 1)
        self.assertEqual(c.name, "Juan")
        self.assertTrue(c.es_mayorista)

    def test_telefono_unico(self):
        """El teléfono debe ser único."""
        Client.objects.create(
            name="Cliente 1",
            phone="5551112222",
            email="c1@test.com",
            rfc="RFC1111"
        )

        with self.assertRaises(IntegrityError):
            Client.objects.create(
                name="Cliente 2",
                phone="5551112222",  # igual
                email="c2@test.com",
                rfc="RFC2222"
            )

    def test_email_unico(self):
        """El email debe ser único."""
        Client.objects.create(
            name="Cliente 1",
            phone="5552223333",
            email="c1@test.com",
            rfc="RFC1111"
        )

        with self.assertRaises(IntegrityError):
            Client.objects.create(
                name="Cliente 2",
                phone="5554445555",
                email="c1@test.com",  # igual
                rfc="RFC2222"
            )

    def test_rfc_unico(self):
        """El RFC debe ser único."""
        Client.objects.create(
            name="Cliente 1",
            phone="5552223333",
            email="c1@test.com",
            rfc="ABC123"
        )

        with self.assertRaises(IntegrityError):
            Client.objects.create(
                name="Cliente 2",
                phone="5554445555",
                email="c2@test.com",
                rfc="ABC123"  # igual
            )

    def test_str_muestra_nombre_completo(self):
        """El método __str__ muestra el nombre completo correctamente."""
        c = Client.objects.create(
            name="Juan",
            apellido_paterno="Pérez",
            apellido_materno="Gómez",
        )

        self.assertEqual(str(c), "Juan Pérez Gómez")
class ClientSerializerTest(TestCase):

    def test_nombre_obligatorio(self):
        """El nombre es obligatorio."""
        data = {
            "name": "   ",
            "phone": "5551112222",
            "email": "test@test.com",
        }
        serializer = ClientSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)
        # No nos casamos con el texto exacto del mensaje
        self.assertGreater(len(serializer.errors["name"]), 0)

    def test_nombre_minimo_tres_caracteres(self):
        """El nombre debe tener al menos 3 caracteres."""
        data = {
            "name": "Jo",
            "phone": "5551112222",
            "email": "test@test.com",
        }
        serializer = ClientSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)
        self.assertIn(
            "El nombre debe tener al menos 3 caracteres.",
            serializer.errors["name"][0],
        )

    def test_nombre_con_espacios_se_guarda_limpio(self):
        """El nombre se trimmea (sin espacios al inicio/fin)."""
        data = {
            "name": "   Juan   ",
            "phone": "5551112222",
            "email": "test@test.com",
        }
        serializer = ClientSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["name"], "Juan")

    def test_telefono_opcional(self):
        """El teléfono puede ser opcional (null/blank)."""
        data = {
            "name": "Juan",
            "phone": None,
            "email": "test@test.com",
        }
        serializer = ClientSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_telefono_invalido_con_letras(self):
        """El teléfono solo debe tener dígitos (y + opcional)."""
        data = {
            "name": "Juan",
            "phone": "55ABC123",
            "email": "test@test.com",
        }
        serializer = ClientSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("phone", serializer.errors)
        self.assertIn(
            "El teléfono solo debe contener dígitos (y opcionalmente + para ladas).",
            serializer.errors["phone"][0],
        )

    def test_telefono_valido_con_mas_y_espacios(self):
        """El teléfono es válido con espacios y +."""
        data = {
            "name": "Juan",
            "phone": "+52 55 111 2222",  # <= 15 caracteres
            "email": "test@test.com",
        }
        serializer = ClientSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_email_opcional(self):
        """El email puede ir vacío."""
        data = {
            "name": "Juan",
            "phone": "5551112222",
            "email": None,
        }
        serializer = ClientSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_email_unico_en_create(self):
        """No se puede crear cliente con email duplicado (case-insensitive)."""
        Client.objects.create(
            name="Cliente 1",
            phone="5551112222",
            email="correo@test.com",
        )

        data = {
            "name": "Cliente 2",
            "phone": "5552223333",
            "email": "CORREO@test.com",  # misma pero distinto case
        }
        serializer = ClientSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)
        # No afirmamos el texto exacto, porque puede venir del UniqueValidator o del validate_email

    def test_email_puede_mantenerse_en_update(self):
        """
        Al actualizar un cliente, puede mantener su mismo email
        sin disparar error de unicidad.
        """
        client = Client.objects.create(
            name="Cliente 1",
            phone="5551112222",
            email="correo@test.com",
        )

        data = {
            "name": "Cliente 1 Actualizado",
            "phone": "5551112222",
            "email": "CORREO@test.com",  # mismo pero en mayúsculas
        }
        serializer = ClientSerializer(instance=client, data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        self.assertEqual(updated.email, "CORREO@test.com")
        self.assertEqual(updated.name, "Cliente 1 Actualizado")



class ClientViewsMinimalTest(APITestCase):
    def setUp(self):
        # Usuario para autenticación
        User = get_user_model()
        self.user = User.objects.create_user(
            username="tester",
            password="password123"
        )
        self.client.force_authenticate(user=self.user)

        # Clientes base
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

        # Ajusta estas URLs si en tu urls.py son distintas
        self.list_url = "/api/clients/list/"
        self.create_url = "/api/clients/create/"

    def test_list_view_solo_activos(self):
        """ListAPIView debe devolver solo clientes activos."""
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["name"], "Activo")

    def test_create_view_crea_cliente(self):
        """CreateAPIView crea un cliente válido."""
        data = {
            "name": "Nuevo",
            "phone": "5553334444",
            "email": "nuevo@test.com",
            "rfc": "RFC123",
        }
        resp = self.client.post(self.create_url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Client.objects.filter(email="nuevo@test.com").exists())

    def test_detail_view_retrieve(self):
        """RetrieveUpdateAPIView permite obtener un cliente."""
        url = f"/api/clients/{self.activo.pk}/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["name"], "Activo")

