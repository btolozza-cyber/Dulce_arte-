from django.db import models
from pedidos.models import Pedido

class HistorialEstado(models.Model):

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='historial'
    )

    estado_anterior = models.CharField(
        max_length=30,
        blank=True
    )

    estado_nuevo = models.CharField(
        max_length=30,
        choices=Pedido.Estado.choices
    )

    fecha_cambio = models.DateTimeField(
        auto_now_add=True
    )

    observacion = models.TextField(
        blank=True
    )

    class Meta:
        ordering = ['fecha_cambio']
        verbose_name = 'Historial de estado'
        verbose_name_plural = 'Historial de estados'

    def __str__(self):
        return (
            f"Pedido #{self.pedido.id}: "
            f"{self.estado_anterior or 'Sin estado'} "
            f"→ {self.estado_nuevo}"
        )