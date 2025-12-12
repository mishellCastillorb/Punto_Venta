from rest_framework import serializers
from .models import Client
import re

RFC_REGEX = re.compile(r"^[A-ZÑ&0-9]{12,13}$", re.IGNORECASE)
class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"

    def validate_name(self, value):
        v = (value or "").strip()
        if not v:
            raise serializers.ValidationError("El nombre es obligatorio.")
        if len(v) < 3:
            raise serializers.ValidationError("El nombre debe tener al menos 3 caracteres.")
        return v

    def validate_apellido_paterno(self, value):
        if value in (None, ""):
            return value
        v = value.strip()
        if len(v) < 3:
            raise serializers.ValidationError("El apellido paterno debe tener al menos 3 caracteres.")
        return v

    def validate_apellido_materno(self, value):
        if value in (None, ""):
            return value
        v = value.strip()
        if len(v) < 3:
            raise serializers.ValidationError("El apellido materno debe tener al menos 3 caracteres.")
        return v

    def validate_phone(self, value):
        if not value:
            return value
        v = value.strip()
        if not v.isdigit():
            raise serializers.ValidationError("El teléfono solo debe contener dígitos.")
        if len(v) < 7:
            raise serializers.ValidationError("El teléfono debe tener al menos 7 dígitos.")
        return v

    def validate_rfc(self, value):
        if not value:
            return value
        v = value.strip().upper()

        if not RFC_REGEX.match(v):
            raise serializers.ValidationError(
                "RFC inválido. Debe tener 12 a 13 caracteres (letras y números)."
            )

        qs = Client.objects.filter(rfc__iexact=v)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya existe un cliente con este RFC.")

        return v

    def validate_email(self, value):
        # EmailField ya valida el formato; aquí solo cuidamos unicidad case-insensitive
        if not value:
            return value

        v = value.strip()
        qs = Client.objects.filter(email__iexact=v)

        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError("Ya existe un cliente con ese correo.")
        return v
