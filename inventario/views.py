
from django.shortcuts import get_object_or_404, render
from django.core.exceptions import ValidationError
from django.db.models import F
from django.db.models.deletion import ProtectedError

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Insumo, MovimientoInventario
from .serializers import (
    InsumoSerializer,
    MovimientoInventarioSerializer,
)
from .services import registrar_movimiento


def pagina_inventario(request):
    return render(request, 'inventario.html')


class InsumoViewSet(viewsets.ModelViewSet):

    queryset = Insumo.objects.all()

    serializer_class = InsumoSerializer

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
        'stock_actual',
        'stock_minimo',
        'fecha_creacion',
    ]

    ordering = ['nombre']

    def destroy(self, request, *args, **kwargs):

        insumo = self.get_object()

        try:
            insumo.delete()

        except ProtectedError:
            return Response(
                {
                    'error': (
                        'No se puede eliminar este insumo porque '
                        'está asociado a recetas o movimientos '
                        'de inventario.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                'mensaje': 'Insumo eliminado correctamente.'
            },
            status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='stock-bajo'
    )
    def stock_bajo(self, request):

        insumos = self.get_queryset().filter(
            stock_actual__lte=F('stock_minimo')
        )

        insumos = self.filter_queryset(insumos)

        serializer = self.get_serializer(
            insumos,
            many=True
        )

        return Response(serializer.data)


class MovimientoInventarioViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = MovimientoInventario.objects.select_related(
        'insumo'
    ).all()

    serializer_class = MovimientoInventarioSerializer

    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        'insumo',
        'tipo',
    ]

    search_fields = [
        'insumo__nombre',
        'observacion',
    ]

    ordering_fields = [
        'fecha_movimiento',
        'cantidad',
        'tipo',
    ]

    ordering = ['-fecha_movimiento']

    @action(
        detail=False,
        methods=['post'],
        url_path='registrar'
    )
    def registrar(self, request):

        serializer = MovimientoInventarioSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        try:
            movimiento = registrar_movimiento(
                insumo_id=serializer.validated_data['insumo'].id,
                tipo=serializer.validated_data['tipo'],
                cantidad=serializer.validated_data['cantidad'],
                observacion=serializer.validated_data.get(
                    'observacion',
                    ''
                )
            )

        except Insumo.DoesNotExist:
            return Response(
                {
                    'error': 'El insumo solicitado no existe.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        except ValidationError as error:
            return Response(
                {
                    'error': error.messages
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            MovimientoInventarioSerializer(movimiento).data,
            status=status.HTTP_201_CREATED
        )
