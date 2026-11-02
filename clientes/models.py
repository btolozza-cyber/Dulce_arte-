from django.db import models

class Cliente(models.Model):

    nombre = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField(blank=True)
    direccion = models.TextField(blank=True)

    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.nombre