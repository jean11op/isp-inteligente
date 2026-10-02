"""Búsqueda en profundidad (DFS)."""

from time import perf_counter

from .graph import Graph, Node, PathResult, result_from_parents


def depth_first_search(
    graph: Graph[Node], start: Node, goal: Node
) -> PathResult[Node] | None:
    """Encuentra una ruta siguiendo la profundidad y el orden de vecinos.

    DFS no garantiza la ruta más corta. Devuelve ``None`` si no hay conexión.
    """
    graph.validate_endpoints(start, goal)
    started_at = perf_counter()
    if start == goal:
        return PathResult((start,), 0.0, "DFS", 0, perf_counter() - started_at)

    frontier = [start]
    visited = {start}
    parents: dict[Node, Node] = {}
    expanded_nodes = 0

    while frontier:
        current = frontier.pop()
        if current == goal:
            return result_from_parents(
                graph,
                parents,
                start,
                goal,
                "DFS",
                expanded_nodes,
                perf_counter() - started_at,
            )

        # Se invierte para que el primer vecino agregado se explore primero.
        expanded_nodes += 1
        for neighbor, _ in reversed(graph.neighbors(current)):
            if neighbor not in visited:
                visited.add(neighbor)
                parents[neighbor] = current
                frontier.append(neighbor)
    return None
