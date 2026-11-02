from django.contrib import admin
from .models import Insumo, MovimientoInventario

#Detalles insumos
@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'nombre',
        'unidad_medida',
        'stock_actual',
        'stock_minimo',
        'fecha_actualizacion',
    )

    list_filter = (
        'unidad_medida',
        'fecha_creacion',
    )

    search_fields = (
        'nombre',
        'descripcion',
    )

    ordering = ('nombre',)

    readonly_fields = (
        'fecha_creacion',
        'fecha_actualizacion',
    )

    list_per_page = 20


#Historial y seguimiento 
@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'insumo',
        'tipo',
        'cantidad',
        'fecha_movimiento',
    )

    list_filter = (
        'tipo',
        'fecha_movimiento',
    )

    search_fields = (
        'insumo__nombre',
        'observacion',
    )

    readonly_fields = ('fecha_movimiento',)

    ordering = ('-fecha_movimiento',)

    list_per_page = 20

def has_add_permission(self, request):
    return False

def has_change_permission(self, request, obj=None):
    return False

def has_delete_permission(self, request, obj=None):
    return False