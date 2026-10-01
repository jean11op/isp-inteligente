from django.conf import settings
from django.db import models


class Specialist(models.Model):
    """
    Representa a un especialista encargado de analizar
    incidencias y realizar diagnósticos.
    """

    # Cuenta de usuario asociada al especialista.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="specialist_profile"
    )

    # Área o especialidad del especialista.
    especialidad = models.CharField(
        max_length=100
    )

    # Indica si el especialista puede recibir nuevos tickets.
    disponible = models.BooleanField(
        default=True
    )

    # Permite desactivar al especialista sin eliminar su historial.
    activo = models.BooleanField(
        default=True
    )

    # Fecha en la que se registró el especialista.
    fecha_registro = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.especialidad}"