from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from clients.models import Client
from evaluations.models import Evaluation
from tickets.models import Ticket

User = get_user_model()


class EvaluationApiTests(APITestCase):
	def setUp(self):
		self.admin = User.objects.create_user(
			username="evaluationadmin",
			password="Password123",
			role=User.Role.ADMINISTRADOR,
		)
		self.client_user = User.objects.create_user(
			username="evaluationclient",
			password="Password123",
			role=User.Role.CLIENTE,
		)
		self.other_client_user = User.objects.create_user(
			username="otherevaluationclient",
			password="Password123",
			role=User.Role.CLIENTE,
		)
		self.specialist_user = User.objects.create_user(
			username="evaluationspecialist",
			password="Password123",
			role=User.Role.ESPECIALISTA,
		)
		self.technician_user = User.objects.create_user(
			username="evaluationtechnician",
			password="Password123",
			role=User.Role.TECNICO,
		)
		self.client_profile = Client.objects.create(
			user=self.client_user,
			nombres="Cliente",
			apellidos="Evaluación",
			documento="eval-001",
			telefono="111111111",
		)
		self.other_client_profile = Client.objects.create(
			user=self.other_client_user,
			nombres="Otro",
			apellidos="Cliente",
			documento="eval-002",
			telefono="222222222",
		)
		self.ticket = self._create_ticket(self.client_profile, Ticket.Status.RESUELTO, "Evaluable")
		self.other_ticket = self._create_ticket(self.other_client_profile, Ticket.Status.CERRADO, "Ajeno")

	def _create_ticket(self, client_profile, state, title):
		return Ticket.objects.create(
			client=client_profile,
			titulo=title,
			descripcion="Incidencia completada",
			estado=state,
		)

	def test_admin_can_list_and_manage_evaluations(self):
		evaluation = Evaluation.objects.create(ticket=self.ticket, puntuacion=4)
		self.client.force_authenticate(user=self.admin)
		list_response = self.client.get(reverse("evaluation-list-create"))
		update_response = self.client.patch(
			reverse("evaluation-detail", args=[evaluation.pk]),
			{"puntuacion": 5},
			format="json",
		)

		self.assertEqual(list_response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(list_response.data), 1)
		self.assertEqual(update_response.status_code, status.HTTP_200_OK)

	def test_client_can_evaluate_own_resolved_ticket(self):
		self.client.force_authenticate(user=self.client_user)
		response = self.client.post(
			reverse("evaluation-list-create"),
			{
				"ticket": self.ticket.pk,
				"puntuacion": 5,
				"comentario": "Atención excelente.",
				"fecha_evaluacion": "2000-01-01T00:00:00Z",
			},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		evaluation = Evaluation.objects.get(ticket=self.ticket)
		self.assertEqual(evaluation.puntuacion, 5)
		self.assertIsNotNone(evaluation.fecha_evaluacion)
		self.assertGreater(evaluation.fecha_evaluacion.year, 2000)

	def test_client_cannot_evaluate_another_clients_ticket(self):
		self.client.force_authenticate(user=self.client_user)
		response = self.client.post(
			reverse("evaluation-list-create"),
			{"ticket": self.other_ticket.pk, "puntuacion": 4},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
		self.assertFalse(Evaluation.objects.filter(ticket=self.other_ticket).exists())

	def test_client_cannot_evaluate_unresolved_ticket(self):
		unresolved_ticket = self._create_ticket(self.client_profile, Ticket.Status.EN_ATENCION, "Aún abierto")
		self.client.force_authenticate(user=self.client_user)
		response = self.client.post(
			reverse("evaluation-list-create"),
			{"ticket": unresolved_ticket.pk, "puntuacion": 3},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertFalse(Evaluation.objects.filter(ticket=unresolved_ticket).exists())

	def test_client_cannot_evaluate_ticket_twice(self):
		Evaluation.objects.create(ticket=self.ticket, puntuacion=4)
		self.client.force_authenticate(user=self.client_user)
		response = self.client.post(
			reverse("evaluation-list-create"),
			{"ticket": self.ticket.pk, "puntuacion": 5},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(Evaluation.objects.filter(ticket=self.ticket).count(), 1)

	def test_client_rejects_scores_outside_one_to_five(self):
		self.client.force_authenticate(user=self.client_user)
		for score in (0, 6):
			with self.subTest(score=score):
				response = self.client.post(
					reverse("evaluation-list-create"),
					{"ticket": self.ticket.pk, "puntuacion": score},
					format="json",
				)
				self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertFalse(Evaluation.objects.filter(ticket=self.ticket).exists())

	def test_client_cannot_update_or_delete_own_evaluation(self):
		evaluation = Evaluation.objects.create(ticket=self.ticket, puntuacion=4)
		self.client.force_authenticate(user=self.client_user)
		detail_url = reverse("evaluation-detail", args=[evaluation.pk])
		update_response = self.client.patch(detail_url, {"puntuacion": 1}, format="json")
		delete_response = self.client.delete(detail_url)

		self.assertEqual(update_response.status_code, status.HTTP_403_FORBIDDEN)
		self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)
		self.assertTrue(Evaluation.objects.filter(pk=evaluation.pk).exists())

	def test_specialist_and_technician_cannot_create_evaluations(self):
		for user in (self.specialist_user, self.technician_user):
			with self.subTest(role=user.role):
				self.client.force_authenticate(user=user)
				response = self.client.post(
					reverse("evaluation-list-create"),
					{"ticket": self.ticket.pk, "puntuacion": 5},
					format="json",
				)
				self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

def test_client_cannot_view_another_clients_evaluation(self):
        evaluation = Evaluation.objects.create(
            ticket=self.other_ticket,
            puntuacion=4,
        )

        self.client.force_authenticate(user=self.client_user)

        response = self.client.get(
            reverse("evaluation-detail", args=[evaluation.pk])
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)