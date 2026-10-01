"""Búsqueda en anchura (BFS), óptima en cantidad de aristas."""

from collections import deque
from time import perf_counter

from .graph import Graph, Node, PathResult, result_from_parents


def breadth_first_search(
    graph: Graph[Node], start: Node, goal: Node
) -> PathResult[Node] | None:
    """Encuentra una ruta con el menor número de aristas.

    No minimiza el costo cuando los pesos son diferentes. Devuelve ``None``
    si no existe una ruta y eleva ``KeyError`` si falta un extremo del grafo.
    """
    graph.validate_endpoints(start, goal)
    started_at = perf_counter()
    if start == goal:
        return PathResult((start,), 0.0, "BFS", 0, perf_counter() - started_at)

    frontier = deque([start])
    visited = {start}
    parents: dict[Node, Node] = {}
    expanded_nodes = 0

    while frontier:
        current = frontier.popleft()
        expanded_nodes += 1
        for neighbor, _ in graph.neighbors(current):
            if neighbor in visited:
                continue
            visited.add(neighbor)
            parents[neighbor] = current
            if neighbor == goal:
                return result_from_parents(
                    graph,
                    parents,
                    start,
                    goal,
                    "BFS",
                    expanded_nodes,
                    perf_counter() - started_at,
                )
            frontier.append(neighbor)
    return None
