
from django.urls import path

from . import views


urlpatterns = [
    path(
        "login/",
        views.login_usuario,
        name="login"
    ),

    path(
        "logout/",
        views.logout_usuario,
        name="logout"
    ),

    path(
        "",
        views.pagina_administracion,
        name="pagina_administracion"
    ),

    path(
        "usuarios/crear/",
        views.crear_usuario,
        name="crear_usuario"
    ),

    path(
        "usuarios/<int:usuario_id>/editar/",
        views.editar_usuario,
        name="editar_usuario"
    ),

    path(
        "usuarios/<int:usuario_id>/estado/",
        views.cambiar_estado_usuario,
        name="cambiar_estado_usuario"
    ),

    path(
        "usuarios/<int:usuario_id>/eliminar/",
        views.eliminar_usuario,
        name="eliminar_usuario"
    ),
]
