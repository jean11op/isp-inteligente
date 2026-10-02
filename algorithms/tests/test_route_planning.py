"""Pruebas locales del optimizador; no acceden a Internet ni a proveedores."""

from __future__ import annotations

import unittest

from algorithms.integrations import GoogleRoutesAdapter, GoogleRoutesIntegrationPending
from algorithms.route_planning import (
    NoFeasibleRouteError,
    RouteStop,
    TrafficIncident,
    TravelEstimate,
    TravelMatrix,
    optimize_itinerary,
)


class ItineraryPlanningTests(unittest.TestCase):
    def setUp(self) -> None:
        self.start = RouteStop("base", -8.11, -79.03)
        self.a = RouteStop("A", -8.10, -79.02, service_duration_seconds=60)
        self.b = RouteStop("B", -8.12, -79.01, service_duration_seconds=120)
        self.matrix = TravelMatrix(["base", "A", "B"])

    def add_pair(
        self,
        origin: str,
        destination: str,
        seconds: float,
        meters: float,
        *,
        incidents: tuple[TrafficIncident, ...] = (),
    ) -> None:
        self.matrix.add_estimate(
            origin,
            destination,
            TravelEstimate(seconds, meters, incidents=incidents),
        )

    def test_minimizes_traffic_aware_duration_before_distance(self) -> None:
        # The detour via B is longer in meters, but much faster with current traffic.
        self.add_pair("base", "A", 900, 1000)
        self.add_pair("base", "B", 300, 1800)
        self.add_pair("A", "B", 900, 700)
        self.add_pair("B", "A", 240, 2100)

        result = optimize_itinerary(self.start, [self.a, self.b], self.matrix)

        self.assertEqual(("B", "A"), result.ordered_stops)
        self.assertEqual(540, result.driving_duration_seconds)
        self.assertEqual(180, result.service_duration_seconds)
        self.assertEqual(720, result.total_duration_seconds)

    def test_skips_closed_pair_and_keeps_incident_on_selected_leg(self) -> None:
        closure = TrafficIncident("incident-1", "roadClosure", "critical", "Cierre")
        self.matrix.add_estimate(
            "base", "A", TravelEstimate(None, None, incidents=(closure,), blocked=True)
        )
        self.add_pair("base", "B", 300, 700)
        self.add_pair("B", "A", 240, 500)

        result = optimize_itinerary(self.start, [self.a, self.b], self.matrix)

        self.assertEqual(("B", "A"), result.ordered_stops)
        self.assertEqual(540, result.driving_duration_seconds)
        self.assertEqual((), result.legs[0].incidents)

    def test_preserves_incidents_and_geometry_in_serializable_result(self) -> None:
        incident = TrafficIncident("incident-2", "accident", "major", "Choque")
        self.matrix.add_estimate(
            "base",
            "A",
            TravelEstimate(
                300,
                800,
                incidents=(incident,),
                geometry=((-8.11, -79.03), (-8.10, -79.02)),
            ),
        )

        result = optimize_itinerary(self.start, [self.a], self.matrix)
        payload = result.to_dict()

        self.assertEqual("A", payload["ordered_stops"][0])
        self.assertEqual("accident", payload["legs"][0]["incidents"][0]["kind"])
        self.assertEqual([-8.11, -79.03], payload["legs"][0]["geometry"][0])

    def test_can_return_to_start_and_counts_the_return_leg(self) -> None:
        self.add_pair("base", "A", 10, 100)
        self.add_pair("A", "base", 20, 200)

        result = optimize_itinerary(
            self.start, [self.a], self.matrix, return_to_start=True
        )

        self.assertEqual(("base", "A", "base"), result.path)
        self.assertEqual(30, result.driving_duration_seconds)
        self.assertEqual(90, result.total_duration_seconds)
        self.assertEqual(300, result.total_distance_meters)

    def test_reports_when_no_complete_route_exists(self) -> None:
        self.add_pair("base", "A", 10, 100)

        with self.assertRaises(NoFeasibleRouteError):
            optimize_itinerary(self.start, [self.a, self.b], self.matrix)

    def test_uses_documented_approximation_above_exact_limit(self) -> None:
        self.add_pair("base", "A", 1, 1)
        self.add_pair("base", "B", 2, 2)
        self.add_pair("A", "B", 2, 2)
        self.add_pair("B", "A", 1, 1)

        result = optimize_itinerary(
            self.start, [self.a, self.b], self.matrix, exact_limit=1
        )

        self.assertEqual("nearest-neighbor-2-opt", result.algorithm)
        self.assertEqual({"A", "B"}, set(result.ordered_stops))

    def test_empty_route_has_zero_cost(self) -> None:
        result = optimize_itinerary(self.start, [], self.matrix)

        self.assertEqual(("base",), result.path)
        self.assertEqual(0, result.total_duration_seconds)
        self.assertEqual((), result.legs)


class GoogleRoutesSafetyTests(unittest.TestCase):
    def test_adapter_is_inactive_and_never_makes_a_request(self) -> None:
        adapter = GoogleRoutesAdapter()
        with self.assertRaises(GoogleRoutesIntegrationPending):
            adapter.build_matrix([RouteStop("base", -8.11, -79.03)])


if __name__ == "__main__":
    unittest.main()
