from django.test import TestCase
from django.db.utils import IntegrityError
from .models import Supplier


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

