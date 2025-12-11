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

    # code obligatorio + único
    code = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            "required": "El código es obligatorio.",
            "blank": "El código es obligatorio.",
        },
    )

    # phone obligatorio + único
    phone = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            "required": "El teléfono es obligatorio.",
            "blank": "El teléfono es obligatorio.",
        },
    )

    # email obligatorio + único, con mensaje de formato
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
        extra_kwargs = {
            "code": {"validators": []},
        }

    # --- Validaciones por campo ---

    def validate_name(self, value):
        value = (value or "").strip()
        if len(value) < 3:
            raise serializers.ValidationError(
                "El nombre debe tener al menos 3 caracteres."
            )
        return value

    def validate_code(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("El código es obligatorio.")

        qs = Supplier.objects.filter(code__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError(
                "Ya existe un proveedor con ese código."
            )
        return value

    def validate_phone(self, value):
        v = (value or "").strip()
        if not v:
            raise serializers.ValidationError("El teléfono es obligatorio.")
        if not v.isdigit():
            raise serializers.ValidationError(
                "El teléfono solo debe contener dígitos."
            )
        if len(v) < 7:
            raise serializers.ValidationError(
                "El teléfono debe tener al menos 7 dígitos."
            )
        return v

    def validate_email(self, value):
        return (value or "").strip()

    # --- Validación cruzada para unicidad de teelfono y correo

    def validate(self, attrs):
        phone = attrs.get("phone")
        email = attrs.get("email")

        instance = getattr(self, "instance", None)

        # telefono único
        if phone:
            qs_phone = Supplier.objects.filter(phone=phone)
            if instance:
                qs_phone = qs_phone.exclude(pk=instance.pk)
            if qs_phone.exists():
                raise serializers.ValidationError({
                    "phone": "Ya existe un proveedor con este número telefónico."
                })

        # correo único
        if email:
            qs_email = Supplier.objects.filter(email__iexact=email)
            if instance:
                qs_email = qs_email.exclude(pk=instance.pk)
            if qs_email.exists():
                raise serializers.ValidationError({
                    "email": "Ya existe un proveedor con este correo electrónico."
                })

        return attrs
