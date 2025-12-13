from django.urls import path
from .views import login_pos, logout_pos, post_login_redirect

urlpatterns = [
    path("login/", login_pos, name="login_pos"),
    path("logout/", logout_pos, name="logout_pos"),
    path("", post_login_redirect, name="post_login"),
]
