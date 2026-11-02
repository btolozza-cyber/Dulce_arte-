
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Insumo, MovimientoInventario


@transaction.atomic
def registrar_movimiento(insumo_id, tipo, cantidad, observacion=''):

    try:
        cantidad = Decimal(str(cantidad))
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError(
            'La cantidad ingresada no es válida.'
        )

    if not cantidad.is_finite():
        raise ValidationError(
            'La cantidad debe ser un número válido.'
        )

    if cantidad < 0:
        raise ValidationError(
            'La cantidad no puede ser negativa.'
        )

    insumo = Insumo.objects.select_for_update().get(
        pk=insumo_id
    )

    stock_anterior = insumo.stock_actual

    if tipo == MovimientoInventario.TipoMovimiento.ENTRADA:

        if cantidad <= 0:
            raise ValidationError(
                'La entrada debe ser mayor que cero.'
            )

        insumo.stock_actual += cantidad

    elif tipo == MovimientoInventario.TipoMovimiento.SALIDA:

        if cantidad <= 0:
            raise ValidationError(
                'La salida debe ser mayor que cero.'
            )

        if cantidad > stock_anterior:
            raise ValidationError(
                'No hay suficiente stock disponible.'
            )

        insumo.stock_actual -= cantidad

    elif tipo == MovimientoInventario.TipoMovimiento.AJUSTE:

        stock_nuevo = cantidad

        diferencia = stock_nuevo - stock_anterior

        if diferencia == 0:
            raise ValidationError(
                'El stock introducido es igual al stock actual. '
                'Nada que ajustar.'
            )

        cantidad = abs(diferencia)
        insumo.stock_actual = stock_nuevo

    else:
        raise ValidationError(
            'El tipo de movimiento no es válido.'
        )

    stock_nuevo = insumo.stock_actual

    insumo.save(
        update_fields=[
            'stock_actual',
            'fecha_actualizacion'
        ]
    )

    movimiento = MovimientoInventario.objects.create(
        insumo=insumo,
        tipo=tipo,
        cantidad=cantidad,
        stock_anterior=stock_anterior,
        stock_nuevo=stock_nuevo,
        observacion=observacion
    )

    return movimiento
