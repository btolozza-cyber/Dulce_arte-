
from django.db import transaction
from django.core.exceptions import ValidationError

from pedidos.models import Pedido
from inventario.models import Insumo, MovimientoInventario
from inventario.services import registrar_movimiento


@transaction.atomic
def consumir_insumos_pedido(pedido_id):

    pedido = Pedido.objects.select_for_update().get(
        pk=pedido_id
    )

    detalles = list(
        pedido.detalles.select_related(
            'producto'
        ).prefetch_related(
            'producto__recetas__insumo'
        )
    )

    if not detalles:
        raise ValidationError(
            'El pedido no contiene productos.'
        )

    consumo = {}

    # Calcular todos los ingredientes necesarios.
    for detalle in detalles:

        recetas = list(detalle.producto.recetas.all())

        if not recetas:
            raise ValidationError(
                f'El producto {detalle.producto.nombre} '
                'no tiene una receta registrada.'
            )

        for receta in recetas:

            insumo = receta.insumo

            cantidad_necesaria = (
                receta.cantidad * detalle.cantidad
            )

            if cantidad_necesaria <= 0:
                raise ValidationError(
                    f'La cantidad calculada para {insumo.nombre} '
                    'no es válida.'
                )

            if insumo.id not in consumo:
                consumo[insumo.id] = {
                    'insumo': insumo,
                    'cantidad': cantidad_necesaria
                }
            else:
                consumo[insumo.id]['cantidad'] += cantidad_necesaria

    # Bloquear los insumos en orden para reducir
    # el riesgo de bloqueos cruzados.
    insumos_bloqueados = Insumo.objects.select_for_update().filter(
        pk__in=sorted(consumo.keys())
    ).order_by('pk')

    insumos_por_id = {
        insumo.id: insumo
        for insumo in insumos_bloqueados
    }

    # Validar que todos los insumos existan y tengan stock.
    for insumo_id, item in consumo.items():

        insumo = insumos_por_id.get(insumo_id)

        if insumo is None:
            raise ValidationError(
                'Uno de los insumos de la receta ya no existe.'
            )

        if insumo.stock_actual < item['cantidad']:
            raise ValidationError(
                f'Stock insuficiente de {insumo.nombre}. '
                f'Disponible: {insumo.stock_actual}. '
                f'Necesario: {item["cantidad"]}.'
            )

    # Registrar los movimientos de salida.
    movimientos = []

    for insumo_id in sorted(consumo.keys()):

        item = consumo[insumo_id]

        movimiento = registrar_movimiento(
            insumo_id=insumo_id,
            tipo=MovimientoInventario.TipoMovimiento.SALIDA,
            cantidad=item['cantidad'],
            observacion=(
                f'Consumo por producción del pedido #{pedido.id}'
            )
        )

        movimientos.append(movimiento)

    return movimientos
