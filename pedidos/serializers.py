from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from .models import Pedido, DetallePedido
from productos.models import Producto


class DetallePedidoSerializer(serializers.ModelSerializer):

    producto_nombre = serializers.CharField(
        source='producto.nombre',
        read_only=True
    )

    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = DetallePedido
        fields = '__all__'
        read_only_fields = ('id',)

    def validate_cantidad(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'La cantidad debe ser al menos una unidad.'
            )
        return value

    def validate_precio_unitario(self, value):
        if value < 0:
            raise serializers.ValidationError(
                'El precio unitario no puede ser negativo.'
            )
        return value


class DetallePedidoEntradaSerializer(serializers.ModelSerializer):
    """
    Serializer utilizado al crear o modificar los detalles
    desde el formulario de pedidos.
    """

    producto = serializers.PrimaryKeyRelatedField(
        queryset=Producto.objects.filter(activo=True)
    )

    producto_nombre = serializers.CharField(
        source='producto.nombre',
        read_only=True
    )

    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = DetallePedido
        fields = (
            'id',
            'producto',
            'producto_nombre',
            'cantidad',
            'precio_unitario',
            'subtotal',
        )

        read_only_fields = (
            'id',
            'precio_unitario',
            'subtotal',
        )

    def validate_cantidad(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'La cantidad debe ser al menos una unidad.'
            )
        return value


class PedidoSerializer(serializers.ModelSerializer):

    cliente_nombre = serializers.CharField(
        source='cliente.nombre',
        read_only=True
    )

    total = serializers.ReadOnlyField()

    detalles = DetallePedidoEntradaSerializer(
        many=True,
        required=False
    )

    class Meta:
        model = Pedido
        fields = '__all__'

        read_only_fields = (
            'id',
            'fecha_creacion',
        )

    def validate_fecha_entrega(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError(
                'La fecha de entrega debe ser futura.'
            )
        return value

    def validate_descripcion(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                'La descripción del pedido no puede estar vacía.'
            )
        return value

    def validate_ingredientes(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                'Debes especificar los ingredientes del pedido.'
            )
        return value

    def validate_detalles(self, value):

        productos = [
            detalle['producto'].id
            for detalle in value
        ]

        if len(productos) != len(set(productos)):
            raise serializers.ValidationError(
                'No puedes agregar el mismo producto dos veces. '
                'Modifica su cantidad en un solo detalle.'
            )

        return value

    @transaction.atomic
    def create(self, validated_data):

        detalles_data = validated_data.pop('detalles', [])

        pedido = Pedido.objects.create(**validated_data)

        for detalle_data in detalles_data:

            producto = detalle_data['producto']
            cantidad = detalle_data['cantidad']

            DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio_base
            )

        return pedido

    @transaction.atomic
    def update(self, instance, validated_data):

        detalles_data = validated_data.pop(
            'detalles',
            None
        )

        for atributo, valor in validated_data.items():
            setattr(instance, atributo, valor)

        instance.save()

        # Solo reemplazar los detalles cuando se envían
        # explícitamente en la solicitud.
        if detalles_data is not None:

            instance.detalles.all().delete()

            for detalle_data in detalles_data:

                producto = detalle_data['producto']
                cantidad = detalle_data['cantidad']

                DetallePedido.objects.create(
                    pedido=instance,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio_base
                )

        return instance
