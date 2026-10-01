"""Búsqueda A*."""

import heapq
import math
from itertools import count
from time import perf_counter
from typing import Callable

from .graph import Graph, Node, PathResult, result_from_parents

Heuristic = Callable[[Node, Node], float]


def _estimate(heuristic: Heuristic, node: Node, goal: Node) -> float:
    value = float(heuristic(node, goal))
    if not math.isfinite(value) or value < 0:
        raise ValueError("La heurística debe ser finita y no negativa.")
    return value


def astar_search(
    graph: Graph[Node], start: Node, goal: Node, heuristic: Heuristic
) -> PathResult[Node] | None:
    """Encuentra una ruta óptima si la heurística es admisible.

    Los nodos pueden reabrirse cuando aparece un costo mejor, por lo que no
    se exige consistencia. La heurística debe ser admisible para garantizar
    optimalidad; el módulo valida valores, pero no puede validar esa propiedad.
    """
    graph.validate_endpoints(start, goal)
    started_at = perf_counter()
    if start == goal:
        return PathResult((start,), 0.0, "A*", 0, perf_counter() - started_at)

    sequence = count()
    start_estimate = _estimate(heuristic, start, goal)
    frontier: list[tuple[float, int, float, Node]] = [
        (start_estimate, next(sequence), 0.0, start)
    ]
    best_cost: dict[Node, float] = {start: 0.0}
    parents: dict[Node, Node] = {}
    expanded_nodes = 0

    while frontier:
        _, _, current_cost, current = heapq.heappop(frontier)
        if current_cost > best_cost.get(current, float("inf")):
            continue
        if current == goal:
            return result_from_parents(
                graph,
                parents,
                start,
                goal,
                "A*",
                expanded_nodes,
                perf_counter() - started_at,
            )

        expanded_nodes += 1
        for neighbor, weight in graph.neighbors(current):
            candidate_cost = current_cost + weight
            if candidate_cost < best_cost.get(neighbor, float("inf")):
                best_cost[neighbor] = candidate_cost
                parents[neighbor] = current
                estimate = _estimate(heuristic, neighbor, goal)
                heapq.heappush(
                    frontier,
                    (
                        candidate_cost + estimate,
                        next(sequence),
                        candidate_cost,
                        neighbor,
                    ),
                )
    return None
