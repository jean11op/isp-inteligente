"""Tipos independientes de Django para recorridos con varias visitas.

La matriz la prepara un proveedor (simulado durante el desarrollo y, en otra
fase, Google Routes). Los tiempos reflejan la salida considerada por el
proveedor; este módulo no inventa datos de tráfico ni consulta servicios.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable


def _finite_non_negative(value: float, label: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise ValueError(f"{label} debe ser un número finito no negativo.")
    return number


@dataclass(frozen=True)
class RouteStop:
    """Ubicación que debe visitarse; `stop_id` debe ser estable y único."""

    stop_id: str
    latitude: float
    longitude: float
    service_duration_seconds: float = 0.0

    def __post_init__(self) -> None:
        identifier = self.stop_id.strip()
        if not identifier:
            raise ValueError("Cada visita debe tener un identificador no vacío.")
        latitude, longitude = float(self.latitude), float(self.longitude)
        if not math.isfinite(latitude) or not -90 <= latitude <= 90:
            raise ValueError("La latitud debe estar entre -90 y 90.")
        if not math.isfinite(longitude) or not -180 <= longitude <= 180:
            raise ValueError("La longitud debe estar entre -180 y 180.")
        object.__setattr__(self, "stop_id", identifier)
        object.__setattr__(self, "latitude", latitude)
        object.__setattr__(self, "longitude", longitude)
        object.__setattr__(
            self,
            "service_duration_seconds",
            _finite_non_negative(self.service_duration_seconds, "La duración del servicio"),
        )


@dataclass(frozen=True)
class TrafficIncident:
    """Incidente asociado a un tramo: accidente, obra, congestión o cierre."""

    incident_id: str
    kind: str
    severity: str = "unknown"
    description: str = ""
    starts_at: datetime | None = None
    ends_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.incident_id.strip():
            raise ValueError("El incidente debe tener un identificador no vacío.")
        if not self.kind.strip():
            raise ValueError("El incidente debe indicar su tipo.")


@dataclass(frozen=True)
class TravelEstimate:
    """Costo dirigido de desplazamiento entre dos puntos."""

    duration_seconds: float | None
    distance_meters: float | None
    incidents: tuple[TrafficIncident, ...] = ()
    blocked: bool = False
    geometry: tuple[tuple[float, float], ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "geometry", _validate_geometry(self.geometry))
        if self.blocked:
            for value, label in (
                (self.duration_seconds, "La duración"),
                (self.distance_meters, "La distancia"),
            ):
                if value is not None:
                    _finite_non_negative(value, label)
            return

        if self.duration_seconds is None or self.distance_meters is None:
            raise ValueError("Un tramo transitable requiere duración y distancia.")
        object.__setattr__(
            self,
            "duration_seconds",
            _finite_non_negative(self.duration_seconds, "La duración"),
        )
        object.__setattr__(
            self,
            "distance_meters",
            _finite_non_negative(self.distance_meters, "La distancia"),
        )


class TravelMatrix:
    """Matriz dirigida de costos entre el inicio y las visitas del recorrido."""

    def __init__(self, stop_ids: Iterable[str], *, departure_time: datetime | None = None):
        identifiers = tuple(stop_ids)
        if any(
            not isinstance(identifier, str) or not identifier.strip()
            for identifier in identifiers
        ):
            raise ValueError("Los identificadores de la matriz deben ser textos no vacíos.")
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("Los identificadores de la matriz deben ser únicos.")
        self._stop_ids = frozenset(identifiers)
        self.departure_time = departure_time
        self._estimates: dict[tuple[str, str], TravelEstimate] = {}

    @property
    def stop_ids(self) -> frozenset[str]:
        return self._stop_ids

    def add_estimate(
        self,
        origin_id: str,
        destination_id: str,
        estimate: TravelEstimate,
    ) -> None:
        """Agrega o reemplaza el costo dirigido de un par de ubicaciones."""
        if origin_id not in self._stop_ids or destination_id not in self._stop_ids:
            raise KeyError("El origen y destino deben pertenecer a la matriz.")
        if origin_id == destination_id:
            raise ValueError("No se agregan tramos de una ubicación hacia sí misma.")
        if not isinstance(estimate, TravelEstimate):
            raise TypeError("estimate debe ser una instancia de TravelEstimate.")
        self._estimates[(origin_id, destination_id)] = estimate

    def estimate(self, origin_id: str, destination_id: str) -> TravelEstimate | None:
        """Devuelve `None` si no hay una ruta utilizable para el par."""
        estimate = self._estimates.get((origin_id, destination_id))
        if estimate is None or estimate.blocked:
            return None
        return estimate


@dataclass(frozen=True)
class PlannedLeg:
    origin_id: str
    destination_id: str
    duration_seconds: float
    distance_meters: float
    incidents: tuple[TrafficIncident, ...] = ()
    geometry: tuple[tuple[float, float], ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "origin_id": self.origin_id,
            "destination_id": self.destination_id,
            "duration_seconds": self.duration_seconds,
            "distance_meters": self.distance_meters,
            "incidents": [_incident_to_dict(incident) for incident in self.incidents],
            "geometry": [list(point) for point in self.geometry],
        }


@dataclass(frozen=True)
class ItineraryResult:
    """Orden y métricas; `path` incluye el inicio y el retorno opcional."""

    path: tuple[str, ...]
    legs: tuple[PlannedLeg, ...]
    driving_duration_seconds: float
    service_duration_seconds: float
    total_duration_seconds: float
    total_distance_meters: float
    algorithm: str
    departure_time: datetime | None = None

    @property
    def ordered_stops(self) -> tuple[str, ...]:
        """Visitas en orden, sin el inicio ni el retorno opcional."""
        if len(self.path) <= 1:
            return ()
        stops = self.path[1:]
        if stops[-1] == self.path[0]:
            return stops[:-1]
        return stops

    def to_dict(self) -> dict[str, object]:
        """Convierte el resultado a datos serializables por la API de Backend."""
        return {
            "path": list(self.path),
            "ordered_stops": list(self.ordered_stops),
            "legs": [leg.to_dict() for leg in self.legs],
            "driving_duration_seconds": self.driving_duration_seconds,
            "service_duration_seconds": self.service_duration_seconds,
            "total_duration_seconds": self.total_duration_seconds,
            "total_distance_meters": self.total_distance_meters,
            "algorithm": self.algorithm,
            "departure_time": (
                self.departure_time.isoformat() if self.departure_time else None
            ),
        }


def _validate_geometry(
    geometry: tuple[tuple[float, float], ...],
) -> tuple[tuple[float, float], ...]:
    points: list[tuple[float, float]] = []
    for point in geometry:
        if len(point) != 2:
            raise ValueError("Cada punto de geometría debe ser (latitud, longitud).")
        latitude, longitude = float(point[0]), float(point[1])
        if not math.isfinite(latitude) or not -90 <= latitude <= 90:
            raise ValueError("La latitud de geometría debe estar entre -90 y 90.")
        if not math.isfinite(longitude) or not -180 <= longitude <= 180:
            raise ValueError("La longitud de geometría debe estar entre -180 y 180.")
        points.append((latitude, longitude))
    return tuple(points)


def _incident_to_dict(incident: TrafficIncident) -> dict[str, str | None]:
    return {
        "incident_id": incident.incident_id,
        "kind": incident.kind,
        "severity": incident.severity,
        "description": incident.description,
        "starts_at": incident.starts_at.isoformat() if incident.starts_at else None,
        "ends_at": incident.ends_at.isoformat() if incident.ends_at else None,
    }
