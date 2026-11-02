from django.apps import apps
from django.contrib import messages
from django.contrib.auth import (get_user_model, login, logout)
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import CrearUsuarioForm, EditarUsuarioForm


User = get_user_model()


def login_usuario(request):
    if request.user.is_authenticated:
        return redirect("inicio")

    siguiente = request.GET.get("next", "")

    if request.method == "POST":
        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)

            siguiente = request.POST.get("next", "")

            if (
                not siguiente
                or not url_has_allowed_host_and_scheme(
                    url=siguiente,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure()
                )
            ):
                siguiente = "/"

            return redirect(siguiente)

    else:
        form = AuthenticationForm(request)

    return render(
        request,
        "login.html",
        {
            "form": form,
            "next": siguiente,
        }
    )


@require_POST
def logout_usuario(request):
    logout(request)

    messages.success(
        request,
        "Has cerrado sesión correctamente."
    )

    return redirect("login")


def es_administrador(user):
    return (
        user.is_authenticated
        and user.is_active
        and (user.is_superuser or user.is_staff)
    )


requiere_administrador = user_passes_test(
    es_administrador,
    login_url="/login/"
)


def obtener_resumen():
    modelos_resumen = [
        ("clientes", "Cliente"),
        ("pedidos", "Pedido"),
        ("productos", "Producto"),
        ("inventario", "Insumo"),
        ("despachos", "Despacho"),
    ]

    resumen = {}

    for app_label, model_name in modelos_resumen:
        try:
            modelo = apps.get_model(app_label, model_name)
            resumen[model_name] = modelo.objects.count()
        except LookupError:
            resumen[model_name] = 0

    return resumen


@requiere_administrador
def pagina_administracion(request):

    crear_form = CrearUsuarioForm()
    editar_form = EditarUsuarioForm()

    modal_abierto = ""
    usuario_edicion_id = ""

    if request.method == "POST":

        accion = request.POST.get("accion")

        # CREAR USUARIO
        if accion == "crear":

            crear_form = CrearUsuarioForm(request.POST)

            if crear_form.is_valid():

                crear_form.save()

                messages.success(
                    request,
                    "Usuario creado correctamente."
                )

                return redirect("pagina_administracion")

            modal_abierto = "crear"

            messages.error(
                request,
                "No se pudo crear el usuario. Revisa los campos."
            )

        # EDITAR USUARIO
        elif accion == "editar":

            usuario_id = request.POST.get("usuario_id")

            usuario = get_object_or_404(
                User,
                id=usuario_id
            )

            usuario_edicion_id = usuario.id

            if usuario.is_superuser:

                messages.error(
                    request,
                    "No puedes modificar una cuenta de superusuario."
                )

                return redirect("pagina_administracion")

            editar_form = EditarUsuarioForm(
                request.POST,
                instance=usuario
            )

            if editar_form.is_valid():

                if usuario.id == request.user.id:

                    if not editar_form.cleaned_data["is_active"]:

                        editar_form.add_error(
                            "is_active",
                            "No puedes desactivar tu propia cuenta."
                        )

                    nuevo_rol = editar_form.cleaned_data["rol"]

                    if (
                        nuevo_rol == "usuario"
                        and usuario.is_staff
                    ):

                        editar_form.add_error(
                            "rol",
                            "No puedes quitarte tus propios privilegios."
                        )

                if editar_form.errors:

                    modal_abierto = "editar"

                    messages.error(
                        request,
                        "No se pudo actualizar el usuario. Revisa los campos."
                    )

                else:

                    editar_form.save()

                    messages.success(
                        request,
                        "Usuario actualizado correctamente."
                    )

                    return redirect("pagina_administracion")

            else:

                modal_abierto = "editar"

                messages.error(
                    request,
                    "No se pudo actualizar el usuario. Revisa los campos."
                )

        # CAMBIAR ESTADO
        elif accion == "estado":

            usuario_id = request.POST.get("usuario_id")

            usuario = get_object_or_404(
                User,
                id=usuario_id
            )

            if usuario.is_superuser:

                messages.error(
                    request,
                    "No puedes modificar una cuenta de superusuario."
                )

            elif usuario.id == request.user.id:

                messages.error(
                    request,
                    "No puedes desactivar tu propia cuenta."
                )

            else:

                usuario.is_active = not usuario.is_active

                usuario.save(
                    update_fields=["is_active"]
                )

                if usuario.is_active:
                    messages.success(
                        request,
                        "Usuario activado correctamente."
                    )
                else:
                    messages.success(
                        request,
                        "Usuario desactivado correctamente."
                    )

            return redirect("pagina_administracion")

        # ELIMINAR USUARIO
        elif accion == "eliminar":

            usuario_id = request.POST.get("usuario_id")

            usuario = get_object_or_404(
                User,
                id=usuario_id
            )

            if usuario.is_superuser:

                messages.error(
                    request,
                    "No puedes eliminar una cuenta de superusuario."
                )

            elif usuario.id == request.user.id:

                messages.error(
                    request,
                    "No puedes eliminar tu propia cuenta."
                )

            else:

                usuario.delete()

                messages.success(
                    request,
                    "Usuario eliminado correctamente."
                )

            return redirect("pagina_administracion")

        else:

            messages.error(
                request,
                "La operación solicitada no es válida."
            )

    contexto = {
        "total_usuarios": User.objects.count(),
        "usuarios_activos": User.objects.filter(
            is_active=True
        ).count(),
        "usuarios_inactivos": User.objects.filter(
            is_active=False
        ).count(),
        "resumen": obtener_resumen(),
        "usuarios": User.objects.all().order_by("-date_joined"),
        "crear_form": crear_form,
        "editar_form": editar_form,
        "modal_abierto": modal_abierto,
        "usuario_edicion_id": usuario_edicion_id,
    }

    return render(
        request,
        "administracion.html",
        contexto
    )


# Vistas anteriores conservadas por compatibilidad.

@requiere_administrador
def crear_usuario(request):

    if request.method == "POST":

        form = CrearUsuarioForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Usuario creado correctamente."
            )

            return redirect("pagina_administracion")

    else:

        form = CrearUsuarioForm()

    return render(
        request,
        "crear_usuario.html",
        {"form": form}
    )


@requiere_administrador
def editar_usuario(request, usuario_id):

    usuario = get_object_or_404(
        User,
        id=usuario_id
    )

    if usuario.is_superuser:

        messages.error(
            request,
            "No puedes modificar una cuenta de superusuario."
        )

        return redirect("pagina_administracion")

    if request.method == "POST":

        form = EditarUsuarioForm(
            request.POST,
            instance=usuario
        )

        if form.is_valid():

            if usuario.id == request.user.id:

                if not form.cleaned_data["is_active"]:

                    form.add_error(
                        "is_active",
                        "No puedes desactivar tu propia cuenta."
                    )

                if (
                    form.cleaned_data["rol"] == "usuario"
                    and usuario.is_staff
                ):

                    form.add_error(
                        "rol",
                        "No puedes quitarte tus propios privilegios."
                    )

            if not form.errors:

                form.save()

                messages.success(
                    request,
                    "Usuario actualizado correctamente."
                )

                return redirect("pagina_administracion")

    else:

        form = EditarUsuarioForm(
            instance=usuario
        )

    return render(
        request,
        "editar_usuario.html",
        {
            "form": form,
            "usuario": usuario,
        }
    )


@requiere_administrador
@require_POST
def cambiar_estado_usuario(request, usuario_id):

    usuario = get_object_or_404(
        User,
        id=usuario_id
    )

    if usuario.is_superuser or usuario.id == request.user.id:

        messages.error(
            request,
            "No puedes modificar el estado de esta cuenta."
        )

        return redirect("pagina_administracion")

    usuario.is_active = not usuario.is_active

    usuario.save(
        update_fields=["is_active"]
    )

    messages.success(
        request,
        "Estado del usuario actualizado correctamente."
    )

    return redirect("pagina_administracion")


@requiere_administrador
@require_POST
def eliminar_usuario(request, usuario_id):

    usuario = get_object_or_404(
        User,
        id=usuario_id
    )

    if usuario.is_superuser or usuario.id == request.user.id:

        messages.error(
            request,
            "No puedes eliminar esta cuenta."
        )

        return redirect("pagina_administracion")

    usuario.delete()

    messages.success(
        request,
        "Usuario eliminado correctamente."
    )

    return redirect("pagina_administracion")
