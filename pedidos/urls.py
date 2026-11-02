
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    PedidoViewSet,
    DetallePedidoViewSet,
)

router = DefaultRouter()

router.register(
    'pedidos',
    PedidoViewSet,
    basename='pedido'
)

router.register(
    'detalles-pedido',
    DetallePedidoViewSet,
    basename='detalle-pedido'
)

urlpatterns = [
    path('', include(router.urls)),
]
