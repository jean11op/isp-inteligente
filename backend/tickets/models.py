from django.db import models


class Ticket(models.Model):
    """
    Representa una incidencia reportada por un cliente.

    El ticket permite controlar todo el ciclo de atención
    de una incidencia, desde su creación hasta su resolución.
    """

    class Priority(models.TextChoices):
        # Prioridad normal para incidencias que no requieren atención urgente.
        BAJA = "BAJA", "Baja"

        # Prioridad utilizada para incidencias de atención habitual.
        MEDIA = "MEDIA", "Media"

        # Prioridad para incidencias que requieren atención rápida.
        ALTA = "ALTA", "Alta"

        # Prioridad máxima para incidencias críticas.
        CRITICA = "CRITICA", "Crítica"

    class Status(models.TextChoices):
        # El cliente acaba de registrar la incidencia.
        NUEVO = "NUEVO", "Nuevo"

        # La incidencia está siendo revisada.
        EN_REVISION = "EN_REVISION", "En revisión"

        # Se está esperando la intervención de un especialista.
        ESPERANDO_ESPECIALISTA = (
            "ESPERANDO_ESPECIALISTA",
            "Esperando especialista"
        )

        # El especialista ya realizó el diagnóstico.
        DIAGNOSTICADO = "DIAGNOSTICADO", "Diagnosticado"

        # El diagnóstico determinó que se necesita una visita.
        REQUIERE_VISITA = "REQUIERE_VISITA", "Requiere visita"

        # Ya se seleccionó un técnico para la visita.
        TECNICO_ASIGNADO = "TECNICO_ASIGNADO", "Técnico asignado"

        # El técnico comenzó su desplazamiento.
        EN_CAMINO = "EN_CAMINO", "En camino"

        # El técnico llegó al domicilio.
        EN_DOMICILIO = "EN_DOMICILIO", "En domicilio"

        # El técnico está atendiendo la incidencia.
        EN_ATENCION = "EN_ATENCION", "En atención"

        # La incidencia fue solucionada.
        RESUELTO = "RESUELTO", "Resuelto"

        # El ticket fue finalizado.
        CERRADO = "CERRADO", "Cerrado"

        # La primera atención no logró solucionar la incidencia.
        NO_RESUELTO = "NO_RESUELTO", "No resuelto"

        # La incidencia necesita una atención adicional.
        ESCALADO = "ESCALADO", "Escalado"

        # Se requiere una segunda visita técnica.
        SEGUNDA_VISITA = "SEGUNDA_VISITA", "Segunda visita"

    # Cliente que reportó la incidencia.
    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.PROTECT,
        related_name="tickets"
    )

    # Servicio de Internet relacionado con la incidencia.
    service = models.ForeignKey(
        "services.Service",
        on_delete=models.PROTECT,
        related_name="tickets",
        null=True,
        blank=True
    )

    # Título breve de la incidencia.
    titulo = models.CharField(
        max_length=150
    )

    # Descripción detallada del problema informado por el cliente.
    descripcion = models.TextField()

    # Nivel de prioridad de la incidencia.
    prioridad = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIA
    )

    # Estado actual del ciclo de atención.
    estado = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.NUEVO
    )

    # Diagnóstico realizado por el especialista.
    diagnostico = models.TextField(
        blank=True
    )

    # Solución aplicada a la incidencia.
    solucion = models.TextField(
        blank=True
    )

    # Especialista que realizó el diagnóstico.
    specialist = models.ForeignKey(
        "specialists.Specialist",
        on_delete=models.SET_NULL,
        related_name="tickets",
        null=True,
        blank=True
    )

    # Técnico asignado para atender la incidencia.
    technician = models.ForeignKey(
        "technicians.Technician",
        on_delete=models.SET_NULL,
        related_name="tickets",
        null=True,
        blank=True
    )

    # Fecha de creación automática del ticket.
    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    # Fecha de última modificación del ticket.
    fecha_actualizacion = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"Ticket #{self.id} - {self.titulo}"