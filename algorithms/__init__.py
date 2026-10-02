"""Algoritmos independientes para ISP Inteligente.

El paquete no accede a Django ni a PostgreSQL. El backend entrega los datos
necesarios, consume los resultados y persiste las decisiones.
"""

from .diagnosis import DiagnosisReport, ISPDiagnosticEngine
from .route_planning import (
    ItineraryResult,
    NoFeasibleRouteError,
    RouteStop,
    TrafficIncident,
    TravelEstimate,
    TravelMatrix,
    optimize_itinerary,
)

__all__ = [
    "DiagnosisReport",
    "ISPDiagnosticEngine",
    "ItineraryResult",
    "NoFeasibleRouteError",
    "RouteStop",
    "TrafficIncident",
    "TravelEstimate",
    "TravelMatrix",
    "optimize_itinerary",
]
