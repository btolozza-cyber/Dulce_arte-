from django.db import models
from django.core.validators import MinValueValidator


class Insumo(models.Model):

    class UnidadMedida(models.TextChoices):
        KILOGRAMO = 'kg', 'Kilogramo'
        GRAMO = 'g', 'Gramo'
        LITRO = 'l', 'Litro'
        MILILITRO = 'ml', 'Mililitro'
        UNIDAD = 'unidad', 'Unidad'

    nombre = models.CharField(
        max_length=150,
        unique=True
    )

    descripcion = models.TextField(
        blank=True
    )

    unidad_medida = models.CharField(
        max_length=10,
        choices=UnidadMedida.choices
    )

    stock_actual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    stock_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True
    )

    @property
    def stock_bajo(self):
        return self.stock_actual <= self.stock_minimo

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Insumo'
        verbose_name_plural = 'Insumos'

    def __str__(self):
        return self.nombre


class MovimientoInventario(models.Model):

    class TipoMovimiento(models.TextChoices):
        ENTRADA = 'entrada', 'Entrada'
        SALIDA = 'salida', 'Salida'
        AJUSTE = 'ajuste', 'Ajuste'

    insumo = models.ForeignKey(
        Insumo,
        on_delete=models.PROTECT,
        related_name='movimientos'
    )

    tipo = models.CharField(
        max_length=10,
        choices=TipoMovimiento.choices
    )

    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    
    stock_anterior = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    stock_nuevo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    observacion = models.TextField(
        blank=True
    )

    fecha_movimiento = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-fecha_movimiento']
        verbose_name = 'Movimiento de inventario'
        verbose_name_plural = 'Movimientos de inventario'

    def __str__(self):
        return (
            f"{self.insumo.nombre} - "
            f"{self.get_tipo_display()} - "
            f"{self.cantidad}"
        )