from django.test import TestCase
from django.urls import reverse
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from .models import StaffProfile
from .forms import StaffCreateForm, StaffEditForm


User = get_user_model()


# MODEL TESTS

class StaffProfileModelTest(TestCase):
    def test_crear_profile_ok_y_str(self):
        u = User.objects.create_user(username="u1", password="pass12345", email="u1@test.com")
        p = StaffProfile.objects.create(
            user=u,
            nombre="Ana",
            apellido_paterno="López",
            apellido_materno="García",
            telefono="5551112222",
            direccion="Calle 1",
        )
        self.assertEqual(StaffProfile.objects.count(), 1)
        self.assertEqual(str(p), "u1 - Ana López")

    def test_telefono_unico_db(self):
        u1 = User.objects.create_user(username="u1", password="pass12345", email="u1@test.com")
        u2 = User.objects.create_user(username="u2", password="pass12345", email="u2@test.com")

        StaffProfile.objects.create(
            user=u1,
            nombre="Ana",
            apellido_paterno="López",
            apellido_materno="García",
            telefono="5551112222",
            direccion="Calle 1",
        )

        with self.assertRaises(IntegrityError):
            StaffProfile.objects.create(
                user=u2,
                nombre="Beto",
                apellido_paterno="Ruiz",
                apellido_materno="Pérez",
                telefono="5551112222",  # duplicado
                direccion="Calle 2",
            )


# FORM TESTS - StaffCreateForm

class StaffCreateFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.g_admin, _ = Group.objects.get_or_create(name="AdminPOS")
        cls.g_vend, _ = Group.objects.get_or_create(name="VendedorPOS")

        cls.superadmin = User.objects.create_superuser(
            username="root",
            password="pass12345",
            email="root@test.com",
        )
        cls.admin = User.objects.create_user(username="admin", password="pass12345", email="admin@test.com")
        cls.admin.groups.add(cls.g_admin)
        cls.admin.is_staff = True
        cls.admin.save(update_fields=["is_staff"])

        # existente para validar duplicados
        cls.existing = User.objects.create_user(username="exist", password="pass12345", email="exist@test.com")
        cls.existing.is_staff = True
        cls.existing.save(update_fields=["is_staff"])
        StaffProfile.objects.create(
            user=cls.existing,
            nombre="X",
            apellido_paterno="Y",
            apellido_materno="Z",
            telefono="5559998888",
            direccion="Dir",
        )

    def _base_payload(self):
        return {
            "username": "nuevo",
            "password1": "secret1",
            "password2": "secret1",
            "nombre": "Juan",
            "apellido_paterno": "Pérez",
            "apellido_materno": "Gómez",
            "email": "nuevo@test.com",
            "telefono": "5551112222",
            "direccion": "Calle 123",
            "rol": "VendedorPOS",
        }

    def test_allowed_roles_superadmin(self):
        form = StaffCreateForm(request_user=self.superadmin)
        roles = [c[0] for c in form.fields["rol"].choices]
        self.assertIn("AdminPOS", roles)
        self.assertIn("VendedorPOS", roles)

    def test_allowed_roles_admin_normal(self):
        form = StaffCreateForm(request_user=self.admin)
        roles = [c[0] for c in form.fields["rol"].choices]
        self.assertEqual(roles, ["VendedorPOS"])

    def test_username_obligatorio_minimo_y_unico(self):
        payload = self._base_payload()
        payload["username"] = "  "
        form = StaffCreateForm(data=payload, request_user=self.admin)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

        payload = self._base_payload()
        payload["username"] = "ab"
        form = StaffCreateForm(data=payload, request_user=self.admin)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

        payload = self._base_payload()
        payload["username"] = "Exist"  # existe (case-insensitive)
        form = StaffCreateForm(data=payload, request_user=self.admin)
        self.assertFalse(form.is_valid())
        self.assertIn("Ese usuario ya existe.", form.errors["username"][0])

    def test_email_obligatorio_y_unico_case_insensitive(self):
        payload = self._base_payload()
        payload["email"] = "  "
        form = StaffCreateForm(data=payload, request_user=self.admin)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

        payload = self._base_payload()
        payload["email"] = "EXIST@test.com"
        form = StaffCreateForm(data=payload, request_user=self.admin)
        self.assertFalse(form.is_valid())
        self.assertIn("Ese correo ya está registrado.", form.errors["email"][0])

    def test_telefono_validaciones_y_unico(self):
        payload = self._base_payload()
        payload["telefono"] = "55ABC"
        form = StaffCreateForm(data=payload, request_user=self.admin)
        self.assertFalse(form.is_valid())
        self.assertIn("telefono", form.errors)

        payload = self._base_payload()
        payload["telefono"] = "123456"  # < 7
        form = StaffCreateForm(data=payload, request_user=self.admin)
        self.assertFalse(form.is_valid())
        self.assertIn("al menos 7", form.errors["telefono"][0].lower())

        payload = self._base_payload()
        payload["telefono"] = "1" * 16  # > 15 (puede caer en max_length del Field)
        form = StaffCreateForm(data=payload, request_user=self.admin)
        self.assertFalse(form.is_valid())
        msg = str(form.errors["telefono"][0]).lower()
        self.assertTrue(
            ("no debe exceder 15" in msg) or ("at most 15" in msg) or ("max" in msg),
            msg
        )

        payload = self._base_payload()
        payload["telefono"] = "5559998888"  # ya existe en StaffProfile
        form = StaffCreateForm(data=payload, request_user=self.admin)
        self.assertFalse(form.is_valid())
        self.assertIn("Ese teléfono ya está registrado.", form.errors["telefono"][0])

    def test_password_match_y_minimo(self):
        payload = self._base_payload()
        payload["password1"] = "123"  # < 6
        payload["password2"] = "123"
        form = StaffCreateForm(data=payload, request_user=self.admin)
        self.assertFalse(form.is_valid())
        self.assertIn("password1", form.errors)

        payload = self._base_payload()
        payload["password2"] = "otra"
        form = StaffCreateForm(data=payload, request_user=self.admin)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_clean_rol_no_permitido(self):
        # OJO: ChoiceField valida choices antes de clean_rol
        payload = self._base_payload()
        payload["rol"] = "AdminPOS"  # admin normal NO puede asignar AdminPOS
        form = StaffCreateForm(data=payload, request_user=self.admin)
        self.assertFalse(form.is_valid())
        self.assertIn("rol", form.errors)

        msg = str(form.errors["rol"][0]).lower()
        self.assertTrue(
            ("no tienes permiso" in msg) or ("select a valid choice" in msg) or ("valid choice" in msg),
            msg
        )

    def test_save_crea_user_staffprofile_y_grupo(self):
        payload = self._base_payload()
        form = StaffCreateForm(data=payload, request_user=self.admin)
        self.assertTrue(form.is_valid(), form.errors)

        u = form.save()

        self.assertTrue(u.is_staff)
        self.assertTrue(u.is_active)
        self.assertTrue(u.groups.filter(name="VendedorPOS").exists())
        self.assertTrue(hasattr(u, "staff_profile"))
        self.assertEqual(u.staff_profile.telefono, "5551112222")


# FORM TESTS - StaffEditForm

class StaffEditFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.g_admin, _ = Group.objects.get_or_create(name="AdminPOS")
        cls.g_vend, _ = Group.objects.get_or_create(name="VendedorPOS")

        cls.admin = User.objects.create_user(username="admin", password="pass12345", email="admin@test.com")
        cls.admin.groups.add(cls.g_admin)
        cls.admin.is_staff = True
        cls.admin.save(update_fields=["is_staff"])

        cls.u = User.objects.create_user(username="vend", password="pass12345", email="vend@test.com")
        cls.u.groups.add(cls.g_vend)
        cls.u.is_staff = True
        cls.u.save(update_fields=["is_staff"])

        cls.profile = StaffProfile.objects.create(
            user=cls.u,
            nombre="V",
            apellido_paterno="P",
            apellido_materno="M",
            telefono="5551112222",
            direccion="Dir",
        )

        cls.other_u = User.objects.create_user(username="other", password="pass12345", email="other@test.com")
        cls.other_u.is_staff = True
        cls.other_u.save(update_fields=["is_staff"])
        cls.other_p = StaffProfile.objects.create(
            user=cls.other_u,
            nombre="O",
            apellido_paterno="O",
            apellido_materno="O",
            telefono="5559998888",
            direccion="Dir2",
        )

    def test_email_unico_excluye_self(self):
        form = StaffEditForm(
            data={
                "nombre": "V",
                "apellido_paterno": "P",
                "apellido_materno": "M",
                "telefono": "5551112222",
                "direccion": "Dir",
                "email": "VEND@test.com",
                "rol": "VendedorPOS",
            },
            instance=self.profile,
            user_instance=self.u,
            request_user=self.admin,
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_email_duplicado_falla(self):
        form = StaffEditForm(
            data={
                "nombre": "V",
                "apellido_paterno": "P",
                "apellido_materno": "M",
                "telefono": "5551112222",
                "direccion": "Dir",
                "email": "OTHER@test.com",  # ya existe
                "rol": "VendedorPOS",
            },
            instance=self.profile,
            user_instance=self.u,
            request_user=self.admin,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_telefono_unico_excluye_self(self):
        form = StaffEditForm(
            data={
                "nombre": "V",
                "apellido_paterno": "P",
                "apellido_materno": "M",
                "telefono": "5559998888",  # ya existe en otro profile
                "direccion": "Dir",
                "email": "vend@test.com",
                "rol": "VendedorPOS",
            },
            instance=self.profile,
            user_instance=self.u,
            request_user=self.admin,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("telefono", form.errors)

    def test_save_actualiza_email_y_grupo(self):
        form = StaffEditForm(
            data={
                "nombre": "V Edit",
                "apellido_paterno": "P",
                "apellido_materno": "M",
                "telefono": "5551112222",
                "direccion": "Dir",
                "email": "nuevoemail@test.com",
                "rol": "VendedorPOS",
            },
            instance=self.profile,
            user_instance=self.u,
            request_user=self.admin,
        )
        self.assertTrue(form.is_valid(), form.errors)
        prof = form.save()

        prof.refresh_from_db()
        self.u.refresh_from_db()
        self.assertEqual(prof.nombre, "V Edit")
        self.assertEqual(self.u.email, "nuevoemail@test.com")
        self.assertTrue(self.u.groups.filter(name="VendedorPOS").exists())


# HOME / AUTH VIEWS TESTS

class StaffAuthViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.g_admin, _ = Group.objects.get_or_create(name="AdminPOS")
        cls.g_vend, _ = Group.objects.get_or_create(name="VendedorPOS")

        cls.staff_admin = User.objects.create_user(username="admin", password="pass12345", email="admin@test.com")
        cls.staff_admin.is_staff = True
        cls.staff_admin.save(update_fields=["is_staff"])
        cls.staff_admin.groups.add(cls.g_admin)

        cls.staff_vend = User.objects.create_user(username="vend", password="pass12345", email="vend@test.com")
        cls.staff_vend.is_staff = True
        cls.staff_vend.save(update_fields=["is_staff"])
        cls.staff_vend.groups.add(cls.g_vend)

        cls.no_staff = User.objects.create_user(username="nostaff", password="pass12345", email="nostaff@test.com")
        cls.no_staff.is_staff = False
        cls.no_staff.save(update_fields=["is_staff"])

        cls.staff_sin_rol = User.objects.create_user(username="sinrol", password="pass12345", email="sinrol@test.com")
        cls.staff_sin_rol.is_staff = True
        cls.staff_sin_rol.save(update_fields=["is_staff"])

    def test_login_pos_credenciales_invalidas(self):
        url = reverse("login_pos")
        res = self.client.post(url, {"username": "x", "password": "y"}, follow=False)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res["Location"], url)

    def test_login_pos_no_staff(self):
        url = reverse("login_pos")
        res = self.client.post(url, {"username": "nostaff", "password": "pass12345"}, follow=False)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res["Location"], url)

    def test_login_pos_staff_ok_redirige_post_login(self):
        url = reverse("login_pos")
        res = self.client.post(url, {"username": "admin", "password": "pass12345"}, follow=False)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res["Location"], reverse("post_login"))

    def test_post_login_no_autenticado_redirige_login(self):
        url = reverse("post_login")
        res = self.client.get(url, follow=False)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res["Location"], reverse("login_pos"))

    def test_post_login_con_rol_valido_redirige_productos(self):
        self.client.login(username="vend", password="pass12345")
        url = reverse("post_login")
        res = self.client.get(url, follow=False)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res["Location"], reverse("products_web:list"))

    def test_post_login_staff_sin_rol_lo_saca_y_redirige_login(self):
        self.client.login(username="sinrol", password="pass12345")
        url = reverse("post_login")
        res = self.client.get(url, follow=False)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res["Location"], reverse("login_pos"))

    def test_logout_pos(self):
        self.client.login(username="admin", password="pass12345")
        url = reverse("logout_pos")
        res = self.client.get(url, follow=False)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res["Location"], reverse("login_pos"))


# WEB VIEWS TESTS

class StaffWebViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.g_admin, _ = Group.objects.get_or_create(name="AdminPOS")
        cls.g_vend, _ = Group.objects.get_or_create(name="VendedorPOS")

        cls.admin = User.objects.create_user(username="admin", password="pass12345", email="admin@test.com")
        cls.admin.is_staff = True
        cls.admin.save(update_fields=["is_staff"])
        cls.admin.groups.add(cls.g_admin)

        cls.superadmin = User.objects.create_superuser(username="root", password="pass12345", email="root@test.com")
        cls.superadmin.is_staff = True
        cls.superadmin.save(update_fields=["is_staff"])

        cls.v_user = User.objects.create_user(username="vend1", password="pass12345", email="vend1@test.com")
        cls.v_user.is_staff = True
        cls.v_user.save(update_fields=["is_staff"])
        cls.v_user.groups.add(cls.g_vend)

        cls.v_profile = StaffProfile.objects.create(
            user=cls.v_user,
            nombre="V",
            apellido_paterno="P",
            apellido_materno="M",
            telefono="5551112222",
            direccion="Dir",
        )

        cls.a_user = User.objects.create_user(username="admin2", password="pass12345", email="admin2@test.com")
        cls.a_user.is_staff = True
        cls.a_user.save(update_fields=["is_staff"])
        cls.a_user.groups.add(cls.g_admin)

        cls.a_profile = StaffProfile.objects.create(
            user=cls.a_user,
            nombre="A",
            apellido_paterno="B",
            apellido_materno="C",
            telefono="5559998888",
            direccion="Dir2",
        )

    def login_admin(self):
        ok = self.client.login(username="admin", password="pass12345")
        self.assertTrue(ok)

    def login_root(self):
        ok = self.client.login(username="root", password="pass12345")
        self.assertTrue(ok)

    def test_list_200_context(self):
        self.login_admin()
        url = reverse("staff_web:list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertIn("activos", res.context)
        self.assertIn("inactivos", res.context)
        self.assertIn("role_user", res.context)

    def test_create_post_crea_vendedor(self):
        self.login_admin()
        url = reverse("staff_web:create")
        payload = {
            "username": "nuevo",
            "password1": "secret1",
            "password2": "secret1",
            "nombre": "Juan",
            "apellido_paterno": "Pérez",
            "apellido_materno": "Gómez",
            "email": "nuevo@test.com",
            "telefono": "5552223333",
            "direccion": "Calle 123",
            "rol": "VendedorPOS",
        }
        res = self.client.post(url, data=payload, follow=False)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res["Location"], reverse("staff_web:list"))
        u = User.objects.get(username="nuevo")
        self.assertTrue(u.is_staff)
        self.assertTrue(u.groups.filter(name="VendedorPOS").exists())
        self.assertTrue(hasattr(u, "staff_profile"))

    def test_edit_post_actualiza(self):
        self.login_admin()
        url = reverse("staff_web:edit", args=[self.v_profile.id])

        payload = {
            "nombre": "V Edit",
            "apellido_paterno": "P",
            "apellido_materno": "M",
            "telefono": "5551112222",
            "direccion": "Dir",
            "email": "vend1nuevo@test.com",
            "rol": "VendedorPOS",
        }
        res = self.client.post(url, data=payload, follow=False)
        self.assertEqual(res.status_code, 302)

        self.v_profile.refresh_from_db()
        self.v_user.refresh_from_db()
        self.assertEqual(self.v_profile.nombre, "V Edit")
        self.assertEqual(self.v_user.email, "vend1nuevo@test.com")

    def test_delete_no_puede_desactivarse_a_si_mismo(self):
        StaffProfile.objects.create(
            user=self.admin,
            nombre="Admin",
            apellido_paterno="X",
            apellido_materno="Y",
            telefono="5554445555",
            direccion="DirAdmin",
        )

        self.login_admin()
        profile_admin = StaffProfile.objects.get(user=self.admin)

        url = reverse("staff_web:delete", args=[profile_admin.id])
        res = self.client.post(url, follow=False)

        self.assertEqual(res.status_code, 302)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)

    def test_delete_admin_normal_puede_desactivar_vendedor(self):
        self.login_admin()
        url = reverse("staff_web:delete", args=[self.v_profile.id])
        res = self.client.post(url, follow=False)
        self.assertEqual(res.status_code, 302)

        self.v_user.refresh_from_db()
        self.assertFalse(self.v_user.is_active)

    def test_delete_admin_normal_no_puede_desactivar_adminpos(self):
        self.login_admin()
        url = reverse("staff_web:delete", args=[self.a_profile.id])
        res = self.client.post(url, follow=False)
        self.assertEqual(res.status_code, 302)

        self.a_user.refresh_from_db()
        self.assertTrue(self.a_user.is_active)

    def test_delete_superadmin_puede_desactivar_adminpos(self):
        self.login_root()
        url = reverse("staff_web:delete", args=[self.a_profile.id])
        res = self.client.post(url, follow=False)
        self.assertEqual(res.status_code, 302)

        self.a_user.refresh_from_db()
        self.assertFalse(self.a_user.is_active)

    def test_activate_admin_normal_solo_vendedor(self):
        self.v_user.is_active = False
        self.v_user.save(update_fields=["is_active"])

        self.login_admin()
        url = reverse("staff_web:activate", args=[self.v_profile.id])
        res = self.client.post(url, follow=False)
        self.assertEqual(res.status_code, 302)

        self.v_user.refresh_from_db()
        self.assertTrue(self.v_user.is_active)

    def test_activate_admin_normal_no_adminpos(self):
        self.a_user.is_active = False
        self.a_user.save(update_fields=["is_active"])

        self.login_admin()
        url = reverse("staff_web:activate", args=[self.a_profile.id])
        res = self.client.post(url, follow=False)
        self.assertEqual(res.status_code, 302)

        self.a_user.refresh_from_db()
        self.assertFalse(self.a_user.is_active)

    def test_activate_superadmin_puede_adminpos(self):
        self.a_user.is_active = False
        self.a_user.save(update_fields=["is_active"])

        self.login_root()
        url = reverse("staff_web:activate", args=[self.a_profile.id])
        res = self.client.post(url, follow=False)
        self.assertEqual(res.status_code, 302)

        self.a_user.refresh_from_db()
        self.assertTrue(self.a_user.is_active)
