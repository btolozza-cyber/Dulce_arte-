from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'nombre',
        'telefono',
        'correo',
        'fecha_registro',
    )

    search_fields = ('nombre', 'telefono', 'correo')

    ordering = ('nombre',)