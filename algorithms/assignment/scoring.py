"""Política configurable para puntuar candidatos a técnico."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Mapping


class TicketPriority(StrEnum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    CRITICA = "CRITICA"


@dataclass(frozen=True)
class ScoreWeights:
    """Pesos para distancia y carga; especialidad se valida como requisito."""

    distance: float = 1.0
    workload: float = 1.0

    def __post_init__(self) -> None:
        if self.distance < 0 or self.workload < 0:
            raise ValueError("Los pesos no pueden ser negativos.")
        if self.distance + self.workload == 0:
            raise ValueError("Al menos un peso debe ser mayor que cero.")


def _default_weights() -> dict[str, ScoreWeights]:
    # Una mayor urgencia prioriza la cercanía sobre el balance de carga.
    # Los pesos quedan configurables por si el equipo acuerda otra política.
    return {
        TicketPriority.BAJA.value: ScoreWeights(distance=0.30, workload=0.70),
        TicketPriority.MEDIA.value: ScoreWeights(distance=0.50, workload=0.50),
        TicketPriority.ALTA.value: ScoreWeights(distance=0.70, workload=0.30),
        TicketPriority.CRITICA.value: ScoreWeights(distance=0.85, workload=0.15),
    }


@dataclass(frozen=True)
class AssignmentPolicy:
    """Pesos ajustables por prioridad sin acoplarlos al modelo Django."""

    weights_by_priority: Mapping[str, ScoreWeights] = field(
        default_factory=_default_weights
    )

    def weights_for(self, priority: str | TicketPriority) -> ScoreWeights:
        key = str(priority).strip().upper()
        try:
            return self.weights_by_priority[key]
        except KeyError as exc:
            raise ValueError(f"Prioridad no configurada: {key!r}.") from exc
