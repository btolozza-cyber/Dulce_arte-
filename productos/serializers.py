from rest_framework import serializers

from .models import Producto, Receta


class RecetaSerializer(serializers.ModelSerializer):

    insumo_nombre = serializers.CharField(
        source='insumo.nombre',
        read_only=True
    )

    unidad_medida = serializers.CharField(
        source='insumo.unidad_medida',
        read_only=True
    )

    class Meta:
        model = Receta
        fields = '__all__'


class ProductoSerializer(serializers.ModelSerializer):

    recetas = RecetaSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Producto
        fields = '__all__'

        read_only_fields = (
            'id',
            'fecha_creacion',
            'fecha_actualizacion',
        )