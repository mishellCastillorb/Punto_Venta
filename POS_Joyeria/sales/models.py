from django.db import models
from django.contrib.auth.models import User
from client.models import Client
from products.models import Product


class Sale(models.Model):

    # Fecha y hora exacta de la venta
    date = models.DateTimeField(auto_now_add=True)
    # Cliente registrado (puede ser null si es venta rápida)
    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    # Cliente rapido en caso de no se un mayorista
    client_name = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    client_phone = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )
    # Vendedor (usuario del sistema)
    seller = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    # Descuento total aplicado a la venta
    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    # Métodos de pago
    PAYMENT_METHOD_CHOICES = (
        ("EFECTIVO", "Efectivo"),
        ("TARJETA", "Tarjeta"),
        ("TRANSFERENCIA", "Transferencia"),
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )
    # Cantidad pagada por el cliente
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    # Cambio devuelto al cliente
    change = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

#Calcular el total de la venta
    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    def __str__(self):
        return f"Venta #{self.id} - {self.date.date()}"

class SaleItem(models.Model):
    # Cada línea del ticket
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    @property
    def subtotal(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.quantity} x {self.product.name} en venta #{self.sale_id}"
