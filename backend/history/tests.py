from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from clients.models import Client
from history.models import TicketHistory
from specialists.models import Specialist
from technicians.models import Technician
from tickets.models import Ticket
from visits.models import Visit

User = get_user_model()


class TicketHistoryApiTests(APITestCase):
	def setUp(self):
		self.admin = User.objects.create_user(
			username="historyadmin",
			password="Password123",
			role=User.Role.ADMINISTRADOR,
		)
		self.client_user = User.objects.create_user(
			username="historyclient",
			password="Password123",
			role=User.Role.CLIENTE,
		)
		self.other_client_user = User.objects.create_user(
			username="otherhistoryclient",
			password="Password123",
			role=User.Role.CLIENTE,
		)
		self.specialist_user = User.objects.create_user(
			username="historyspecialist",
			password="Password123",
			role=User.Role.ESPECIALISTA,
		)
		self.technician_user = User.objects.create_user(
			username="historytechnician",
			password="Password123",
			role=User.Role.TECNICO,
		)
		self.client_profile = Client.objects.create(
			user=self.client_user,
			nombres="Cliente",
			apellidos="Historia",
			documento="hist-001",
			telefono="111111111",
		)
		self.other_client_profile = Client.objects.create(
			user=self.other_client_user,
			nombres="Otro",
			apellidos="Cliente",
			documento="hist-002",
			telefono="222222222",
		)
		self.specialist = Specialist.objects.create(user=self.specialist_user, especialidad="Redes")
		self.technician = Technician.objects.create(user=self.technician_user, especialidad="Fibra")
		self.ticket = Ticket.objects.create(
			client=self.client_profile,
			specialist=self.specialist,
			technician=self.technician,
			titulo="Falla de conexión",
			descripcion="Sin servicio",
			estado=Ticket.Status.NUEVO,
		)
		self.other_ticket = Ticket.objects.create(
			client=self.other_client_profile,
			titulo="Falla ajena",
			descripcion="Otro cliente",
			estado=Ticket.Status.NUEVO,
		)

	def _history(self, ticket, actor=None):
		return TicketHistory.objects.create(
			ticket=ticket,
			user=actor or self.admin,
			estado_anterior=Ticket.Status.NUEVO,
			estado_nuevo=Ticket.Status.EN_REVISION,
		)

	def test_valid_status_change_creates_history_with_actor_and_states(self):
		self.client.force_authenticate(user=self.admin)
		response = self.client.patch(
			reverse("ticket-detail", args=[self.ticket.pk]),
			{"estado": Ticket.Status.EN_REVISION},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		history = TicketHistory.objects.get(ticket=self.ticket)
		self.assertEqual(history.user, self.admin)
		self.assertEqual(history.estado_anterior, Ticket.Status.NUEVO)
		self.assertEqual(history.estado_nuevo, Ticket.Status.EN_REVISION)
		self.assertIsNotNone(history.fecha)

	def test_invalid_transition_does_not_create_history(self):
		self.client.force_authenticate(user=self.admin)
		response = self.client.patch(
			reverse("ticket-detail", args=[self.ticket.pk]),
			{"estado": Ticket.Status.CERRADO},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertFalse(TicketHistory.objects.filter(ticket=self.ticket).exists())

	def test_non_status_update_does_not_create_history(self):
		self.client.force_authenticate(user=self.admin)
		response = self.client.patch(
			reverse("ticket-detail", args=[self.ticket.pk]),
			{"titulo": "Descripción actualizada"},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertFalse(TicketHistory.objects.filter(ticket=self.ticket).exists())

	def test_client_can_read_only_own_ticket_history(self):
		own_history = self._history(self.ticket)
		other_history = self._history(self.other_ticket)
		self.client.force_authenticate(user=self.client_user)

		list_response = self.client.get(reverse("history-list"))
		own_detail_response = self.client.get(reverse("history-detail", args=[own_history.pk]))
		other_detail_response = self.client.get(reverse("history-detail", args=[other_history.pk]))

		self.assertEqual(list_response.status_code, status.HTTP_200_OK)
		self.assertEqual([entry["id"] for entry in list_response.data], [own_history.pk])
		self.assertEqual(own_detail_response.status_code, status.HTTP_200_OK)
		self.assertEqual(other_detail_response.status_code, status.HTTP_404_NOT_FOUND)

	def test_specialist_can_read_history_of_assigned_ticket(self):
		history = self._history(self.ticket)
		self.client.force_authenticate(user=self.specialist_user)
		response = self.client.get(reverse("history-detail", args=[history.pk]))

		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_technician_can_read_history_of_ticket_related_to_visit(self):
		ticket = Ticket.objects.create(
			client=self.other_client_profile,
			titulo="Visita técnica",
			descripcion="Atención de campo",
			estado=Ticket.Status.TECNICO_ASIGNADO,
		)
		Visit.objects.create(
			ticket=ticket,
			technician=self.technician,
			fecha_programada=timezone.now() + timedelta(days=1),
		)
		history = self._history(ticket)
		self.client.force_authenticate(user=self.technician_user)
		response = self.client.get(reverse("history-detail", args=[history.pk]))

		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_history_api_is_read_only(self):
		history = self._history(self.ticket)
		self.client.force_authenticate(user=self.client_user)
		list_url = reverse("history-list")
		detail_url = reverse("history-detail", args=[history.pk])

		create_response = self.client.post(
			list_url,
			{"ticket": self.ticket.pk, "estado_nuevo": Ticket.Status.CERRADO},
			format="json",
		)
		update_response = self.client.patch(detail_url, {"comentario": "Modificado"}, format="json")
		delete_response = self.client.delete(detail_url)

		self.assertEqual(create_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
		self.assertEqual(update_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
		self.assertEqual(delete_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

	def test_admin_can_list_all_history(self):
		self._history(self.ticket)
		self._history(self.other_ticket)
		self.client.force_authenticate(user=self.admin)
		response = self.client.get(reverse("history-list"))

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 2)
