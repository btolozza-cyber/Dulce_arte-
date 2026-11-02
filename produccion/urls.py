
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    HistorialEstadoViewSet,
    TableroProduccionView,
    cambiar_estado_pedido,
)

router = DefaultRouter()

router.register(
    'historial',
    HistorialEstadoViewSet,
    basename='historial'
)

urlpatterns = [
    path('', include(router.urls)),

    path(
        'produccion/tablero/',
        TableroProduccionView.as_view(),
        name='tablero-produccion'
    ),

    path(
        'produccion/pedidos/<int:pedido_id>/estado/',
        cambiar_estado_pedido,
        name='cambiar-estado-pedido'
    ),
]
