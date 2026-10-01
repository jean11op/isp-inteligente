"""Motor genérico de inferencia por reglas, independiente de Django."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import Iterable


def normalize_fact(fact: str) -> str:
    """Normaliza un hecho para evitar diferencias de mayúsculas y espacios."""
    if not isinstance(fact, str):
        raise TypeError("Los hechos deben ser cadenas de texto.")
    normalized = unicodedata.normalize("NFKD", fact.strip().casefold())
    normalized = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    normalized = "_".join(normalized.split())
    if not normalized:
        raise ValueError("Un hecho no puede estar vacío.")
    return normalized


@dataclass(frozen=True)
class Rule:
    """Regla de producción: si todos los antecedentes son ciertos, infiere un hecho."""

    rule_id: str
    premises: frozenset[str]
    conclusion: str
    description: str = ""
    priority: int = 0

    def __post_init__(self) -> None:
        rule_id = self.rule_id.strip()
        if not rule_id:
            raise ValueError("Cada regla necesita un identificador.")
        if isinstance(self.priority, bool) or not isinstance(self.priority, int):
            raise TypeError("La prioridad debe ser un entero.")
        premises = frozenset(normalize_fact(item) for item in self.premises)
        if not premises:
            raise ValueError("Una regla debe tener al menos un antecedente.")
        object.__setattr__(self, "rule_id", rule_id)
        object.__setattr__(self, "premises", premises)
        object.__setattr__(self, "conclusion", normalize_fact(self.conclusion))
        object.__setattr__(self, "description", self.description.strip())


@dataclass(frozen=True)
class ForwardResult:
    """Cierre de hechos producido por encadenamiento hacia adelante."""

    initial_facts: frozenset[str]
    facts: frozenset[str]
    fired_rules: tuple[Rule, ...]

    @property
    def inferred_facts(self) -> frozenset[str]:
        return self.facts - self.initial_facts

    @property
    def explanation(self) -> tuple[str, ...]:
        return tuple(_explain(rule) for rule in self.fired_rules)


@dataclass(frozen=True)
class BackwardResult:
    """Resultado de intentar demostrar una hipótesis hacia atrás."""

    goal: str
    proven: bool
    initial_facts: frozenset[str]
    facts: frozenset[str]
    fired_rules: tuple[Rule, ...]

    @property
    def inferred_facts(self) -> frozenset[str]:
        return self.facts - self.initial_facts

    @property
    def explanation(self) -> tuple[str, ...]:
        return tuple(_explain(rule) for rule in self.fired_rules)


def _explain(rule: Rule) -> str:
    detail = f" — {rule.description}" if rule.description else ""
    premises = " Y ".join(sorted(rule.premises))
    return f"{rule.rule_id}: SI {premises} ENTONCES {rule.conclusion}{detail}"


class KnowledgeBase:
    """Base de reglas con inferencia hacia adelante y hacia atrás.

    Las reglas se consideran monotónicas: los hechos inferidos no se retiran.
    Cuando hay varias reglas habilitadas se evalúan por prioridad, especificidad
    (más antecedentes primero) y orden de registro. Todas las reglas compatibles
    pueden dispararse; la prioridad ordena la traza, no descarta conclusiones.
    """

    def __init__(self, rules: Iterable[Rule]) -> None:
        self.rules = tuple(rules)
        identifiers = [rule.rule_id for rule in self.rules]
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("Los identificadores de regla deben ser únicos.")
        self._ordered_rules = tuple(
            rule
            for _, rule in sorted(
                enumerate(self.rules),
                key=lambda item: (-item[1].priority, -len(item[1].premises), item[0]),
            )
        )
        by_conclusion: dict[str, list[Rule]] = {}
        for rule in self._ordered_rules:
            by_conclusion.setdefault(rule.conclusion, []).append(rule)
        self._by_conclusion = {
            conclusion: tuple(conclusion_rules)
            for conclusion, conclusion_rules in by_conclusion.items()
        }

    def forward_chain(self, facts: Iterable[str]) -> ForwardResult:
        """Aplica reglas hasta que una pasada completa no agregue hechos."""
        initial = frozenset(normalize_fact(fact) for fact in facts)
        known = set(initial)
        fired: list[Rule] = []
        fired_ids: set[str] = set()

        while True:
            changed = False
            for rule in self._ordered_rules:
                if rule.rule_id in fired_ids or rule.conclusion in known:
                    continue
                if rule.premises <= known:
                    known.add(rule.conclusion)
                    fired.append(rule)
                    fired_ids.add(rule.rule_id)
                    changed = True
            if not changed:
                break

        return ForwardResult(initial, frozenset(known), tuple(fired))

    def backward_chain(self, goal: str, facts: Iterable[str]) -> BackwardResult:
        """Intenta demostrar una hipótesis; los ciclos se cortan por rama."""
        normalized_goal = normalize_fact(goal)
        initial = frozenset(normalize_fact(fact) for fact in facts)

        def prove(
            current_goal: str,
            known: set[str],
            fired: list[Rule],
            active_goals: frozenset[str],
        ) -> tuple[bool, set[str], list[Rule]]:
            if current_goal in known:
                return True, known, fired
            if current_goal in active_goals:
                return False, known, fired

            next_active = active_goals | {current_goal}
            for rule in self._by_conclusion.get(current_goal, ()):
                branch_facts = set(known)
                branch_fired = list(fired)
                successful = True
                for premise in sorted(rule.premises):
                    proven, branch_facts, branch_fired = prove(
                        premise, branch_facts, branch_fired, next_active
                    )
                    if not proven:
                        successful = False
                        break
                if successful:
                    branch_facts.add(current_goal)
                    if rule.rule_id not in {item.rule_id for item in branch_fired}:
                        branch_fired.append(rule)
                    return True, branch_facts, branch_fired
            return False, known, fired

        proven, final_facts, fired_rules = prove(
            normalized_goal, set(initial), [], frozenset()
        )
        return BackwardResult(
            normalized_goal,
            proven,
            initial,
            frozenset(final_facts),
            tuple(fired_rules),
        )
