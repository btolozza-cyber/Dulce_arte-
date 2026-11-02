from rest_framework import serializers
from .models import HistorialEstado


class HistorialEstadoSerializer(serializers.ModelSerializer):

    class Meta:
        model = HistorialEstado
        fields = '__all__'
        read_only_fields = ('id', 'fecha_cambio')