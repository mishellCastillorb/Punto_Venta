from django.urls import path
from .views import login_pos, logout_pos, home_pos, post_login_redirect

urlpatterns = [
    path("login/", login_pos, name="login_pos"),
    path("logout/", logout_pos, name="logout_pos"),
    path("", post_login_redirect, name="post_login"),
    path("inicio/", home_pos, name="home_pos"),
]
