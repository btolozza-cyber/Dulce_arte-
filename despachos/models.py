from django.db import models
from pedidos.models import Pedido


class Despacho(models.Model):

    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        EN_RUTA = 'en_ruta', 'En ruta'
        ENTREGADO = 'entregado', 'Entregado'
        INCIDENCIA = 'incidencia', 'Incidencia'

    pedido = models.OneToOneField(
        Pedido,
        on_delete=models.PROTECT,
        related_name='despacho'
    )

    direccion_entrega = models.TextField()

    fecha_programada = models.DateTimeField()

    receptor = models.CharField(
        max_length=150,
        blank=True
    )

    transportista = models.CharField(
        max_length=150,
        blank=True
    )

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE
    )

    fecha_entrega_real = models.DateTimeField(
        null=True,
        blank=True
    )

    comprobante = models.FileField(
        upload_to='comprobantes_despacho/',
        null=True,
        blank=True
    )

    observacion = models.TextField(blank=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Despacho del pedido #{self.pedido.id}"