from django.contrib import admin
from .models import Pedido, DetallePedido


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'cliente',
        'fecha_entrega',
        'estado',
        'fecha_creacion',
    )

    list_filter = (
        'estado',
        'fecha_entrega',
        'fecha_creacion',
    )

    search_fields = (
        'cliente__nombre',
        'cliente__telefono',
        'descripcion',
    )

    ordering = ('fecha_entrega',)

    readonly_fields = ('fecha_creacion',)

    list_per_page = 20

@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'pedido',
        'producto',
        'cantidad',
        'precio_unitario',
        'mostrar_subtotal',
    )

    list_filter = (
        'producto',
    )

    search_fields = (
        'pedido__id',
        'producto__nombre',
    )

    readonly_fields = ('mostrar_subtotal',)

    def mostrar_subtotal(self, obj):
        return obj.subtotal

    mostrar_subtotal.short_description = 'Subtotal'