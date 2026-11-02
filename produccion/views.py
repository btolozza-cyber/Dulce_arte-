
from django.shortcuts import get_object_or_404, render
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.core.exceptions import ValidationError

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, filters, status
from rest_framework.views import APIView

from pedidos.models import Pedido
from pedidos.serializers import PedidoSerializer

from .models import HistorialEstado
from .serializers import HistorialEstadoSerializer
from .services import consumir_insumos_pedido


def pagina_produccion(request):
    return render(request, 'produccion.html')


class HistorialEstadoViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = HistorialEstado.objects.select_related(
        'pedido'
    ).all()

    serializer_class = HistorialEstadoSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        'pedido',
        'estado_anterior',
        'estado_nuevo',
    ]

    search_fields = [
        'pedido__id',
        'estado_anterior',
        'estado_nuevo',
        'observacion',
    ]

    ordering_fields = [
        'fecha_cambio',
        'estado_nuevo',
    ]

    ordering = ['-fecha_cambio']


class TableroProduccionView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        pedidos = Pedido.objects.select_related(
            'cliente'
        ).order_by('fecha_entrega')

        tablero = {}

        for estado, etiqueta in Pedido.Estado.choices:

            pedidos_estado = pedidos.filter(
                estado=estado
            )

            tablero[estado] = {
                'nombre': etiqueta,
                'pedidos': PedidoSerializer(
                    pedidos_estado,
                    many=True
                ).data
            }

        return Response(tablero)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def cambiar_estado_pedido(request, pedido_id):

    pedido = get_object_or_404(
        Pedido.objects.select_for_update(),
        pk=pedido_id
    )

    nuevo_estado = request.data.get('estado')

    transiciones_permitidas = {
        'recibido': 'preparacion',
        'preparacion': 'horneado_decorado',
        'horneado_decorado': 'control_calidad',
        'control_calidad': 'listo',
    }

    estado_actual = pedido.estado

    estado_siguiente = transiciones_permitidas.get(
        estado_actual
    )

    if nuevo_estado != estado_siguiente:
        return Response(
            {
                'error': 'Transición de estado no permitida.',
                'estado_actual': estado_actual,
                'estado_siguiente_permitido': estado_siguiente,
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Consumir ingredientes al iniciar la producción.
    if estado_actual == 'recibido' and nuevo_estado == 'preparacion':

        try:
            consumir_insumos_pedido(pedido.id)

        except ValidationError as error:
            return Response(
                {
                    'error': error.messages,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    pedido.estado = nuevo_estado
    pedido.save(update_fields=['estado'])

    return Response(
        {
            'mensaje': 'Estado del pedido actualizado correctamente.',
            'pedido': PedidoSerializer(pedido).data,
        },
        status=status.HTTP_200_OK
    )
