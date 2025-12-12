# suppliers/serializers.py
from rest_framework import serializers
from .models import Supplier


class SupplierSerializer(serializers.ModelSerializer):
    # name obligatorio
    name = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            "required": "El nombre es obligatorio.",
            "blank": "El nombre es obligatorio.",
        },
    )

    # code obligatorio
    code = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            "required": "El código es obligatorio.",
            "blank": "El código es obligatorio.",
        },
    )

    # phone obligatorio
    phone = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            "required": "El teléfono es obligatorio.",
            "blank": "El teléfono es obligatorio.",
        },
    )

    # email obligatorio + formato
    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        allow_null=False,
        error_messages={
            "required": "El correo electrónico es obligatorio.",
            "blank": "El correo electrónico es obligatorio.",
            "invalid": "Ingresa un correo válido.",
        },
    )

    class Meta:
        model = Supplier
        fields = ["id", "name", "code", "phone", "email", "notes"]

        # IMPORTANTE: quitamos los unique validators automáticos
        # para poder controlar mensajes y devolver varios errores a la vez
        extra_kwargs = {
            "code": {"validators": []},
            "phone": {"validators": []},
            "email": {"validators": []},
        }

    # -------- Validaciones por campo (formato / reglas) --------

    def validate_name(self, value):
        value = (value or "").strip()
        if len(value) < 3:
            raise serializers.ValidationError("El nombre debe tener al menos 3 caracteres.")
        return value

    def validate_code(self, value):
        return (value or "").strip()

    def validate_phone(self, value):
        v = (value or "").strip()
        if not v.isdigit():
            raise serializers.ValidationError("El teléfono solo debe contener dígitos.")
        if len(v) < 7:
            raise serializers.ValidationError("El teléfono debe tener al menos 7 dígitos.")
        return v

    def validate_email(self, value):
        return (value or "").strip()

    # -------- Validación cruzada (unicidad) --------
    def validate(self, attrs):
        code = attrs.get("code")
        phone = attrs.get("phone")
        email = attrs.get("email")

        instance = getattr(self, "instance", None)
        errors = {}

        # code único (case-insensitive)
        if code:
            qs = Supplier.objects.filter(code__iexact=code)
            if instance:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                errors["code"] = "Ya existe un proveedor con ese código."

        # phone único
        if phone:
            qs = Supplier.objects.filter(phone=phone)
            if instance:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                errors["phone"] = "Ya existe un proveedor con este número telefónico."

        # email único (case-insensitive)
        if email:
            qs = Supplier.objects.filter(email__iexact=email)
            if instance:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                errors["email"] = "Ya existe un proveedor con este correo electrónico."

        if errors:
            raise serializers.ValidationError(errors)

        return attrs
