from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.http import urlencode


class AutenticacionObligatoriaMiddleware:
    """
    Exige autenticación para acceder al sistema.

    Las páginas HTML redirigen al login.
    Las solicitudes API reciben una respuesta 401.
    """

    RUTAS_PUBLICAS = (
        "/login/",
        "/static/",
        "/media/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        ruta = request.path

        # Permitir las rutas públicas.
        if any(
            ruta.startswith(ruta_publica)
            for ruta_publica in self.RUTAS_PUBLICAS
        ):
            return self.get_response(request)

        # Permitir la pantalla de login del administrador de Django.
        if ruta == "/admin/login/":
            return self.get_response(request)

        # Comprobar autenticación.
        if not request.user.is_authenticated:

            # Las APIs no deben recibir una página HTML como respuesta.
            if ruta.startswith("/api/"):
                return JsonResponse(
                    {
                        "detail": "Autenticación requerida."
                    },
                    status=401
                )

            parametros = urlencode({
                "next": request.get_full_path()
            })

            return redirect(
                f"/login/?{parametros}"
            )

        return self.get_response(request)