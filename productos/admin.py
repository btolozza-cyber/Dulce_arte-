from django.contrib import admin
from .models import Producto, Receta


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'nombre',
        'precio_base',
        'activo',
        'fecha_creacion',
    )

    list_filter = (
        'activo',
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


@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'producto',
        'insumo',
        'cantidad',
    )

    list_filter = (
        'producto',
        'insumo',
    )

    search_fields = (
        'producto__nombre',
        'insumo__nombre',
    )

    ordering = (
        'producto__nombre',
        'insumo__nombre',
    )