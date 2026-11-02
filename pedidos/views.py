from django.shortcuts import render
from django.db import transaction

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from .models import Pedido, DetallePedido
from .serializers import (
    PedidoSerializer,
    DetallePedidoSerializer,
)


def inicio(request):
    return render(request, 'index.html')


def pagina_pedidos(request):
    return render(request, 'pedidos.html')


class PedidoViewSet(viewsets.ModelViewSet):

    queryset = Pedido.objects.select_related(
        'cliente'
    ).prefetch_related(
        'detalles__producto'
    ).all()

    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        'cliente__nombre',
        'cliente__telefono',
        'descripcion',
        'ingredientes',
    ]

    ordering_fields = [
        'fecha_entrega',
        'fecha_creacion',
        'estado',
    ]

    filterset_fields = [
        'estado',
        'cliente',
        'fecha_entrega',
    ]

    ordering = ['fecha_entrega']

    def destroy(self, request, *args, **kwargs):

        with transaction.atomic():

            pedido = Pedido.objects.select_for_update().filter(
                pk=kwargs['pk']
            ).first()

            if pedido is None:
                return Response(
                    {'error': 'El pedido no existe.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            if pedido.estado != Pedido.Estado.RECIBIDO:
                return Response(
                    {
                        'error': (
                            'Solo se pueden eliminar pedidos '
                            'que todavía estén en estado recibido.'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            tiene_despacho = Pedido.objects.filter(
                pk=pedido.pk,
                despacho__isnull=False
            ).exists()

            if tiene_despacho:
                return Response(
                    {
                        'error': (
                            'No se puede eliminar este pedido porque '
                            'tiene un despacho asociado.'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            pedido.delete()

        return Response(
            {'mensaje': 'Pedido eliminado correctamente.'},
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=['post'],
        url_path='cancelar'
    )
    def cancelar(self, request, pk=None):

        with transaction.atomic():

            pedido = Pedido.objects.select_for_update().filter(
                pk=pk
            ).first()

            if pedido is None:
                return Response(
                    {'error': 'El pedido no existe.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            estados_cancelables = [
                Pedido.Estado.PREPARACION,
                Pedido.Estado.HORNEADO_DECORADO,
                Pedido.Estado.CONTROL_CALIDAD,
            ]

            if pedido.estado not in estados_cancelables:
                return Response(
                    {
                        'error': (
                            'Solo se pueden cancelar pedidos '
                            'que hayan comenzado su producción '
                            'y que todavía no estén listos.'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            pedido.estado = Pedido.Estado.CANCELADO
            pedido.save(update_fields=['estado'])

        return Response(
            {
                'mensaje': 'Pedido cancelado correctamente.',
                'pedido': PedidoSerializer(pedido).data
            },
            status=status.HTTP_200_OK
        )


class DetallePedidoViewSet(viewsets.ModelViewSet):

    queryset = DetallePedido.objects.select_related(
        'pedido',
        'producto'
    ).all()

    serializer_class = DetallePedidoSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        'pedido',
        'producto',
    ]

    search_fields = [
        'producto__nombre',
        'pedido__id',
    ]

    ordering_fields = [
        'cantidad',
        'precio_unitario',
    ]

    ordering = ['pedido']
