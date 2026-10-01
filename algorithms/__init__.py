"""Algoritmos independientes para ISP Inteligente.

El paquete no accede a Django ni a PostgreSQL. El backend entrega los datos
necesarios, consume los resultados y persiste las decisiones.
"""

from .diagnosis import DiagnosisReport, ISPDiagnosticEngine

__all__ = ["DiagnosisReport", "ISPDiagnosticEngine"]
