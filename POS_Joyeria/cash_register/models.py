from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class CashRegister(models.Model):
    #Quien abre caja y quien cierra
    opened_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="cash_opened"
    )

    closed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="cash_closed"
    )

    #Con cuanto se abre la caja
    opening_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    cash_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    card_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    transfer_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    total_sales = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    closing_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    #Si es 0,
    difference = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    is_closed = models.BooleanField(default=False)

    def __str__(self):
        estado = "CERRADA" if self.is_closed else "ABIERTA"
        return f"Caja #{self.id} - {estado}"
