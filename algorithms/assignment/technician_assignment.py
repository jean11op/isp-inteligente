"""Puntuación y selección pura de técnicos candidatos."""

from __future__ import annotations

import math
import unicodedata
from dataclasses import dataclass

from .scoring import AssignmentPolicy, TicketPriority


@dataclass(frozen=True)
class TechnicianCandidate:
    """Datos mínimos que el backend entrega al selector."""

    technician_id: int | str
    specialty: str
    available: bool
    active: bool
    workload: int
    latitude: float | None
    longitude: float | None


@dataclass(frozen=True)
class ScoredTechnician:
    candidate: TechnicianCandidate
    score: float
    distance_km: float
    distance_score: float
    workload_score: float


def _normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.strip().casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def _validate_coordinates(latitude: float, longitude: float) -> tuple[float, float]:
    lat, lon = float(latitude), float(longitude)
    if not math.isfinite(lat) or not -90 <= lat <= 90:
        raise ValueError("La latitud debe estar entre -90 y 90.")
    if not math.isfinite(lon) or not -180 <= lon <= 180:
        raise ValueError("La longitud debe estar entre -180 y 180.")
    return lat, lon


def haversine_km(
    latitude_a: float,
    longitude_a: float,
    latitude_b: float,
    longitude_b: float,
) -> float:
    """Calcula distancia geográfica en línea recta; no sigue calles."""
    lat_a, lon_a = _validate_coordinates(latitude_a, longitude_a)
    lat_b, lon_b = _validate_coordinates(latitude_b, longitude_b)
    radius_km = 6371.0088

    phi_a, phi_b = math.radians(lat_a), math.radians(lat_b)
    delta_phi = math.radians(lat_b - lat_a)
    delta_lambda = math.radians(lon_b - lon_a)
    haversine = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi_a) * math.cos(phi_b) * math.sin(delta_lambda / 2) ** 2
    )
    return 2 * radius_km * math.asin(math.sqrt(min(1.0, haversine)))


def is_within_radius(
    latitude_a: float,
    longitude_a: float,
    latitude_b: float,
    longitude_b: float,
    radius_km: float,
) -> bool:
    """Indica si dos ubicaciones están dentro de un radio en línea recta."""
    radius = float(radius_km)
    if not math.isfinite(radius) or radius < 0:
        raise ValueError("El radio debe ser finito y no negativo.")
    return haversine_km(latitude_a, longitude_a, latitude_b, longitude_b) <= radius


def score_technicians(
    candidates: list[TechnicianCandidate] | tuple[TechnicianCandidate, ...],
    *,
    required_specialty: str,
    destination_latitude: float,
    destination_longitude: float,
    ticket_priority: str | TicketPriority,
    policy: AssignmentPolicy | None = None,
) -> list[ScoredTechnician]:
    """Filtra y ordena candidatos válidos para un destino.

    Se descartan técnicos inactivos, no disponibles, sin especialidad
    coincidente o sin coordenadas válidas. La puntuación combina distancia
    geográfica y carga de trabajo; sus pesos dependen de la prioridad y pueden
    configurarse. La especialidad es un requisito, no una bonificación.
    """
    destination = _validate_coordinates(destination_latitude, destination_longitude)
    requested_specialty = _normalize_text(required_specialty)
    if not requested_specialty:
        raise ValueError("Se requiere una especialidad para filtrar candidatos.")

    active_policy = policy or AssignmentPolicy()
    weights = active_policy.weights_for(ticket_priority)

    eligible: list[tuple[TechnicianCandidate, float]] = []
    for candidate in candidates:
        if not candidate.active or not candidate.available:
            continue
        if _normalize_text(candidate.specialty) != requested_specialty:
            continue
        if candidate.workload < 0:
            raise ValueError("La carga de trabajo no puede ser negativa.")
        if candidate.latitude is None or candidate.longitude is None:
            continue
        distance = haversine_km(
            candidate.latitude,
            candidate.longitude,
            destination[0],
            destination[1],
        )
        eligible.append((candidate, distance))

    if not eligible:
        return []

    max_distance = max(distance for _, distance in eligible)
    max_workload = max(candidate.workload for candidate, _ in eligible)
    total_weight = weights.distance + weights.workload
    scored: list[ScoredTechnician] = []

    for candidate, distance in eligible:
        distance_score = (
            1.0 if max_distance == 0 else 1.0 - distance / max_distance
        )
        workload_score = (
            1.0
            if max_workload == 0
            else 1.0 - candidate.workload / max_workload
        )
        score = (
            weights.distance * distance_score
            + weights.workload * workload_score
        ) / total_weight
        scored.append(
            ScoredTechnician(
                candidate=candidate,
                score=score,
                distance_km=distance,
                distance_score=distance_score,
                workload_score=workload_score,
            )
        )

    return sorted(
        scored,
        key=lambda item: (
            -item.score,
            item.distance_km,
            item.candidate.workload,
            str(item.candidate.technician_id),
        ),
    )


def select_technician(
    candidates: list[TechnicianCandidate] | tuple[TechnicianCandidate, ...],
    *,
    required_specialty: str,
    destination_latitude: float,
    destination_longitude: float,
    ticket_priority: str | TicketPriority,
    policy: AssignmentPolicy | None = None,
) -> ScoredTechnician | None:
    """Devuelve el mejor candidato o ``None`` para que Backend escale."""
    ranked = score_technicians(
        candidates,
        required_specialty=required_specialty,
        destination_latitude=destination_latitude,
        destination_longitude=destination_longitude,
        ticket_priority=ticket_priority,
        policy=policy,
    )
    return ranked[0] if ranked else None
