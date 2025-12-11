from django.test import TestCase
from django.db.utils import IntegrityError
from .models import Supplier
from rest_framework.test import APITestCase
from django.urls import reverse


class SupplierModelTest(TestCase):

    def test_crear_provedor(self):
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

    def test_codigo_unico(self):
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

    def test_telfono_unico(self):
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

    def test_correo_unico(self):
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
        """Se puede crear un proveedor válido."""
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
        """Rechaza crear proveedor sin code, phone o email."""
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

    def test_rechaza_code_duplicado(self):
        """No permite duplicar el código del proveedor."""
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
        """No permite duplicar el teléfono del proveedor."""
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
        """No permite duplicar el correo del proveedor."""
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
    def test_nombre_demasiado_corto(self):
        """Rechaza nombre con menos de 3 caracteres."""
        data = {
            "name": "Ab",
            "code": "P10",
            "phone": "5551234567",
            "email": "p10@test.com",
        }
        response = self.client.post(self.url_list, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.data)

    def test_telefono_no_numerico(self):
        """Rechaza teléfono con caracteres no numéricos."""
        data = {
            "name": "Proveedor Tel",
            "code": "P11",
            "phone": "55-50A01111",   # letras y guión
            "email": "p11@test.com",
        }
        response = self.client.post(self.url_list, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("phone", response.data)

    def test_telefono_demasiado_corto(self):
        """Rechaza teléfono con menos de 7 dígitos."""
        data = {
            "name": "Proveedor Tel C",
            "code": "P12",
            "phone": "123456",   # 6 dígitos
            "email": "p12@test.com",
        }
        response = self.client.post(self.url_list, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("phone", response.data)

    def test_email_formato_invalido(self):
        """Rechaza email con formato inválido."""
        data = {
            "name": "Proveedor Mail Malo",
            "code": "P13",
            "phone": "5551234567",
            "email": "no-es-correo",   # sin @
        }
        response = self.client.post(self.url_list, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_actualizar_mantiene_code_unico_correctamente(self):
        """
        Al actualizar un proveedor, puede mantener su mismo code/phone/email
        sin disparar las validaciones de duplicado.
        """
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

