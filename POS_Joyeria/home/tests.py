from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from home.views import login_pos, logout_pos, post_login_redirect

User = get_user_model()


def _add_session_and_messages(request):
    middleware = SessionMiddleware(lambda r: None)
    middleware.process_request(request)
    request.session.save()
    setattr(request, "_messages", FallbackStorage(request))
    return request


class HomeViewsTest(TestCase):
    def setUp(self):
        self.rf = RequestFactory()
        self.staff = User.objects.create_user(
            username="staff",
            password="12345678",
            is_staff=True
        )
        self.nostaff = User.objects.create_user(
            username="nostaff",
            password="12345678",
            is_staff=False
        )

    def test_post_login_redirect_no_auth_redirige_login_pos(self):
        req = self.rf.get("/")
        _add_session_and_messages(req)
        req.user = AnonymousUser()
        res = post_login_redirect(req)
        self.assertEqual(res.status_code, 302)
        self.assertIn("login", res["Location"])

    def test_post_login_redirect_auth_redirige_products(self):
        req = self.rf.get("/")
        _add_session_and_messages(req)
        req.user = self.staff
        res = post_login_redirect(req)
        self.assertEqual(res.status_code, 302)
        self.assertIn("productos", res["Location"])

    def test_login_get_renderiza_y_pasa_next(self):
        req = self.rf.get("/login/?next=/productos/")
        _add_session_and_messages(req)
        req.user = AnonymousUser()
        res = login_pos(req)
        self.assertEqual(res.status_code, 200)
        content = res.content.decode("utf-8")
        self.assertIn('name="next"', content)
        self.assertIn('value="/productos/"', content)

    def test_login_si_ya_esta_autenticado_redirige_products(self):
        req = self.rf.get("/login/")
        _add_session_and_messages(req)
        req.user = self.staff
        res = login_pos(req)
        self.assertEqual(res.status_code, 302)
        self.assertIn("productos", res["Location"])

    def test_login_post_credenciales_incorrectas_retorna_200(self):
        req = self.rf.post("/login/", data={"username": "staff", "password": "MAL", "next": ""})
        _add_session_and_messages(req)
        req.user = AnonymousUser()
        res = login_pos(req)
        self.assertEqual(res.status_code, 200)

    def test_login_post_usuario_no_staff_no_acceso(self):
        req = self.rf.post("/login/", data={"username": "nostaff", "password": "12345678", "next": ""})
        _add_session_and_messages(req)
        req.user = AnonymousUser()
        res = login_pos(req)
        self.assertEqual(res.status_code, 200)

    def test_login_post_ok_sin_next_redirige_products(self):
        req = self.rf.post("/login/", data={"username": "staff", "password": "12345678", "next": ""})
        _add_session_and_messages(req)
        req.user = AnonymousUser()
        res = login_pos(req)
        self.assertEqual(res.status_code, 302)
        self.assertIn("productos", res["Location"])

    def test_login_post_ok_con_next_seguro_redirige_next(self):
        req = self.rf.post("/login/", data={"username": "staff", "password": "12345678", "next": "/productos/"})
        _add_session_and_messages(req)
        req.user = AnonymousUser()
        res = login_pos(req)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res["Location"], "/productos/")

    def test_login_post_ok_con_next_inseguro_ignora_y_redirige_products(self):
        req = self.rf.post("/login/", data={"username": "staff", "password": "12345678", "next": "https://evil.com/phish"})
        _add_session_and_messages(req)
        req.user = AnonymousUser()
        res = login_pos(req)
        self.assertEqual(res.status_code, 302)
        self.assertIn("productos", res["Location"])

    def test_logout_sin_next_redirige_login(self):
        req = self.rf.get("/logout/")
        _add_session_and_messages(req)
        req.user = self.staff
        res = logout_pos(req)
        self.assertEqual(res.status_code, 302)
        self.assertIn("login", res["Location"])

    def test_logout_con_next_redirige_login_con_query_next(self):
        req = self.rf.get("/logout/?next=/productos/")
        _add_session_and_messages(req)
        req.user = self.staff
        res = logout_pos(req)
        self.assertEqual(res.status_code, 302)
        self.assertIn("login", res["Location"])
        self.assertIn("next=/productos/", res["Location"])
