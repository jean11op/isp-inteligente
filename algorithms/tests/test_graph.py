import unittest

from algorithms.graph import Graph, compare_routes


class RouteSearchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = Graph[str]()
        self.graph.add_edge("A", "B", 4)
        self.graph.add_edge("A", "C", 2)
        self.graph.add_edge("C", "B", 1)
        self.graph.add_edge("B", "D", 3)
        self.graph.add_edge("C", "D", 8)
        self.heuristic = {"A": 6, "B": 3, "C": 4, "D": 0}

    def test_all_five_searches_return_comparable_results(self) -> None:
        results = compare_routes(
            self.graph,
            "A",
            "D",
            heuristic=lambda node, _goal: self.heuristic[node],
        )

        self.assertEqual({"BFS", "DFS", "UCS", "Greedy", "A*"}, set(results))
        for result in results.values():
            self.assertIsNotNone(result)
            assert result is not None
            self.assertEqual("A", result.path[0])
            self.assertEqual("D", result.path[-1])
            self.assertEqual(self.graph.path_cost(result.path), result.cost)
            self.assertGreater(result.expanded_nodes, 0)
            self.assertGreaterEqual(result.elapsed_seconds, 0)
        self.assertEqual(6, results["UCS"].cost)
        self.assertEqual(6, results["A*"].cost)

    def test_search_returns_none_for_disconnected_nodes(self) -> None:
        self.graph.add_node("Z")

        result = compare_routes(
            self.graph, "A", "Z", heuristic=lambda _node, _goal: 0
        )

        self.assertTrue(all(path is None for path in result.values()))

    def test_graph_rejects_negative_edge_weights(self) -> None:
        with self.assertRaises(ValueError):
            self.graph.add_edge("A", "Z", -1)


if __name__ == "__main__":
    unittest.main()
