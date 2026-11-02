
from django.shortcuts import render

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from .models import Producto, Receta
from .serializers import ProductoSerializer, RecetaSerializer


def pagina_productos(request):
    return render(request, 'productos.html')


class ProductoViewSet(viewsets.ModelViewSet):

    queryset = Producto.objects.prefetch_related(
        'recetas__insumo'
    ).all()

    serializer_class = ProductoSerializer

    permission_classes = [IsAuthenticated]

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        'nombre',
        'descripcion',
    ]

    ordering_fields = [
        'nombre',
        'precio_base',
        'fecha_creacion',
    ]

    ordering = ['nombre']


class RecetaViewSet(viewsets.ModelViewSet):

    queryset = Receta.objects.select_related(
        'producto',
        'insumo'
    ).all()

    serializer_class = RecetaSerializer

    permission_classes = [IsAuthenticated]

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        'producto__nombre',
        'insumo__nombre',
    ]

    ordering_fields = [
        'producto__nombre',
        'insumo__nombre',
        'cantidad',
    ]

    ordering = ['producto__nombre']
