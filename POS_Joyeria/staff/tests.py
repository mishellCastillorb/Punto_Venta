from django.test import TestCase
from django.db.utils import IntegrityError
from django.contrib.auth.models import User

from .models import Employee


class EmployeeModelTest(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1",
            password="test123"
        )

        self.user2 = User.objects.create_user(
            username="user2",
            password="test123"
        )

    def test_crear_empleado_ok(self):
        emp = Employee.objects.create(
            user=self.user1,
            nombre="Ana",
            apellido_paterno="López",
            apellido_materno="García",
            rol="VENDEDOR",
            phone="5551112222",
            address="Calle 1"
        )

        self.assertEqual(Employee.objects.count(), 1)
        self.assertEqual(emp.nombre, "Ana")
        self.assertTrue(emp.is_active)
        self.assertEqual(emp.rol, "VENDEDOR")

    def test_user_unico(self):
        Employee.objects.create(
            user=self.user1,
            nombre="Ana",
            apellido_paterno="López",
            phone="5551112222"
        )

        with self.assertRaises(IntegrityError):
            Employee.objects.create(
                user=self.user1,  # mismo user
                nombre="María",
                apellido_paterno="Pérez",
                phone="5553334444"
            )

    def test_phone_unico(self):
        Employee.objects.create(
            user=self.user1,
            nombre="Ana",
            apellido_paterno="López",
            phone="5551112222"
        )

        with self.assertRaises(IntegrityError):
            Employee.objects.create(
                user=self.user2,
                nombre="María",
                apellido_paterno="Pérez",
                phone="5551112222"  # mismo teléfono
            )

    def test_rol_por_defecto(self):
        emp = Employee.objects.create(
            user=self.user1,
            nombre="Ana",
            apellido_paterno="López",
            phone="5559990000"
        )

        self.assertEqual(emp.rol, "VENDEDOR")

    def test_str_muestra_nombre(self):
        emp = Employee.objects.create(
            user=self.user1,
            nombre="Ana",
            apellido_paterno="López",
            apellido_materno="García",
            phone="5557778888"
        )

        self.assertEqual(str(emp), "Ana López García")
