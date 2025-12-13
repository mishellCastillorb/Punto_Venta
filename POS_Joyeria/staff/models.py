from django.db import models
from django.contrib.auth.models import User

class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="staff_profile")
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15, unique=True)
    direccion = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.user.username} - {self.nombre} {self.apellido_paterno}"
