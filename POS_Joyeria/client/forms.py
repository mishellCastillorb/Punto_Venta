from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import Client
import re

RFC_REGEX = re.compile(r"^[A-ZÑ&0-9]{12,13}$", re.IGNORECASE)

BASE = "border p-2 rounded w-full focus:outline-none focus:ring-2 focus:ring-amber-700/40"

class ClientForm(forms.ModelForm):
    email = forms.EmailField(
        required=False,
        error_messages={"invalid": "Ingresa un correo electrónico válido."},
        widget=forms.EmailInput(attrs={"placeholder": "Correo", "id": "c-correo"})
    )

    class Meta:
        model = Client
        fields = [
            "name",
            "apellido_paterno",
            "apellido_materno",
            "phone",
            "email",
            "rfc",
            "es_mayorista",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Nombre", "id": "c-nombre"}),
            "apellido_paterno": forms.TextInput(attrs={"placeholder": "Apellido paterno", "id": "c-apellido-paterno"}),
            "apellido_materno": forms.TextInput(attrs={"placeholder": "Apellido materno", "id": "c-apellido-materno"}),
            "phone": forms.TextInput(attrs={"placeholder": "Teléfono", "id": "c-telefono"}),
            "rfc": forms.TextInput(attrs={"placeholder": "RFC (12 a 13)", "id": "c-rfc"}),
        }
        error_messages = {
            "name": {"required": "El nombre es obligatorio."},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for fname in ["name", "apellido_paterno", "apellido_materno", "phone", "email", "rfc"]:
            self.fields[fname].widget.attrs["class"] = BASE

        self.fields["es_mayorista"].widget.attrs["class"] = "h-4 w-4 accent-amber-700"

    def clean_name(self):
        v = (self.cleaned_data.get("name") or "").strip()
        if not v:
            raise ValidationError("El nombre es obligatorio.")
        if len(v) < 3:
            raise ValidationError("El nombre debe tener al menos 3 caracteres.")
        return v

    def clean_apellido_paterno(self):
        v = self.cleaned_data.get("apellido_paterno")
        if not v:
            return v
        v = v.strip()
        if len(v) < 3:
            raise ValidationError("El apellido paterno debe tener al menos 3 caracteres.")
        return v

    def clean_apellido_materno(self):
        v = self.cleaned_data.get("apellido_materno")
        if not v:
            return v
        v = v.strip()
        if len(v) < 3:
            raise ValidationError("El apellido materno debe tener al menos 3 caracteres.")
        return v

    def clean_phone(self):
        v = self.cleaned_data.get("phone")
        if not v:
            return v
        v = v.strip()
        if not v.isdigit():
            raise ValidationError("El teléfono solo debe contener dígitos.")
        if len(v) < 7:
            raise ValidationError("El teléfono debe tener al menos 7 dígitos.")
        if len(v) > 15:
            raise ValidationError("El teléfono no debe exceder 15 dígitos.")

        qs = Client.objects.filter(phone=v)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Ya existe un cliente con ese teléfono.")
        return v

    def clean_rfc(self):
        rfc = self.cleaned_data.get("rfc")
        if not rfc:
            return rfc
        rfc = rfc.strip().upper()

        if not RFC_REGEX.match(rfc):
            raise ValidationError("El RFC debe tener 12 a 13 caracteres (letras y números).")

        qs = Client.objects.filter(rfc__iexact=rfc)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Ya existe un cliente registrado con este RFC.")
        return rfc

    def clean_email(self):
        v = self.cleaned_data.get("email")
        if not v:
            return v
        v = v.strip()

        try:
            validate_email(v)
        except ValidationError:
            raise ValidationError("Ingresa un correo electrónico válido.")

        qs = Client.objects.filter(email__iexact=v)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Ya existe un cliente con ese correo.")
        return v
