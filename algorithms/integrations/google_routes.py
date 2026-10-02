"""Punto de extensión seguro para Google Routes.

Esta entrega no incluye llamadas HTTP ni lee claves. La clase reserva el
contrato y falla de forma explícita hasta que el equipo acuerde e integre el
proveedor. Importarla o instanciarla no consume eventos ni requiere credenciales.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from algorithms.route_planning.models import RouteStop, TravelMatrix
from algorithms.route_planning.providers import TravelMatrixProvider


class GoogleRoutesIntegrationPending(RuntimeError):
    """La integración real se habilitará en un bloque posterior del equipo."""


class GoogleRoutesAdapter(TravelMatrixProvider):
    """Adaptador deliberadamente inactivo; nunca envía solicitudes de red."""

    enabled_by_default = False

    def build_matrix(
        self,
        stops: Sequence[RouteStop],
        *,
        departure_time: datetime | None = None,
    ) -> TravelMatrix:
        del stops, departure_time
        raise GoogleRoutesIntegrationPending(
            "Google Routes todavía no está integrado. Usa una matriz de prueba "
            "hasta acordar el contrato y habilitar la integración."
        )
