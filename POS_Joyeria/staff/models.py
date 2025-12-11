from django.db import models
from django.contrib.auth.models import User


class Employee(models.Model):
    # Usuario vinculado (único por OneToOne)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        unique=True
    )
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=70)
    apellido_materno = models.CharField(max_length=70, blank=True, null=True)
    # Rol del empleado
    ROL_CHOICES = (
        ("SUPERADMIN", "Superadministrador"),
        ("ADMIN", "Administrador"),
        ("VENDEDOR", "Vendedor"),
    )
    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default="VENDEDOR"
    )
    # Datos de contacto
    phone = models.CharField(
        max_length=20,
        unique=True
    )
    address = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno or ''} {self.apellido_materno or ''}".strip()
