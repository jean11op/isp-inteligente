from django.db import models


class Visit(models.Model):
    """
    Representa una visita técnica realizada para atender
    una incidencia registrada en un ticket.
    """

    class Status(models.TextChoices):
        # La visita fue programada pero todavía no comenzó.
        PROGRAMADA = "PROGRAMADA", "Programada"

        # El técnico inició el desplazamiento.
        EN_CAMINO = "EN_CAMINO", "En camino"

        # El técnico llegó al domicilio del cliente.
        EN_DOMICILIO = "EN_DOMICILIO", "En domicilio"

        # El técnico está atendiendo la incidencia.
        EN_ATENCION = "EN_ATENCION", "En atención"

        # La visita terminó correctamente.
        COMPLETADA = "COMPLETADA", "Completada"

        # La visita no pudo completarse.
        CANCELADA = "CANCELADA", "Cancelada"

    # Ticket que originó la visita.
    ticket = models.ForeignKey(
        "tickets.Ticket",
        on_delete=models.CASCADE,
        related_name="visits"
    )

    # Técnico encargado de realizar la visita.
    technician = models.ForeignKey(
        "technicians.Technician",
        on_delete=models.PROTECT,
        related_name="visits"
    )

    # Estado actual de la visita.
    estado = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PROGRAMADA
    )

    # Fecha y hora programada para la visita.
    fecha_programada = models.DateTimeField()

    # Fecha y hora en que el técnico inició la visita.
    fecha_inicio = models.DateTimeField(
        null=True,
        blank=True
    )

    # Fecha y hora en que terminó la visita.
    fecha_fin = models.DateTimeField(
        null=True,
        blank=True
    )

    # Resultado registrado por el técnico.
    resultado = models.TextField(
        blank=True
    )

    # Observaciones adicionales de la atención.
    observaciones = models.TextField(
        blank=True
    )

    # Fecha de creación del registro.
    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Visita #{self.id} - Ticket #{self.ticket.id}"