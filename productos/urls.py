
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ProductoViewSet,
    RecetaViewSet,
)

router = DefaultRouter()

router.register(
    'productos',
    ProductoViewSet,
    basename='producto'
)

router.register(
    'recetas',
    RecetaViewSet,
    basename='receta'
)

urlpatterns = [
    path('', include(router.urls)),
]
