from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import InsumoViewSet, MovimientoInventarioViewSet


router = DefaultRouter()

router.register(
    'insumos',
    InsumoViewSet,
    basename='insumo'
)

router.register(
    'movimientos',
    MovimientoInventarioViewSet,
    basename='movimiento'
)


urlpatterns = [
    path('', include(router.urls)),
]