"""Grafo ponderado y tipos compartidos por las búsquedas de rutas."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Generic, Hashable, TypeVar

Node = TypeVar("Node", bound=Hashable)


@dataclass(frozen=True)
class PathResult(Generic[Node]):
    """Ruta encontrada y costo real de recorrerla.

    ``cost`` siempre suma los pesos de las aristas de ``path``. En BFS y DFS
    la ruta se elige por orden de exploración, no por costo mínimo.
    ``expanded_nodes`` cuenta nodos cuyos vecinos se procesaron; ``elapsed_seconds``
    mide el tiempo de búsqueda y reconstrucción, sin incluir la creación del grafo.
    """

    path: tuple[Node, ...]
    cost: float
    algorithm: str
    expanded_nodes: int = 0
    elapsed_seconds: float = 0.0


class Graph(Generic[Node]):
    """Grafo con pesos no negativos y orden de vecinos determinista.

    Las aristas son bidireccionales por defecto. Para un grafo dirigido,
    construye con ``Graph(directed=True)`` o usa ``bidirectional=False`` al
    agregar una arista. Si se agrega dos veces la misma arista, el peso nuevo
    reemplaza al anterior.
    """

    def __init__(self, *, directed: bool = False) -> None:
        self.directed = directed
        self._adjacency: dict[Node, dict[Node, float]] = {}

    def add_node(self, node: Node) -> None:
        """Agrega un nodo si aún no existe."""
        self._adjacency.setdefault(node, {})

    def add_edge(
        self,
        source: Node,
        destination: Node,
        weight: float = 1.0,
        *,
        bidirectional: bool | None = None,
    ) -> None:
        """Agrega una arista; los nodos se crean automáticamente."""
        numeric_weight = float(weight)
        if not math.isfinite(numeric_weight) or numeric_weight < 0:
            raise ValueError("El peso debe ser un número finito no negativo.")

        self.add_node(source)
        self.add_node(destination)
        self._adjacency[source][destination] = numeric_weight

        make_reverse = not self.directed if bidirectional is None else bidirectional
        if make_reverse:
            self._adjacency[destination][source] = numeric_weight

    def has_node(self, node: Node) -> bool:
        return node in self._adjacency

    def nodes(self) -> tuple[Node, ...]:
        """Devuelve los nodos en el orden en que fueron agregados."""
        return tuple(self._adjacency)

    def neighbors(self, node: Node) -> tuple[tuple[Node, float], ...]:
        """Devuelve los vecinos y sus pesos en orden de inserción."""
        self._require_node(node)
        return tuple(self._adjacency[node].items())

    def edge_weight(self, source: Node, destination: Node) -> float:
        self._require_node(source)
        try:
            return self._adjacency[source][destination]
        except KeyError as exc:
            raise KeyError(f"No existe una arista de {source!r} a {destination!r}.") from exc

    def path_cost(self, path: tuple[Node, ...] | list[Node]) -> float:
        """Calcula y valida el costo de una ruta."""
        if not path:
            return 0.0
        return sum(
            self.edge_weight(source, destination)
            for source, destination in zip(path, path[1:])
        )

    def validate_endpoints(self, start: Node, goal: Node) -> None:
        self._require_node(start)
        self._require_node(goal)

    def _require_node(self, node: Node) -> None:
        if node not in self._adjacency:
            raise KeyError(f"El nodo {node!r} no pertenece al grafo.")


def result_from_parents(
    graph: Graph[Node],
    parents: dict[Node, Node],
    start: Node,
    goal: Node,
    algorithm: str,
    expanded_nodes: int = 0,
    elapsed_seconds: float = 0.0,
) -> PathResult[Node]:
    """Reconstruye una ruta a partir del mapa de predecesores."""
    path = [goal]
    while path[-1] != start:
        path.append(parents[path[-1]])
    path.reverse()
    return PathResult(
        tuple(path),
        graph.path_cost(path),
        algorithm,
        expanded_nodes,
        elapsed_seconds,
    )
