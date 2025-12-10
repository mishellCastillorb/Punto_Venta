from django.db import models


class Supplier(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=30, unique=True) # valor unico
    phone = models.CharField(max_length=15, unique=True) #valor unico
    email = models.EmailField(unique=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

