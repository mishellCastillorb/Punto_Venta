from django.db import models

class Client(models.Model):
    name = models.CharField(max_length=100)
    apellido_paterno = models.CharField(
        max_length=70,
        blank=True,
        null=True
    )
    apellido_materno = models.CharField(
        max_length=70,
        blank=True,
        null=True
    )
    phone = models.CharField(
        max_length=15,
        unique=True,
        blank=True,
        null=True
    )
    email = models.EmailField(
        unique=True,
        blank=True,
        null=True
    )
    address = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )
    rfc = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True
    )
    es_mayorista = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
#Muestra nombre completo sin espacios dobles.
        return " ".join(
            part for part in [
                self.name,
                self.apellido_paterno,
                self.apellido_materno
            ] if part
        )
