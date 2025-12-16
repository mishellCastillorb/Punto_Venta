from django import forms
from .models import Category, Material, Product

BASE_INPUT = "border p-2 rounded w-full"


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": BASE_INPUT,
                "placeholder": "Ej. Anillos"
            }),
        }

    def clean_name(self):
        v = (self.cleaned_data.get("name") or "").strip()

        if not v:
            raise forms.ValidationError("El nombre es obligatorio.")
        if len(v) < 3:
            raise forms.ValidationError("Debe tener al menos 3 caracteres.")

        qs = Category.objects.filter(name__iexact=v)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("Ya existe una categoría con ese nombre.")

        return v


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ["name", "purity"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": BASE_INPUT,
                "placeholder": "Ej. Oro"
            }),
            "purity": forms.TextInput(attrs={
                "class": BASE_INPUT,
                "placeholder": "Ej. 14k, 925"
            }),
        }

    def clean(self):
        cleaned = super().clean()
        name = (cleaned.get("name") or "").strip()
        purity = (cleaned.get("purity") or "").strip()

        if not name or not purity:
            return cleaned

        qs = Material.objects.filter(name__iexact=name, purity__iexact=purity)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            self.add_error("purity", "Ya existe ese material con esa pureza.")
        return cleaned


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name", "category", "supplier", "material",
            "purchase_price", "sale_price", "weight",
            "stock", "image"
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": BASE_INPUT}),
            "category": forms.Select(attrs={"class": BASE_INPUT}),
            "supplier": forms.Select(attrs={"class": BASE_INPUT}),
            "material": forms.Select(attrs={"class": BASE_INPUT}),
            "purchase_price": forms.NumberInput(attrs={"class": BASE_INPUT}),
            "sale_price": forms.NumberInput(attrs={"class": BASE_INPUT}),
            "weight": forms.NumberInput(attrs={"class": BASE_INPUT}),
            "stock": forms.NumberInput(attrs={"class": BASE_INPUT}),
        }
