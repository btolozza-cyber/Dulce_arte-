from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from pedidos.models import Pedido
from .models import HistorialEstado


@receiver(pre_save, sender=Pedido)
def obtener_estado_anterior(sender, instance, **kwargs):

    if instance.pk:

        try:
            pedido_anterior = Pedido.objects.get(pk=instance.pk)
            instance._estado_anterior = pedido_anterior.estado

        except Pedido.DoesNotExist:
            instance._estado_anterior = None

    else:
        instance._estado_anterior = None


@receiver(post_save, sender=Pedido)
def registrar_historial_estado(sender, instance, created, **kwargs):

    estado_anterior = getattr(
        instance,
        '_estado_anterior',
        None
    )

    if created:

        HistorialEstado.objects.create(
            pedido=instance,
            estado_anterior='',
            estado_nuevo=instance.estado,
            observacion='Registro inicial del pedido.'
        )

    elif estado_anterior != instance.estado:

        HistorialEstado.objects.create(
            pedido=instance,
            estado_anterior=estado_anterior,
            estado_nuevo=instance.estado
        )