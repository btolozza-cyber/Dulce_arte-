from django.db import models
from django.core.validators import MinValueValidator

from inventario.models import Insumo


class Producto(models.Model):

    nombre = models.CharField(
        max_length=150,
        unique=True
    )

    descripcion = models.TextField(
        blank=True
    )

    precio_base = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    activo = models.BooleanField(
        default=True
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return self.nombre


class Receta(models.Model):

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='recetas'
    )

    insumo = models.ForeignKey(
        Insumo,
        on_delete=models.PROTECT,
        related_name='recetas'
    )

    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    class Meta:
        ordering = ['producto__nombre', 'insumo__nombre']
        verbose_name = 'Ingrediente de receta'
        verbose_name_plural = 'Ingredientes de recetas'

        constraints = [
            models.UniqueConstraint(
                fields=['producto', 'insumo'],
                name='un_insumo_por_producto'
            )
        ]

    def __str__(self):
        return (
            f"{self.producto.nombre} - "
            f"{self.insumo.nombre}: "
            f"{self.cantidad} {self.insumo.unidad_medida}"
        )