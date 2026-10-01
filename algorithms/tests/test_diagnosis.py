import unittest

from algorithms.diagnosis import ISPDiagnosticEngine, KnowledgeBase, Rule


class DiagnosisEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = ISPDiagnosticEngine()

    def test_forward_chaining_returns_diagnosis_recommendation_and_trace(self) -> None:
        report = self.engine.process({"No hay Internet", "router apagado"})

        self.assertIn("router_apagado", report.diagnoses)
        self.assertIn("encender_router", report.recommendations)
        self.assertEqual({"diagnostico:router_apagado", "recomendacion:encender_router"},
                         report.inferred_facts)
        self.assertEqual({"ISP-R1-DIAG", "ISP-R1-REC"},
                         {rule.rule_id for rule in report.fired_rules})
        self.assertEqual(2, len(report.explanation))
        response = report.to_dict()
        self.assertEqual(["router_apagado"], response["diagnoses"])
        self.assertEqual(["encender_router"], response["recommendations"])
        self.assertEqual(2, len(response["applied_rules"]))

    def test_second_and_third_network_rules(self) -> None:
        cable_report = self.engine.process({"router_encendido", "sin_conexion"})
        provider_report = self.engine.process({"cable_correcto", "sin_conexion"})

        self.assertIn("revisar_cable", cable_report.recommendations)
        self.assertIn("posible_problema_de_cableado", cable_report.diagnoses)
        self.assertIn("contactar_proveedor", provider_report.recommendations)
        self.assertIn("posible_falla_externa", provider_report.diagnoses)

    def test_no_matching_symptoms_returns_no_recommendation(self) -> None:
        report = self.engine.process({"servicio_funciona"})

        self.assertFalse(report.diagnoses)
        self.assertFalse(report.recommendations)
        self.assertFalse(report.fired_rules)

    def test_backward_chaining_proves_goal_from_observed_facts(self) -> None:
        result = self.engine.verify_hypothesis(
            "recomendacion:encender_router", {"no_hay_internet", "router_apagado"}
        )

        self.assertTrue(result.proven)
        self.assertEqual("recomendacion:encender_router", result.goal)
        self.assertEqual({"ISP-R1-REC"}, {rule.rule_id for rule in result.fired_rules})

    def test_backward_chaining_does_not_prove_goal_without_support(self) -> None:
        result = self.engine.verify_hypothesis(
            "recomendacion:encender_router", {"router_encendido"}
        )

        self.assertFalse(result.proven)
        self.assertFalse(result.fired_rules)

    def test_backward_chaining_stops_a_rule_cycle(self) -> None:
        knowledge = KnowledgeBase(
            [
                Rule("A-TO-B", frozenset({"b"}), "a"),
                Rule("B-TO-A", frozenset({"a"}), "b"),
            ]
        )

        result = knowledge.backward_chain("a", set())

        self.assertFalse(result.proven)
        self.assertFalse(result.fired_rules)

    def test_duplicate_rule_ids_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            KnowledgeBase(
                [
                    Rule("DUPLICATE", frozenset({"x"}), "y"),
                    Rule("DUPLICATE", frozenset({"y"}), "z"),
                ]
            )


if __name__ == "__main__":
    unittest.main()
