from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from client.models import Client
from products.models import Product


class Sale(models.Model):
    class Status(models.TextChoices):
        REALIZADA = "REALIZADA", "Realizada"
        CANCELADA = "CANCELADA", "Cancelada"

    class PaymentMethod(models.TextChoices):
        CASH = "CASH", "Efectivo"
        CARD = "CARD", "Tarjeta"
        TRANSFER = "TRANSFER", "Transferencia"

    fecha = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.REALIZADA)

    cliente = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    nombre_cliente = models.CharField(max_length=100, null=True, blank=True)
    cliente_telefono = models.CharField(max_length=20, null=True, blank=True)

    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="ventas"
    )

    descuento = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0, validators=[MinValueValidator(0)]
    )

    metodo_pago = models.CharField(
        max_length=10,
        choices=PaymentMethod.choices,
        null=True, blank=True
    )

    cantidad_pagada = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        validators=[MinValueValidator(0)]
    )

    cambio = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        validators=[MinValueValidator(0)]
    )

    subtotal = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True,
        validators=[MinValueValidator(0)]
    )

    total = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True,
        validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return f"Venta #{self.id} - {self.fecha.date()}"

    @property
    def cliente_display(self):
        if self.cliente_id:
            return str(self.cliente)
        return self.nombre_cliente or "Cliente rápido"


class SaleItem(models.Model):
    venta = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Product, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1)])
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    @property
    def subtotal(self):
        return (self.cantidad or 0) * self.precio

    def __str__(self):
        return f"{self.producto} x{self.cantidad}"

