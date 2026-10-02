from django.db import models


class InventoryItem(models.Model):
    """
    Representa un material o equipo disponible
    dentro del inventario del ISP.
    """

    # Nombre del material o equipo.
    nombre = models.CharField(
        max_length=150
    )

    # Descripción del material.
    descripcion = models.TextField(
        blank=True
    )

    # Cantidad disponible actualmente.
    cantidad = models.PositiveIntegerField(
        default=0
    )

    # Unidad utilizada para expresar la cantidad.
    unidad = models.CharField(
        max_length=30,
        default="unidad"
    )

    # Permite desactivar un producto sin eliminar su historial.
    activo = models.BooleanField(
        default=True
    )

    # Fecha de registro.
    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.nombre} - {self.cantidad} {self.unidad}"
    
class InventoryUsage(models.Model):
    """
    Registra el uso de un material durante una visita técnica.
    """

    # Visita en la que se utilizó el material.
    visit = models.ForeignKey(
        "visits.Visit",
        on_delete=models.CASCADE,
        related_name="materials_used"
    )

    # Material utilizado.
    item = models.ForeignKey(
        InventoryItem,
        on_delete=models.PROTECT,
        related_name="usages"
    )

    # Cantidad utilizada durante la visita.
    cantidad = models.PositiveIntegerField()

    # Fecha del registro del consumo.
    fecha_registro = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.item.nombre} - {self.cantidad}"