from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from clients.models import Client
from specialists.models import Specialist
from technicians.models import Technician
from tickets.models import Ticket

User = get_user_model()


class AuthAndPermissionTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="Password123",
            role=User.Role.ADMINISTRADOR,
        )

        self.client_user = User.objects.create_user(
            username="cliente1",
            email="cliente1@example.com",
            password="Password123",
            role=User.Role.CLIENTE,
        )
        self.other_client_user = User.objects.create_user(
            username="cliente2",
            email="cliente2@example.com",
            password="Password123",
            role=User.Role.CLIENTE,
        )

        self.client_profile = Client.objects.create(
            user=self.client_user,
            nombres="Cliente",
            apellidos="Uno",
            documento="11111111",
            telefono="123456789",
        )
        self.other_client_profile = Client.objects.create(
            user=self.other_client_user,
            nombres="Cliente",
            apellidos="Dos",
            documento="22222222",
            telefono="987654321",
        )

        self.ticket = Ticket.objects.create(
            client=self.client_profile,
            titulo="Fallo de conexión",
            descripcion="Sin internet",
            prioridad=Ticket.Priority.MEDIA,
            estado=Ticket.Status.NUEVO,
        )

        self.other_ticket = Ticket.objects.create(
            client=self.other_client_profile,
            titulo="Otro fallo",
            descripcion="Otro problema",
            prioridad=Ticket.Priority.MEDIA,
            estado=Ticket.Status.NUEVO,
        )

        self.specialist_user = User.objects.create_user(
            username="especialista1",
            email="especialista1@example.com",
            password="Password123",
            role=User.Role.ESPECIALISTA,
        )
        self.specialist = Specialist.objects.create(
            user=self.specialist_user,
            especialidad="Redes",
        )
        self.ticket.specialist = self.specialist
        self.ticket.save()

        self.technician_user = User.objects.create_user(
            username="tecnico1",
            email="tecnico1@example.com",
            password="Password123",
            role=User.Role.TECNICO,
        )
        self.technician = Technician.objects.create(
            user=self.technician_user,
            especialidad="Fibra",
        )
        self.ticket.technician = self.technician
        self.ticket.save()

    def test_login_jwt_valid(self):
        url = reverse("token-obtain-pair")
        response = self.client.post(
            url,
            {"username": "cliente1", "password": "Password123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_jwt_invalid(self):
        url = reverse("token-obtain-pair")
        response = self.client.post(
            url,
            {"username": "cliente1", "password": "WrongPassword"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_endpoint_requires_auth(self):
        url = reverse("user-list-create")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_detail_requires_auth(self):
        response = self.client.get(reverse("user-detail", args=[self.client_user.pk]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_client_detail_requires_auth(self):
        response = self.client.get(reverse("client-detail", args=[self.client_profile.pk]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ticket_detail_requires_auth(self):
        response = self.client.get(reverse("ticket-detail", args=[self.ticket.pk]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_can_access_users(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse("user-list-create"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_client_can_access_own_profile_but_not_other_profile(self):
        self.client.force_authenticate(user=self.client_user)

        own_response = self.client.get(reverse("user-detail", args=[self.client_user.pk]))
        other_response = self.client.get(reverse("user-detail", args=[self.other_client_user.pk]))

        self.assertEqual(own_response.status_code, status.HTTP_200_OK)
        self.assertEqual(other_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_client_cannot_access_other_client_ticket(self):
        self.client.force_authenticate(user=self.client_user)
        response = self.client.get(reverse("ticket-detail", args=[self.other_ticket.pk]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_password_is_hashed_on_update(self):
        payload = {"password": "NewPass123"}
        response = self.client.patch(
            reverse("user-detail", args=[self.client_user.pk]),
            payload,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self._get_token(self.client_user)}",
        )

        self.client_user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.client_user.check_password("NewPass123"))
        self.assertNotIn("password", response.data)

    def test_client_cannot_change_its_role_to_admin(self):
        self.client.force_authenticate(user=self.client_user)
        response = self.client.patch(
            reverse("user-detail", args=[self.client_user.pk]),
            {"role": User.Role.ADMINISTRADOR},
            format="json",
        )

        self.client_user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client_user.role, User.Role.CLIENTE)

    def test_related_specialist_cannot_patch_ticket_by_relation(self):
        self.client.force_authenticate(user=self.specialist_user)
        response = self.client.patch(
            reverse("ticket-detail", args=[self.ticket.pk]),
            {"solucion": "Se revisó"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_related_technician_cannot_delete_ticket_by_relation(self):
        self.client.force_authenticate(user=self.technician_user)
        response = self.client.delete(reverse("ticket-detail", args=[self.ticket.pk]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_client_cannot_reassign_client_user_relationship(self):
        self.client.force_authenticate(user=self.client_user)
        response = self.client.patch(
            reverse("client-detail", args=[self.client_profile.pk]),
            {"user": self.other_client_user.pk},
            format="json",
        )

        self.client_profile.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client_profile.user, self.client_user)

    def test_client_cannot_patch_or_delete_other_ticket(self):
        self.client.force_authenticate(user=self.client_user)

        patch_response = self.client.patch(
            reverse("ticket-detail", args=[self.other_ticket.pk]),
            {"descripcion": "No autorizado"},
            format="json",
        )
        delete_response = self.client.delete(reverse("ticket-detail", args=[self.other_ticket.pk]))

        self.assertEqual(patch_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)

    def _get_token(self, user):
        response = self.client.post(
            reverse("token-obtain-pair"),
            {"username": user.username, "password": "Password123"},
            format="json",
        )
        return response.data["access"]
