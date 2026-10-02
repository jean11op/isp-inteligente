import unittest

from algorithms.assignment import (
    AssignmentPolicy,
    ScoreWeights,
    TechnicianCandidate,
    score_technicians,
    select_technician,
)


class TechnicianSelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.candidates = [
            TechnicianCandidate(1, "Fibra Óptica", True, True, 2, -8.11, -79.03),
            TechnicianCandidate(2, "Fibra optica", True, True, 0, -8.12, -79.04),
            TechnicianCandidate(3, "Fibra Óptica", False, True, 0, -8.10, -79.02),
            TechnicianCandidate(4, "Radio", True, True, 0, -8.10, -79.02),
        ]

    def test_filters_and_ranks_by_configured_priority_weights(self) -> None:
        policy = AssignmentPolicy(
            weights_by_priority={"ALTA": ScoreWeights(distance=1, workload=0)}
        )

        ranked = score_technicians(
            self.candidates,
            required_specialty="fibra optica",
            destination_latitude=-8.11,
            destination_longitude=-79.03,
            ticket_priority="ALTA",
            policy=policy,
        )

        self.assertEqual([1, 2], [item.candidate.technician_id for item in ranked])
        self.assertEqual(1, select_technician(
            self.candidates,
            required_specialty="fibra optica",
            destination_latitude=-8.11,
            destination_longitude=-79.03,
            ticket_priority="ALTA",
            policy=policy,
        ).candidate.technician_id)

    def test_weight_policy_rejects_all_zero_weights(self) -> None:
        with self.assertRaises(ValueError):
            ScoreWeights(distance=0, workload=0)


if __name__ == "__main__":
    unittest.main()
