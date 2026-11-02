
from django.shortcuts import render

from django.utils import timezone
from django.db import transaction

from rest_framework.parsers import (
    MultiPartParser,
    FormParser,
    JSONParser,
)

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from pedidos.models import Pedido

from .models import Despacho
from .serializers import DespachoSerializer


def pagina_despachos(request):
    return render(request, 'despachos.html')


class DespachoViewSet(viewsets.ModelViewSet):

    parser_classes = [
        MultiPartParser,
        FormParser,
        JSONParser,
    ]

    queryset = Despacho.objects.select_related(
        'pedido',
        'pedido__cliente'
    ).all()

    serializer_class = DespachoSerializer

    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = [
        'estado',
        'pedido',
    ]

    search_fields = [
        'pedido__cliente__nombre',
        'direccion_entrega',
        'transportista',
    ]

    ordering_fields = [
        'fecha_programada',
        'fecha_creacion',
    ]

    ordering = ['fecha_programada']

    def create(self, request, *args, **kwargs):

        with transaction.atomic():

            pedido_id = request.data.get('pedido')

            if not pedido_id:
                return Response(
                    {'error': 'Debes indicar el pedido.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                pedido = Pedido.objects.select_for_update().get(
                    pk=pedido_id
                )

            except (Pedido.DoesNotExist, ValueError, TypeError):
                return Response(
                    {'error': 'El pedido solicitado no existe.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            if pedido.estado != Pedido.Estado.LISTO:
                return Response(
                    {
                        'error': (
                            'Solo se pueden crear despachos '
                            'para pedidos que estén listos.'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            if Despacho.objects.filter(pedido=pedido).exists():
                return Response(
                    {
                        'error': 'Este pedido ya tiene un despacho asociado.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = self.get_serializer(
                data=request.data
            )

            serializer.is_valid(raise_exception=True)

            serializer.save(pedido=pedido)

            headers = self.get_success_headers(
                serializer.data
            )

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )

    @action(
        detail=True,
        methods=['patch'],
        url_path='cambiar-estado'
    )
    def cambiar_estado(self, request, pk=None):

        with transaction.atomic():

            despacho = self.get_object()

            despacho = Despacho.objects.select_for_update().select_related(
                'pedido',
                'pedido__cliente'
            ).get(pk=despacho.pk)

            nuevo_estado = request.data.get('estado')

            transiciones = {
                Despacho.Estado.PENDIENTE: [
                    Despacho.Estado.EN_RUTA
                ],
                Despacho.Estado.EN_RUTA: [
                    Despacho.Estado.ENTREGADO,
                    Despacho.Estado.INCIDENCIA,
                ],
                Despacho.Estado.INCIDENCIA: [
                    Despacho.Estado.EN_RUTA
                ],
                Despacho.Estado.ENTREGADO: [],
            }

            if nuevo_estado not in transiciones.get(
                despacho.estado,
                []
            ):
                return Response(
                    {
                        'error': 'Transición de estado no permitida.',
                        'estado_actual': despacho.estado,
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            if nuevo_estado == Despacho.Estado.ENTREGADO:

                receptor = request.data.get(
                    'receptor',
                    ''
                ).strip()

                if not receptor:
                    return Response(
                        {
                            'error': (
                                'Debes indicar quién recibió el pedido.'
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                despacho.receptor = receptor
                despacho.fecha_entrega_real = timezone.now()

            despacho.estado = nuevo_estado

            campos_actualizados = ['estado']

            if nuevo_estado == Despacho.Estado.ENTREGADO:
                campos_actualizados.extend([
                    'receptor',
                    'fecha_entrega_real',
                ])

            despacho.save(
                update_fields=campos_actualizados
            )

            return Response(
                DespachoSerializer(despacho).data,
                status=status.HTTP_200_OK
            )
