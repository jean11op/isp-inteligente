"""Diagnóstico por reglas para CU-40."""

from .inference import BackwardResult, ForwardResult, KnowledgeBase, Rule
from .isp import DiagnosisReport, ISPDiagnosticEngine, default_isp_rules

__all__ = [
    "BackwardResult",
    "DiagnosisReport",
    "ForwardResult",
    "ISPDiagnosticEngine",
    "KnowledgeBase",
    "Rule",
    "default_isp_rules",
]
