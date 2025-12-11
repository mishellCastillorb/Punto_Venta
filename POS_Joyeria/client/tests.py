from django.test import TestCase
from django.db.utils import IntegrityError
from .models import Client


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
