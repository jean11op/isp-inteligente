"""Optimización pura del orden de visitas a partir de una matriz de viajes.

Se minimiza el tiempo estimado de conducción (incluido el tráfico que informe
la matriz); la distancia sirve como desempate. Los tramos bloqueados no se usan.
Para jornadas pequeñas Held-Karp encuentra el óptimo global. Para más visitas
se usa vecino más cercano con mejora 2-opt y se informa que es aproximado.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeAlias

from .models import ItineraryResult, PlannedLeg, RouteStop, TravelEstimate, TravelMatrix

_Score: TypeAlias = tuple[float, float, tuple[str, ...]]


class NoFeasibleRouteError(ValueError):
    """No existe una secuencia que conecte el inicio con todas las visitas."""


def optimize_itinerary(
    start: RouteStop,
    stops: Sequence[RouteStop],
    matrix: TravelMatrix,
    *,
    return_to_start: bool = False,
    exact_limit: int = 12,
) -> ItineraryResult:
    """Ordena todas las visitas minimizando ETA y luego distancia.

    `matrix` debe contener estimaciones dirigidas para la hora de salida elegida.
    Para recalcular tras una visita, el llamador pasa la nueva ubicación, las
    visitas pendientes y una matriz actualizada. Esta función nunca llama APIs.
    """
    if not isinstance(exact_limit, int) or exact_limit < 1:
        raise ValueError("exact_limit debe ser un entero positivo.")
    if exact_limit > 16:
        raise ValueError("exact_limit no puede superar 16 por costo de memoria y cómputo.")

    stop_ids = [stop.stop_id for stop in stops]
    if start.stop_id in stop_ids:
        raise ValueError("El punto inicial no puede repetirse como visita.")
    if len(set(stop_ids)) != len(stop_ids):
        raise ValueError("Las visitas deben tener identificadores únicos.")

    expected_ids = {start.stop_id, *stop_ids}
    if not expected_ids.issubset(matrix.stop_ids):
        missing = sorted(expected_ids - matrix.stop_ids)
        raise ValueError(f"Faltan ubicaciones en la matriz: {missing}.")

    if not stops:
        return ItineraryResult(
            path=(start.stop_id,),
            legs=(),
            driving_duration_seconds=0.0,
            service_duration_seconds=0.0,
            total_duration_seconds=0.0,
            total_distance_meters=0.0,
            algorithm="held-karp",
            departure_time=matrix.departure_time,
        )

    ordered = tuple(stops)
    if len(ordered) <= exact_limit:
        order = _held_karp(start, ordered, matrix, return_to_start)
        algorithm = "held-karp"
    else:
        order = _nearest_neighbor_two_opt(start, ordered, matrix, return_to_start)
        algorithm = "nearest-neighbor-2-opt"

    path_ids = (start.stop_id, *(stop.stop_id for stop in order))
    if return_to_start:
        path_ids = (*path_ids, start.stop_id)
    legs = _build_legs(path_ids, matrix)
    driving = sum(leg.duration_seconds for leg in legs)
    distance = sum(leg.distance_meters for leg in legs)
    service = sum(stop.service_duration_seconds for stop in ordered)

    return ItineraryResult(
        path=path_ids,
        legs=legs,
        driving_duration_seconds=driving,
        service_duration_seconds=service,
        total_duration_seconds=driving + service,
        total_distance_meters=distance,
        algorithm=algorithm,
        departure_time=matrix.departure_time,
    )


def _estimate(
    origin_id: str,
    destination_id: str,
    matrix: TravelMatrix,
) -> TravelEstimate | None:
    return matrix.estimate(origin_id, destination_id)


def _held_karp(
    start: RouteStop,
    stops: tuple[RouteStop, ...],
    matrix: TravelMatrix,
    return_to_start: bool,
) -> tuple[RouteStop, ...]:
    # Estado: (máscara de visitas, último índice) -> tiempo, distancia, secuencia.
    states: dict[tuple[int, int], tuple[float, float, tuple[int, ...]]] = {}
    for index, stop in enumerate(stops):
        estimate = _estimate(start.stop_id, stop.stop_id, matrix)
        if estimate is not None:
            states[(1 << index, index)] = (
                estimate.duration_seconds or 0.0,
                estimate.distance_meters or 0.0,
                (index,),
            )

    full_mask = (1 << len(stops)) - 1
    for mask in range(1, full_mask + 1):
        for last in range(len(stops)):
            state = states.get((mask, last))
            if state is None:
                continue
            duration, distance, order = state
            for next_index, next_stop in enumerate(stops):
                bit = 1 << next_index
                if mask & bit:
                    continue
                estimate = _estimate(stops[last].stop_id, next_stop.stop_id, matrix)
                if estimate is None:
                    continue
                candidate = (
                    duration + (estimate.duration_seconds or 0.0),
                    distance + (estimate.distance_meters or 0.0),
                    (*order, next_index),
                )
                key = (mask | bit, next_index)
                incumbent = states.get(key)
                if incumbent is None or _state_score(candidate, stops) < _state_score(
                    incumbent, stops
                ):
                    states[key] = candidate

    candidates: list[tuple[float, float, tuple[int, ...]]] = []
    for last, stop in enumerate(stops):
        state = states.get((full_mask, last))
        if state is None:
            continue
        duration, distance, order = state
        if return_to_start:
            final_leg = _estimate(stop.stop_id, start.stop_id, matrix)
            if final_leg is None:
                continue
            duration += final_leg.duration_seconds or 0.0
            distance += final_leg.distance_meters or 0.0
        candidates.append((duration, distance, order))

    if not candidates:
        suffix = " y volver al inicio" if return_to_start else ""
        raise NoFeasibleRouteError(
            f"No hay una ruta transitable que cubra todas las visitas{suffix}."
        )
    best = min(candidates, key=lambda item: _state_score(item, stops))
    return tuple(stops[index] for index in best[2])


def _state_score(
    state: tuple[float, float, tuple[int, ...]],
    stops: tuple[RouteStop, ...],
) -> _Score:
    duration, distance, order = state
    return duration, distance, tuple(stops[index].stop_id for index in order)


def _nearest_neighbor_two_opt(
    start: RouteStop,
    stops: tuple[RouteStop, ...],
    matrix: TravelMatrix,
    return_to_start: bool,
) -> tuple[RouteStop, ...]:
    remaining = {stop.stop_id: stop for stop in stops}
    order: list[RouteStop] = []
    current_id = start.stop_id
    while remaining:
        options: list[tuple[float, float, str, RouteStop]] = []
        for stop in remaining.values():
            estimate = _estimate(current_id, stop.stop_id, matrix)
            if estimate is not None:
                options.append(
                    (
                        estimate.duration_seconds or 0.0,
                        estimate.distance_meters or 0.0,
                        stop.stop_id,
                        stop,
                    )
                )
        if not options:
            raise NoFeasibleRouteError(
                f"No hay un tramo transitable desde {current_id!r} "
                "hacia las visitas pendientes."
            )
        next_stop = min(options, key=lambda option: option[:3])[3]
        order.append(next_stop)
        del remaining[next_stop.stop_id]
        current_id = next_stop.stop_id

    improved = True
    while improved:
        improved = False
        current_score = _path_score(start, tuple(order), matrix, return_to_start)
        best_order = tuple(order)
        best_score = current_score
        for left in range(len(order) - 1):
            for right in range(left + 1, len(order)):
                candidate = tuple(
                    (*order[:left], *reversed(order[left : right + 1]), *order[right + 1 :])
                )
                try:
                    score = _path_score(start, candidate, matrix, return_to_start)
                except NoFeasibleRouteError:
                    continue
                if score < best_score:
                    best_order, best_score = candidate, score
        if best_score < current_score:
            order = list(best_order)
            improved = True
    return tuple(order)


def _path_score(
    start: RouteStop,
    order: tuple[RouteStop, ...],
    matrix: TravelMatrix,
    return_to_start: bool,
) -> _Score:
    path = [start.stop_id, *(stop.stop_id for stop in order)]
    if return_to_start:
        path.append(start.stop_id)
    duration = 0.0
    distance = 0.0
    for origin_id, destination_id in zip(path, path[1:]):
        estimate = _estimate(origin_id, destination_id, matrix)
        if estimate is None:
            raise NoFeasibleRouteError("La secuencia contiene un tramo bloqueado o ausente.")
        duration += estimate.duration_seconds or 0.0
        distance += estimate.distance_meters or 0.0
    return duration, distance, tuple(stop.stop_id for stop in order)


def _build_legs(path: tuple[str, ...], matrix: TravelMatrix) -> tuple[PlannedLeg, ...]:
    legs: list[PlannedLeg] = []
    for origin_id, destination_id in zip(path, path[1:]):
        estimate = _estimate(origin_id, destination_id, matrix)
        if estimate is None:
            raise NoFeasibleRouteError(
                f"El tramo {origin_id!r} → {destination_id!r} no es transitable."
            )
        legs.append(
            PlannedLeg(
                origin_id=origin_id,
                destination_id=destination_id,
                duration_seconds=estimate.duration_seconds or 0.0,
                distance_meters=estimate.distance_meters or 0.0,
                incidents=estimate.incidents,
                geometry=estimate.geometry,
            )
        )
    return tuple(legs)
