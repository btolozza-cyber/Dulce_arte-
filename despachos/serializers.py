
from pathlib import Path

from django.utils import timezone
from rest_framework import serializers

from .models import Despacho
from pedidos.models import Pedido


class DespachoSerializer(serializers.ModelSerializer):

    pedido_cliente = serializers.CharField(
        source='pedido.cliente.nombre',
        read_only=True
    )

    class Meta:
        model = Despacho
        fields = '__all__'

        read_only_fields = (
            'id',
            'estado',
            'fecha_creacion',
            'fecha_entrega_real',
        )

    def validate_pedido(self, value):

        if value.estado != Pedido.Estado.LISTO:
            raise serializers.ValidationError(
                'Solo se pueden crear despachos para pedidos listos.'
            )

        if (
            self.instance is not None
            and self.instance.pedido_id != value.id
        ):
            raise serializers.ValidationError(
                'No se puede cambiar el pedido de un despacho existente.'
            )

        return value

    def validate_direccion_entrega(self, value):

        if not value.strip():
            raise serializers.ValidationError(
                'La dirección de entrega es obligatoria.'
            )

        return value.strip()

    def validate_fecha_programada(self, value):

        if value <= timezone.now():
            raise serializers.ValidationError(
                'La fecha programada debe ser futura.'
            )

        return value

    def validate_comprobante(self, archivo):

        if archivo is None:
            return archivo

        extensiones_permitidas = {
            '.pdf',
            '.png',
            '.jpg',
            '.jpeg',
        }

        extension = Path(archivo.name).suffix.lower()

        if extension not in extensiones_permitidas:
            raise serializers.ValidationError(
                'Solo se permiten archivos PDF, PNG o JPG.'
            )

        if archivo.size > 5 * 1024 * 1024:
            raise serializers.ValidationError(
                'El archivo no puede superar los 5 MB.'
            )

        return archivo

