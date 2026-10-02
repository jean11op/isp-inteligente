from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from clients.models import Client
from technicians.models import Technician
from tickets.models import Ticket
from .models import Visit

User = get_user_model()


class VisitApiTests(APITestCase):
	def setUp(self):
		self.admin = User.objects.create_user(
			username="visitadmin",
			password="Password123",
			role=User.Role.ADMINISTRADOR,
		)
		self.client_user = User.objects.create_user(
			username="visitclient",
			password="Password123",
			role=User.Role.CLIENTE,
		)
		self.other_client_user = User.objects.create_user(
			username="othervisitclient",
			password="Password123",
			role=User.Role.CLIENTE,
		)
		self.technician_user = User.objects.create_user(
			username="visittechnician",
			password="Password123",
			role=User.Role.TECNICO,
		)
		self.other_technician_user = User.objects.create_user(
			username="othervisittech",
			password="Password123",
			role=User.Role.TECNICO,
		)
		self.client_profile = Client.objects.create(
			user=self.client_user,
			nombres="Cliente",
			apellidos="Uno",
			documento="visit-001",
			telefono="111111111",
		)
		self.other_client_profile = Client.objects.create(
			user=self.other_client_user,
			nombres="Cliente",
			apellidos="Dos",
			documento="visit-002",
			telefono="222222222",
		)
		self.technician = Technician.objects.create(
			user=self.technician_user,
			especialidad="Fibra",
		)
		self.other_technician = Technician.objects.create(
			user=self.other_technician_user,
			especialidad="Redes",
		)
		self.ticket = self._create_assigned_ticket(self.client_profile, self.technician)
		self.other_ticket = self._create_assigned_ticket(self.other_client_profile, self.other_technician)
		self.visit = self._create_visit(self.ticket, self.technician)
		self.other_visit = self._create_visit(self.other_ticket, self.other_technician)

	def _create_assigned_ticket(self, client, technician):
		return Ticket.objects.create(
			client=client,
			technician=technician,
			titulo="Falla de servicio",
			descripcion="Sin conexión",
			estado=Ticket.Status.TECNICO_ASIGNADO,
		)

	def _create_visit(self, ticket, technician):
		return Visit.objects.create(
			ticket=ticket,
			technician=technician,
			fecha_programada=timezone.now() + timedelta(days=1),
		)

	def _visit_payload(self, ticket=None, technician=None):
		return {
			"ticket": (ticket or self.ticket).pk,
			"technician": (technician or self.technician).pk,
			"fecha_programada": (timezone.now() + timedelta(days=2)).isoformat(),
		}

	def test_admin_can_create_valid_visit(self):
		self.client.force_authenticate(user=self.admin)
		response = self.client.post(reverse("visit-list-create"), self._visit_payload(), format="json")

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(response.data["estado"], Visit.Status.PROGRAMADA)
		self.assertEqual(Visit.objects.filter(ticket=self.ticket).count(), 2)

	def test_client_cannot_create_visit(self):
		self.client.force_authenticate(user=self.client_user)
		response = self.client.post(reverse("visit-list-create"), self._visit_payload(), format="json")

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_technician_can_read_and_update_own_visit(self):
		self.client.force_authenticate(user=self.technician_user)
		detail_url = reverse("visit-detail", args=[self.visit.pk])
		get_response = self.client.get(detail_url)
		patch_response = self.client.patch(detail_url, {"estado": Visit.Status.EN_CAMINO}, format="json")

		self.assertEqual(get_response.status_code, status.HTTP_200_OK)
		self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
		self.visit.refresh_from_db()
		self.assertEqual(self.visit.estado, Visit.Status.EN_CAMINO)
		self.assertIsNotNone(self.visit.fecha_inicio)

	def test_technician_cannot_modify_other_technicians_visit(self):
		self.client.force_authenticate(user=self.technician_user)
		response = self.client.patch(
			reverse("visit-detail", args=[self.other_visit.pk]),
			{"estado": Visit.Status.EN_CAMINO},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

	def test_visit_creation_rejects_invalid_inactive_or_unavailable_technician(self):
		invalid_role_user = User.objects.create_user(
			username="visitwrongrole",
			password="Password123",
			role=User.Role.CLIENTE,
		)
		invalid_role_technician = Technician.objects.create(
			user=invalid_role_user,
			especialidad="Perfil inválido",
		)
		self.client.force_authenticate(user=self.admin)

		invalid_role_response = self.client.post(
			reverse("visit-list-create"),
			self._visit_payload(technician=invalid_role_technician),
			format="json",
		)
		self.technician.activo = False
		self.technician.save(update_fields=["activo"])
		inactive_response = self.client.post(
			reverse("visit-list-create"),
			self._visit_payload(),
			format="json",
		)
		self.technician.activo = True
		self.technician.disponible = False
		self.technician.save(update_fields=["activo", "disponible"])
		unavailable_response = self.client.post(
			reverse("visit-list-create"),
			self._visit_payload(),
			format="json",
		)

		self.assertEqual(invalid_role_response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(inactive_response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(unavailable_response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_visit_accepts_valid_transitions_and_programmed_cancellation(self):
		self.client.force_authenticate(user=self.technician_user)
		detail_url = reverse("visit-detail", args=[self.visit.pk])
		for next_status in (
			Visit.Status.EN_CAMINO,
			Visit.Status.EN_DOMICILIO,
			Visit.Status.EN_ATENCION,
			Visit.Status.COMPLETADA,
		):
			response = self.client.patch(detail_url, {"estado": next_status}, format="json")
			self.assertEqual(response.status_code, status.HTTP_200_OK)

		second_visit = self._create_visit(self.ticket, self.technician)
		cancellation_response = self.client.patch(
			reverse("visit-detail", args=[second_visit.pk]),
			{"estado": Visit.Status.CANCELADA},
			format="json",
		)
		self.assertEqual(cancellation_response.status_code, status.HTTP_200_OK)
		second_visit.refresh_from_db()
		self.assertIsNotNone(second_visit.fecha_fin)

	def test_visit_rejects_invalid_transition(self):
		self.client.force_authenticate(user=self.technician_user)
		response = self.client.patch(
			reverse("visit-detail", args=[self.visit.pk]),
			{"estado": Visit.Status.COMPLETADA},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.visit.refresh_from_db()
		self.assertEqual(self.visit.estado, Visit.Status.PROGRAMADA)

	def test_client_only_lists_visits_for_own_tickets(self):
		self.client.force_authenticate(user=self.client_user)
		response = self.client.get(reverse("visit-list-create"))

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual([item["id"] for item in response.data], [self.visit.pk])
