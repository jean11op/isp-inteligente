"""Búsqueda de costo uniforme (UCS)."""

import heapq
from itertools import count
from time import perf_counter

from .graph import Graph, Node, PathResult, result_from_parents


def uniform_cost_search(
    graph: Graph[Node], start: Node, goal: Node
) -> PathResult[Node] | None:
    """Encuentra una ruta de costo mínimo con pesos no negativos."""
    graph.validate_endpoints(start, goal)
    started_at = perf_counter()
    if start == goal:
        return PathResult((start,), 0.0, "UCS", 0, perf_counter() - started_at)

    sequence = count()
    frontier: list[tuple[float, int, Node]] = [(0.0, next(sequence), start)]
    best_cost: dict[Node, float] = {start: 0.0}
    parents: dict[Node, Node] = {}
    expanded_nodes = 0

    while frontier:
        current_cost, _, current = heapq.heappop(frontier)
        if current_cost > best_cost.get(current, float("inf")):
            continue
        if current == goal:
            return result_from_parents(
                graph,
                parents,
                start,
                goal,
                "UCS",
                expanded_nodes,
                perf_counter() - started_at,
            )

        expanded_nodes += 1
        for neighbor, weight in graph.neighbors(current):
            candidate_cost = current_cost + weight
            if candidate_cost < best_cost.get(neighbor, float("inf")):
                best_cost[neighbor] = candidate_cost
                parents[neighbor] = current
                heapq.heappush(
                    frontier, (candidate_cost, next(sequence), neighbor)
                )
    return None
