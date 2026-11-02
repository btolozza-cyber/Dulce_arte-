from django.contrib import admin
from .models import HistorialEstado


@admin.register(HistorialEstado)
class HistorialEstadoAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'pedido',
        'estado_anterior',
        'estado_nuevo',
        'fecha_cambio',
    )

    list_filter = (
        'estado_nuevo',
        'fecha_cambio',
    )

    search_fields = (
        'pedido__id',
        'observacion',
    )

    readonly_fields = ('fecha_cambio',)

    ordering = ('-fecha_cambio',)