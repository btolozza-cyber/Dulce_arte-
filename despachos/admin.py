from django.contrib import admin
from .models import Despacho


@admin.register(Despacho)
class DespachoAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'pedido',
        'direccion_entrega',
        'fecha_programada',
        'transportista',
        'estado'
    )

    list_filter = ('estado', 'fecha_programada')
    search_fields = ('pedido__cliente__nombre', 'direccion_entrega')