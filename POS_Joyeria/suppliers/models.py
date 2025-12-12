from django.db import models
from django.core.validators import RegexValidator

solo_digitos = RegexValidator(regex=r'^\d+$',message="El teléfono solo debe contener números.")
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=30, unique=True) # valor unico
    phone = models.CharField(max_length=15,unique=True,validators=[solo_digitos]) #valor unico
    email = models.EmailField(unique=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

