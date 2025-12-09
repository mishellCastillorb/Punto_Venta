from django.db import models  # Hereda de model, representa una tabla en la bd

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Material(models.Model):
    name = models.CharField(max_length=30)
    purity = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=120)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Peso en gramos"
    )
    stock = models.PositiveIntegerField()  # solo valores >= 0
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.SET_NULL,
        null=True
    )
    material = models.ForeignKey(
        Material,
        on_delete=models.SET_NULL,
        null=True
    )
    image = models.ImageField(upload_to="products/", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name
