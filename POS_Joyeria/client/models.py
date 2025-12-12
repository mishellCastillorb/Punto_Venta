from django.db import models
from django.core.validators import RegexValidator

digits_only = RegexValidator(
    regex=r"^\d+$",
    message="Solo se permiten números."
)

rfc_simple_12_13 = RegexValidator(
    regex=r"^[A-ZÑ&0-9]{12,13}$",
    message="El RFC debe tener 12 a 13 caracteres (letras y números)."
)

class Client(models.Model):
    name = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=70, blank=True, null=True)
    apellido_materno = models.CharField(max_length=70, blank=True, null=True)

    phone = models.CharField(
        max_length=15,
        unique=True,
        blank=True,
        null=True,
        validators=[digits_only],
    )

    email = models.EmailField(unique=True, blank=True, null=True)

    rfc = models.CharField(
        max_length=13,
        unique=True,
        blank=True,
        null=True,
        validators=[rfc_simple_12_13],  # ✅ cambia esto
    )

    es_mayorista = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return " ".join(
            part for part in [self.name, self.apellido_paterno, self.apellido_materno] if part
        )
