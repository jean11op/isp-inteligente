"""Ejecución conjunta de los algoritmos de rutas."""

from .astar import Heuristic, astar_search
from .bfs import breadth_first_search
from .dfs import depth_first_search
from .graph import Graph, Node, PathResult
from .greedy import greedy_best_first_search
from .ucs import uniform_cost_search


def compare_routes(
    graph: Graph[Node], start: Node, goal: Node, heuristic: Heuristic
) -> dict[str, PathResult[Node] | None]:
    """Devuelve resultados comparables para BFS, DFS, UCS, Greedy y A*."""
    return {
        "BFS": breadth_first_search(graph, start, goal),
        "DFS": depth_first_search(graph, start, goal),
        "UCS": uniform_cost_search(graph, start, goal),
        "Greedy": greedy_best_first_search(graph, start, goal, heuristic),
        "A*": astar_search(graph, start, goal, heuristic),
    }
