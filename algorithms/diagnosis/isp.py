"""Motor de diagnóstico ISP basado en reglas de producción configurables."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .inference import (
    BackwardResult,
    ForwardResult,
    KnowledgeBase,
    Rule,
    normalize_fact,
)


@dataclass(frozen=True)
class DiagnosisReport:
    """Resultado interpretable para que el Backend lo presente y persista."""

    initial_facts: frozenset[str]
    facts: frozenset[str]
    diagnoses: tuple[str, ...]
    recommendations: tuple[str, ...]
    fired_rules: tuple[Rule, ...]

    @property
    def inferred_facts(self) -> frozenset[str]:
        return self.facts - self.initial_facts

    @property
    def explanation(self) -> tuple[str, ...]:
        return tuple(
            f"{rule.rule_id}: SI {' Y '.join(sorted(rule.premises))} "
            f"ENTONCES {rule.conclusion}"
            + (f" — {rule.description}" if rule.description else "")
            for rule in self.fired_rules
        )

    @property
    def has_recommendation(self) -> bool:
        return bool(self.recommendations)

    def to_dict(self) -> dict[str, object]:
        """Devuelve un resultado serializable para la capa de Backend/API."""
        return {
            "diagnoses": list(self.diagnoses),
            "recommendations": list(self.recommendations),
            "observed_facts": sorted(self.initial_facts),
            "inferred_facts": sorted(self.inferred_facts),
            "applied_rules": [
                {
                    "id": rule.rule_id,
                    "premises": sorted(rule.premises),
                    "conclusion": rule.conclusion,
                    "description": rule.description,
                    "priority": rule.priority,
                }
                for rule in self.fired_rules
            ],
            "explanation": list(self.explanation),
        }


def default_isp_rules() -> tuple[Rule, ...]:
    """Reglas didácticas iniciales tomadas del ejemplo de diagnóstico de red.

    Deben ser revisadas por el equipo antes de considerarse política operativa
    del ISP. Las reglas producen hipótesis y recomendaciones, no certezas.
    """
    return (
        Rule(
            "ISP-R1-DIAG",
            frozenset({"no_hay_internet", "router_apagado"}),
            "diagnostico:router_apagado",
            "El ejemplo de clase relaciona la falta de Internet con el router apagado.",
            priority=10,
        ),
        Rule(
            "ISP-R1-REC",
            frozenset({"no_hay_internet", "router_apagado"}),
            "recomendacion:encender_router",
            "Verificar alimentación y encender el router.",
            priority=10,
        ),
        Rule(
            "ISP-R2-DIAG",
            frozenset({"router_encendido", "sin_conexion"}),
            "diagnostico:posible_problema_de_cableado",
            "El ejemplo de clase indica revisar el cable cuando sigue sin haber conexión.",
            priority=10,
        ),
        Rule(
            "ISP-R2-REC",
            frozenset({"router_encendido", "sin_conexion"}),
            "recomendacion:revisar_cable",
            "Revisar conexión y estado del cable.",
            priority=10,
        ),
        Rule(
            "ISP-R3-DIAG",
            frozenset({"cable_correcto", "sin_conexion"}),
            "diagnostico:posible_falla_externa",
            "El ejemplo de clase sugiere contactar al proveedor si el cable está correcto.",
            priority=10,
        ),
        Rule(
            "ISP-R3-REC",
            frozenset({"cable_correcto", "sin_conexion"}),
            "recomendacion:contactar_proveedor",
            "Escalar para verificar una posible incidencia del proveedor.",
            priority=10,
        ),
    )


class ISPDiagnosticEngine:
    """Interfaz de CU-40; no consulta modelos, APIs ni base de datos."""

    def __init__(self, rules: Iterable[Rule] | None = None) -> None:
        self.knowledge_base = KnowledgeBase(
            default_isp_rules() if rules is None else rules
        )

    def process(self, facts: Iterable[str]) -> DiagnosisReport:
        """Procesa hechos observados y devuelve hallazgos y recomendaciones."""
        result: ForwardResult = self.knowledge_base.forward_chain(facts)
        diagnoses = _outcomes(result.inferred_facts, "diagnostico:")
        recommendations = _outcomes(result.inferred_facts, "recomendacion:")
        return DiagnosisReport(
            result.initial_facts,
            result.facts,
            diagnoses,
            recommendations,
            result.fired_rules,
        )

    def verify_hypothesis(
        self, hypothesis: str, facts: Iterable[str]
    ) -> BackwardResult:
        """Verifica una hipótesis con encadenamiento hacia atrás.

        Devuelve ``BackwardResult`` para exponer si se probó y qué reglas se
        necesitaron.
        """
        if not isinstance(hypothesis, str):
            raise TypeError("La hipótesis debe ser una cadena de texto.")
        return self.knowledge_base.backward_chain(hypothesis, facts)


def _outcomes(facts: Iterable[str], prefix: str) -> tuple[str, ...]:
    normalized_prefix = normalize_fact(prefix)
    return tuple(
        sorted(
            fact[len(normalized_prefix) :]
            for fact in facts
            if fact.startswith(normalized_prefix)
        )
    )
