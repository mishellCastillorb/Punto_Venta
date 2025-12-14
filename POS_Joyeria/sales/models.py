from decimal import Decimal
from django.conf import settings
from django.db import models


class Sale(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Abierta"
        PAID = "PAID", "Pagada"
        CANCELLED = "CANCELLED", "Cancelada"

    class PaymentMethod(models.TextChoices):
        CASH = "CASH", "Efectivo"
        CARD = "CARD", "Tarjeta"
        TRANSFER = "TRANSFER", "Transferencia"

    folio = models.CharField(max_length=32, unique=True, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.OPEN)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)

    # Cliente (registrado o rápido)
    client = models.ForeignKey("client.Client", null=True, blank=True, on_delete=models.PROTECT)
    quick_client_name = models.CharField(max_length=150, blank=True, default="")
    quick_client_phone = models.CharField(max_length=30, blank=True, default="")

    discount_pct = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    payment_method = models.CharField(max_length=12, choices=PaymentMethod.choices, default=PaymentMethod.CASH)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    change_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.folio or f"Venta #{self.pk}"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.PROTECT)

    product_name = models.CharField(max_length=200)  # snapshot
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    qty = models.PositiveIntegerField()
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} x{self.qty}"
