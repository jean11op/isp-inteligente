from django.conf import settings
from django.db import models


class Technician(models.Model):
    """
    Representa a un técnico encargado de realizar
    visitas y atender incidencias en campo.
    """

    # Cuenta de usuario asociada al técnico.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="technician_profile"
    )

    # Especialidad principal del técnico.
    especialidad = models.CharField(
        max_length=100
    )

    # Indica si el técnico está disponible para recibir nuevas asignaciones.
    disponible = models.BooleanField(
        default=True
    )

    # Latitud de la ubicación actual del técnico.
    latitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    # Longitud de la ubicación actual del técnico.
    longitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    # Cantidad de trabajos que actualmente tiene asignados.
    carga_trabajo = models.PositiveIntegerField(
        default=0
    )

    # Permite desactivar al técnico sin eliminar su historial.
    activo = models.BooleanField(
        default=True
    )

    # Fecha de registro del técnico.
    fecha_registro = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.especialidad}"