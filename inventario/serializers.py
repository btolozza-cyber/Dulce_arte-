
from rest_framework import serializers

from .models import Insumo, MovimientoInventario


class InsumoSerializer(serializers.ModelSerializer):

    stock_bajo = serializers.ReadOnlyField()

    class Meta:
        model = Insumo
        fields = '__all__'

        read_only_fields = (
            'id',
            'stock_actual',
            'fecha_creacion',
            'fecha_actualizacion',
        )

    def validate_nombre(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                'El nombre del insumo no puede estar vacío.'
            )

        return value


class MovimientoInventarioSerializer(serializers.ModelSerializer):

    insumo_nombre = serializers.CharField(
        source='insumo.nombre',
        read_only=True
    )

    class Meta:
        model = MovimientoInventario
        fields = '__all__'

        read_only_fields = (
            'id',
            'fecha_movimiento',
            'stock_anterior',
            'stock_nuevo',
        )

    def validate_cantidad(self, value):

        if not value.is_finite():
            raise serializers.ValidationError(
                'La cantidad debe ser un número válido.'
            )

        return value

    def validate(self, attrs):

        tipo = attrs.get('tipo')
        cantidad = attrs.get('cantidad')

        if tipo == MovimientoInventario.TipoMovimiento.AJUSTE:

            if cantidad < 0:
                raise serializers.ValidationError({
                    'cantidad': 'El stock final no puede ser negativo.'
                })

        elif cantidad <= 0:

            raise serializers.ValidationError({
                'cantidad': (
                    'La entrada o salida debe ser mayor que cero.'
                )
            })

        return attrs

    def update(self, instance, validated_data):

        raise serializers.ValidationError(
            'Los movimientos de inventario no se pueden modificar.'
        )
