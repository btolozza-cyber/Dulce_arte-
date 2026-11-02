"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib import admin
from django.urls import include, path

from django.conf import settings
from django.conf.urls.static import static

from pedidos.views import inicio, pagina_pedidos
from clientes.views import pagina_clientes
from productos.views import pagina_productos
from produccion.views import pagina_produccion
from inventario.views import pagina_inventario
from despachos.views import pagina_despachos

from administracion.views import login_usuario, logout_usuario


urlpatterns = [
    path('admin/', admin.site.urls),

    # APIs
    path('api/', include('pedidos.urls')),
    path('api/', include('clientes.urls')),
    path('api/', include('produccion.urls')),
    path('api/inventario/', include('inventario.urls')),
    path('api/', include('productos.urls')),
    path('api/', include('despachos.urls')),

    # Autenticación
    path('login/', login_usuario, name='login'),
    path('logout/', logout_usuario, name='logout'),

    # Módulos
    path('clientes/', pagina_clientes, name='pagina_clientes'),
    path('pedidos/', pagina_pedidos, name='pagina_pedidos'),
    path('productos/', pagina_productos, name='pagina_productos'),
    path('produccion/', pagina_produccion, name='pagina_produccion'),
    path('inventario/', pagina_inventario, name='pagina_inventario'),
    path('despachos/', pagina_despachos, name='pagina_despachos'),

    # Administración
    path('administracion/', include('administracion.urls')),

    # Inicio
    path('', inicio, name='inicio'),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )