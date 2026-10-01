from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Evaluation(models.Model):
    """
    Representa la evaluación realizada por el cliente
    después de la atención de un ticket.
    """

    # Ticket que fue evaluado.
    ticket = models.OneToOneField(
        "tickets.Ticket",
        on_delete=models.CASCADE,
        related_name="evaluation"
    )

    # Puntuación otorgada por el cliente, de 1 a 5.
    puntuacion = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )

    # Comentario opcional del cliente.
    comentario = models.TextField(
        blank=True
    )

    # Fecha en la que se realizó la evaluación.
    fecha_evaluacion = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Evaluación Ticket #{self.ticket.id} - {self.puntuacion}/5"