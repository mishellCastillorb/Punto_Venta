from django.db import models

#categorias diponibles para los productos (anillos, pulseras,etc)
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

#materiales de los cuales estan echos los productos
class Material(models.Model):
    name = models.CharField(max_length=30)
    purity = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=120)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True
    )
    # Código generado automáticamente- proveedor + 3 letras de categoría + número consecutivo por categoría
    code = models.CharField(
        max_length=40,
        unique=True,
        editable=False
    )
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Peso en gramos"
    )
    stock = models.PositiveIntegerField()
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
    image = models.ImageField(
        upload_to="products/",
        null=True,
        blank=True
    )
    is_active = models.BooleanField(default=True)

    # Funcion para la generacion automatica del codigo
    def generate_code(self):

        # Regla: proveedor + 3 letras de categoría + consecutivo dentro de la categoría.

        if not self.supplier or not self.supplier.code:
            return None

        if not self.category or not self.category.name:
            return None

        supplier_code = self.supplier.code
        category_prefix = self.category.name[:3].upper()

        # Buscar cuántos productos existen en esta categoría
        existing = Product.objects.filter(category=self.category).count() + 1

        # Formatear como 3 dígitos
        return f"{supplier_code}{category_prefix}{existing:03d}"

    def save(self, *args, **kwargs):
        # Generar código solo si no existe todavía
        if not self.code:
            self.code = self.generate_code()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
