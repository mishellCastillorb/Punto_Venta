from django import forms
from django.contrib.auth.models import User, Group
from .models import StaffProfile

BASE_INPUT = "border p-2 rounded w-full"


def allowed_role_choices_for(request_user):
    """
    - SuperAdmin (superuser): puede crear/editar AdminPOS y VendedorPOS
    - AdminPOS normal: SOLO puede crear/editar VendedorPOS
    """
    if request_user and request_user.is_superuser:
        return (("AdminPOS", "AdminPOS"), ("VendedorPOS", "VendedorPOS"))
    return (("VendedorPOS", "VendedorPOS"),)


class StaffCreateForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": BASE_INPUT, "id": "st-username"})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": BASE_INPUT, "id": "st-password1"})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": BASE_INPUT, "id": "st-password2"})
    )

    nombre = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"class": BASE_INPUT, "id": "st-nombre"})
    )
    apellido_paterno = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"class": BASE_INPUT, "id": "st-ap"})
    )
    apellido_materno = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"class": BASE_INPUT, "id": "st-am"})
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": BASE_INPUT, "id": "st-email"})
    )
    telefono = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={"class": BASE_INPUT, "id": "st-telefono"})
    )
    direccion = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={"class": BASE_INPUT, "id": "st-direccion"})
    )

    rol = forms.ChoiceField(
        choices=(("VendedorPOS", "VendedorPOS"),),
        widget=forms.Select(attrs={"class": BASE_INPUT, "id": "st-rol"})
    )

    def __init__(self, *args, request_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_user = request_user
        self.fields["rol"].choices = allowed_role_choices_for(request_user)

    def clean_username(self):
        v = (self.cleaned_data.get("username") or "").strip()
        if not v:
            raise forms.ValidationError("El usuario es obligatorio.")
        if len(v) < 3:
            raise forms.ValidationError("El usuario debe tener al menos 3 caracteres.")
        if User.objects.filter(username__iexact=v).exists():
            raise forms.ValidationError("Ese usuario ya existe.")
        return v

    def clean_email(self):
        v = (self.cleaned_data.get("email") or "").strip().lower()
        if not v:
            raise forms.ValidationError("El correo es obligatorio.")
        if User.objects.filter(email__iexact=v).exists():
            raise forms.ValidationError("Ese correo ya está registrado.")
        return v

    def clean_telefono(self):
        v = (self.cleaned_data.get("telefono") or "").strip()
        if not v:
            raise forms.ValidationError("El teléfono es obligatorio.")
        if not v.isdigit():
            raise forms.ValidationError("El teléfono solo debe contener dígitos.")
        if len(v) < 7:
            raise forms.ValidationError("El teléfono debe tener al menos 7 dígitos.")
        if len(v) > 15:
            raise forms.ValidationError("El teléfono no debe exceder 15 dígitos.")
        if StaffProfile.objects.filter(telefono=v).exists():
            raise forms.ValidationError("Ese teléfono ya está registrado.")
        return v

    def clean_rol(self):
        rol = self.cleaned_data.get("rol")
        allowed = [r[0] for r in allowed_role_choices_for(self.request_user)]
        if rol not in allowed:
            raise forms.ValidationError("No tienes permiso para asignar ese rol.")
        return rol

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and len(p1) < 6:
            self.add_error("password1", "La contraseña debe tener al menos 6 caracteres.")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Las contraseñas no coinciden.")
        return cleaned

    def save(self):
        cd = self.cleaned_data

        u = User.objects.create_user(
            username=cd["username"],
            email=cd["email"],
            password=cd["password1"],
        )
        u.is_staff = True
        u.is_active = True
        u.save()

        group, _ = Group.objects.get_or_create(name=cd["rol"])
        u.groups.add(group)

        StaffProfile.objects.create(
            user=u,
            nombre=cd["nombre"],
            apellido_paterno=cd["apellido_paterno"],
            apellido_materno=cd["apellido_materno"],
            telefono=cd["telefono"],
            direccion=cd["direccion"],
        )
        return u


class StaffEditForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": BASE_INPUT, "id": "st-email"})
    )
    rol = forms.ChoiceField(
        choices=(("VendedorPOS", "VendedorPOS"),),
        widget=forms.Select(attrs={"class": BASE_INPUT, "id": "st-rol"})
    )

    class Meta:
        model = StaffProfile
        fields = ["nombre", "apellido_paterno", "apellido_materno", "telefono", "direccion"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": BASE_INPUT, "id": "st-nombre"}),
            "apellido_paterno": forms.TextInput(attrs={"class": BASE_INPUT, "id": "st-ap"}),
            "apellido_materno": forms.TextInput(attrs={"class": BASE_INPUT, "id": "st-am"}),
            "telefono": forms.TextInput(attrs={"class": BASE_INPUT, "id": "st-telefono"}),
            "direccion": forms.TextInput(attrs={"class": BASE_INPUT, "id": "st-direccion"}),
        }

    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop("user_instance", None)
        self.request_user = kwargs.pop("request_user", None)
        super().__init__(*args, **kwargs)

        self.fields["rol"].choices = allowed_role_choices_for(self.request_user)

        if self.user_instance:
            self.fields["email"].initial = self.user_instance.email
            current = self.user_instance.groups.values_list("name", flat=True).first()
            if current:
                self.fields["rol"].initial = current

    def clean_email(self):
        v = (self.cleaned_data.get("email") or "").strip().lower()
        if not v:
            raise forms.ValidationError("El correo es obligatorio.")
        if User.objects.filter(email__iexact=v).exclude(pk=self.user_instance.pk).exists():
            raise forms.ValidationError("Ese correo ya está registrado.")
        return v

    def clean_telefono(self):
        v = (self.cleaned_data.get("telefono") or "").strip()
        if not v:
            raise forms.ValidationError("El teléfono es obligatorio.")
        if not v.isdigit():
            raise forms.ValidationError("El teléfono solo debe contener dígitos.")
        if len(v) < 7:
            raise forms.ValidationError("El teléfono debe tener al menos 7 dígitos.")
        if len(v) > 15:
            raise forms.ValidationError("El teléfono no debe exceder 15 dígitos.")
        if StaffProfile.objects.filter(telefono=v).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ese teléfono ya está registrado.")
        return v

    def clean_rol(self):
        rol = self.cleaned_data.get("rol")
        allowed = [r[0] for r in allowed_role_choices_for(self.request_user)]
        if rol not in allowed:
            raise forms.ValidationError("No tienes permiso para asignar ese rol.")
        return rol

    def save(self, commit=True):
        profile = super().save(commit=commit)

        u = self.user_instance
        u.email = self.cleaned_data["email"]
        u.save(update_fields=["email"])

        u.groups.clear()
        group, _ = Group.objects.get_or_create(name=self.cleaned_data["rol"])
        u.groups.add(group)

        return profile
