
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


ROLES = (
    ("usuario", "Usuario normal"),
    ("administrador", "Administrador"),
)


class CrearUsuarioForm(UserCreationForm):
    email = forms.EmailField(
        required=False,
        label="Correo electrónico"
    )

    first_name = forms.CharField(
        required=False,
        label="Nombre"
    )

    last_name = forms.CharField(
        required=False,
        label="Apellido"
    )

    rol = forms.ChoiceField(
        choices=ROLES,
        label="Privilegios",
        initial="usuario"
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

    def save(self, commit=True):
        usuario = super().save(commit=False)

        es_admin = self.cleaned_data["rol"] == "administrador"

        usuario.is_staff = es_admin
        usuario.is_superuser = False

        if commit:
            usuario.save()

        return usuario


class EditarUsuarioForm(forms.ModelForm):
    rol = forms.ChoiceField(
        choices=ROLES,
        label="Privilegios"
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
        )

        labels = {
            "username": "Nombre de usuario",
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo electrónico",
            "is_active": "Cuenta activa",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields["rol"].initial = (
                "administrador"
                if self.instance.is_staff or self.instance.is_superuser
                else "usuario"
            )

    def save(self, commit=True):
        usuario = super().save(commit=False)

        es_admin = self.cleaned_data["rol"] == "administrador"

        usuario.is_staff = es_admin

        if commit:
            usuario.save()

        return usuario
