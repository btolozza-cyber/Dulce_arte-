from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Cliente
from .serializers import ClienteSerializer

class ClienteViewSet(viewsets.ModelViewSet):

    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        'nombre',
        'telefono',
        'correo',
        'direccion',
    ]

    ordering_fields = [
        'nombre',
        'fecha_registro',
    ]

    ordering = ['nombre']

    def destroy(self, request, *args, **kwargs):

        cliente = self.get_object()

        if cliente.pedidos.exists():
            return Response(
                {
                    'error': 'No se puede eliminar este cliente porque tiene pedidos asociados.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().destroy(request, *args, **kwargs)


def pagina_clientes(request):
    return render(request, 'clientes.html')