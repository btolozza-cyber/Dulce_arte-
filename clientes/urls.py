from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ClienteViewSet, pagina_clientes


router = DefaultRouter()
router.register('clientes', ClienteViewSet, basename='cliente')


urlpatterns = [
    path('', pagina_clientes, name='pagina_clientes'),
    *router.urls,
]