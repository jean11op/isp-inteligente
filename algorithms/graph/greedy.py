"""Búsqueda voraz por mejor primero."""

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


def greedy_best_first_search(
    graph: Graph[Node], start: Node, goal: Node, heuristic: Heuristic
) -> PathResult[Node] | None:
    """Prioriza el nodo con menor heurística; no garantiza costo mínimo."""
    graph.validate_endpoints(start, goal)
    started_at = perf_counter()
    if start == goal:
        return PathResult((start,), 0.0, "Greedy", 0, perf_counter() - started_at)

    sequence = count()
    frontier: list[tuple[float, int, Node]] = [
        (_estimate(heuristic, start, goal), next(sequence), start)
    ]
    parents: dict[Node, Node] = {}
    best_cost: dict[Node, float] = {start: 0.0}
    closed: set[Node] = set()
    expanded_nodes = 0

    while frontier:
        _, _, current = heapq.heappop(frontier)
        if current in closed:
            continue
        if current == goal:
            return result_from_parents(
                graph,
                parents,
                start,
                goal,
                "Greedy",
                expanded_nodes,
                perf_counter() - started_at,
            )
        closed.add(current)

        expanded_nodes += 1
        for neighbor, weight in graph.neighbors(current):
            candidate_cost = best_cost[current] + weight
            if neighbor in closed or candidate_cost >= best_cost.get(
                neighbor, float("inf")
            ):
                continue
            best_cost[neighbor] = candidate_cost
            parents[neighbor] = current
            heapq.heappush(
                frontier,
                (_estimate(heuristic, neighbor, goal), next(sequence), neighbor),
            )
    return None
