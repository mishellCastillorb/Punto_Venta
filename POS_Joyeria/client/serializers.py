from rest_framework import serializers
from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"

    # Validar nombre
    def validate_name(self, value):
        v = (value or "").strip()
        if not v:
            raise serializers.ValidationError("El nombre es obligatorio.")
        if len(v) < 3:
            raise serializers.ValidationError(
                "El nombre debe tener al menos 3 caracteres."
            )
        return v

    # Validar telefono
    def validate_phone(self, value):
        if not value:
            return value
        v = value.strip()
        # Permite digitos, espacios y +
        v_simple = v.replace(" ", "").replace("+", "")
        if not v_simple.isdigit():
            raise serializers.ValidationError(
                "El teléfono solo debe contener dígitos (y opcionalmente + para ladas)."
                )
        return value

    # Validar email
    def validate_email(self, value):
        if not value:
            return value

        qs = Client.objects.filter(email__iexact=value)

        # Si se esta editando un cliente, se excluye
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError(
                "Ya existe un cliente con ese correo."
            )
        return value


