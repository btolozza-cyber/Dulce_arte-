from rest_framework import serializers

from .models import Cliente


class ClienteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cliente
        fields = '__all__'
        read_only_fields = ('id', 'fecha_registro')

    def validate_nombre(self, value):

        if not value.strip():
            raise serializers.ValidationError(
                'El nombre del cliente no puede estar vacío.'
            )

        return value.strip()

    def validate_telefono(self, value):

        telefono = value.strip()

        if not telefono:
            raise serializers.ValidationError(
                'El teléfono del cliente es obligatorio.'
            )

        if not telefono.replace('+', '').replace(' ', '').isdigit():
            raise serializers.ValidationError(
                'Uso de caracteres no permitidos.'
            )

        return telefono

    def validate_correo(self, value):

        return value.strip().lower()