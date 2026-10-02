from django.db import models


class Service(models.Model):
    """
    Representa un servicio o plan de Internet ofrecido
    por el ISP.
    """

    # Nombre comercial del plan.
    nombre = models.CharField(
        max_length=100
    )

    # Descripción general del servicio.
    descripcion = models.TextField(
        blank=True
    )

    # Velocidad contratada por el cliente en Mbps.
    velocidad_mbps = models.PositiveIntegerField()

    # Precio mensual del servicio.
    precio_mensual = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    # Permite activar o desactivar un plan sin eliminarlo.
    activo = models.BooleanField(
        default=True
    )

    # Fecha en que el servicio fue registrado.
    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        """
        Representación legible del servicio.
        """
        return f"{self.nombre} - {self.velocidad_mbps} Mbps"