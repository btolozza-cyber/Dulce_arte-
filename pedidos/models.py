
from django.db import models
from django.core.validators import MinValueValidator

from clientes.models import Cliente
from productos.models import Producto


class Pedido(models.Model):

    class Estado(models.TextChoices):
        RECIBIDO = 'recibido', 'Recibido'
        PREPARACION = 'preparacion', 'En Preparación'
        HORNEADO_DECORADO = 'horneado_decorado', 'Horneado/Decorado'
        CONTROL_CALIDAD = 'control_calidad', 'Control de Calidad'
        LISTO = 'listo', 'Listo'
        CANCELADO = 'cancelado', 'Cancelado'

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='pedidos'
    )

    telefono = models.CharField(max_length=20)
    descripcion = models.TextField()
    ingredientes = models.TextField()
    diseno = models.TextField()

    fecha_entrega = models.DateTimeField()

    estado = models.CharField(
        max_length=30,
        choices=Estado.choices,
        default=Estado.RECIBIDO
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha_entrega']

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.nombre}"

    @property
    def total(self):
        return sum(
            detalle.subtotal
            for detalle in self.detalles.all()
        )


class DetallePedido(models.Model):

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='detalles'
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='detalles_pedido'
    )

    cantidad = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'Detalle de pedido'
        verbose_name_plural = 'Detalles de pedidos'

        constraints = [
            models.UniqueConstraint(
                fields=['pedido', 'producto'],
                name='producto_unico_por_pedido'
            )
        ]

    def __str__(self):
        return (
            f"Pedido #{self.pedido.id} - "
            f"{self.producto.nombre} x {self.cantidad}"
        )

    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad
