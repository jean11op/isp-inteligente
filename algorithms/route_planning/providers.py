"""Contrato para fuentes de tiempos de viaje, sin dependencia de proveedor."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Protocol

from .models import RouteStop, TravelMatrix


class TravelMatrixProvider(Protocol):
    """Construye costos dirigidos para un conjunto de ubicaciones."""

    def build_matrix(
        self,
        stops: Sequence[RouteStop],
        *,
        departure_time: datetime | None = None,
    ) -> TravelMatrix:
        """Devuelve tiempos, distancias e incidentes para los pares consultados."""
        ...
