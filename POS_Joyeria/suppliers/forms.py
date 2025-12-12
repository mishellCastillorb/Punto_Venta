from django import forms
from .models import Supplier

BASE_INPUT = "border p-2 rounded w-full"
BASE_TEXTAREA = "border p-2 rounded w-full resize-y"

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ["name", "code", "phone", "email", "notes"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": BASE_INPUT, "placeholder": "Nombre", "id": "prov-name"
            }),
            "code": forms.TextInput(attrs={
                "class": BASE_INPUT, "placeholder": "Código", "id": "prov-code"
            }),
            "phone": forms.TextInput(attrs={
                "class": BASE_INPUT, "placeholder": "Teléfono", "id": "prov-phone",
                "inputmode": "numeric", "pattern": r"\d*",
            }),
            "email": forms.EmailInput(attrs={
                "class": BASE_INPUT, "placeholder": "Correo", "id": "prov-email"
            }),
            "notes": forms.Textarea(attrs={
                "class": BASE_TEXTAREA,
                "placeholder": "Notas",
                "rows": 4
            }),
        }
