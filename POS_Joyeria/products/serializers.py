from rest_framework import serializers
from .models import Category, Material, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ("code",)

        extra_kwargs = {
            # Obligar a que siempre haya estos campos
            "category": {"required": True, "allow_null": False},
            "supplier": {"required": True, "allow_null": False},
            "material": {"required": True, "allow_null": False},
            "purchase_price": {"required": True},
            "sale_price": {"required": True},
            "stock": {"required": True},
            "weight": {"required": True},
            # Para alta, image la vamos a validar aparte
            "image": {"required": False},
        }

    def validate_stock(self, value):
        if value is None:
            raise serializers.ValidationError("El stock es obligatorio.")
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser negativo.")
        return value

    def validate_purchase_price(self, value):
        if value is None:
            raise serializers.ValidationError("El precio de compra es obligatorio.")
        if value < 0:
            raise serializers.ValidationError("El precio de compra no puede ser negativo.")
        return value

    def validate_sale_price(self, value):
        if value is None:
            raise serializers.ValidationError("El precio de venta es obligatorio.")
        if value < 0:
            raise serializers.ValidationError("El precio de venta no puede ser negativo.")
        return value

    def validate_weight(self, value):
        if value is None:
            raise serializers.ValidationError("El peso es obligatorio.")
        if value < 0:
            raise serializers.ValidationError("El peso no puede ser negativo.")
        return value

    def validate(self, attrs):
        """
        Validaciones a nivel de objeto:
        - Debe tener categoría, proveedor, material.
        - Debe tener imagen al dar de alta (POST).
        """
        creando = self.instance is None

        category = attrs.get("category") or (self.instance.category if self.instance else None)
        supplier = attrs.get("supplier") or (self.instance.supplier if self.instance else None)
        material = attrs.get("material") or (self.instance.material if self.instance else None)

        if category is None:
            raise serializers.ValidationError({"category": "Debe tener una categoría asignada."})

        if supplier is None:
            raise serializers.ValidationError({"supplier": "Debe tener un proveedor asignado."})

        if material is None:
            raise serializers.ValidationError({"material": "Debe tener un material asignado."})

        # Validar imagen solo al crear
        if creando:
            image = attrs.get("image")
            if not image:
                raise serializers.ValidationError(
                    {"image": "Debe subir una imagen para dar de alta el producto."}
                )

        return attrs
