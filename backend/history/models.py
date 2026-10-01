from django.conf import settings
from django.db import models


class TicketHistory(models.Model):
    """
    Registra los cambios importantes realizados sobre un ticket.
    Permite conservar la trazabilidad de la atención.
    """

    # Ticket al que pertenece este registro histórico.
    ticket = models.ForeignKey(
        "tickets.Ticket",
        on_delete=models.CASCADE,
        related_name="history"
    )

    # Usuario que realizó la acción.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ticket_history"
    )

    # Estado anterior del ticket.
    estado_anterior = models.CharField(
        max_length=30,
        blank=True
    )

    # Nuevo estado del ticket.
    estado_nuevo = models.CharField(
        max_length=30
    )

    # Comentario o explicación del cambio.
    comentario = models.TextField(
        blank=True
    )

    # Momento en que ocurrió el cambio.
    fecha = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Ticket #{self.ticket.id}: {self.estado_nuevo}"