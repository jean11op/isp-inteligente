from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from clients.models import Address, Client
from services.models import Service
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
        self.service = Service.objects.create(
            nombre="Fibra hogar",
            descripcion="Servicio de prueba",
            velocidad_mbps=100,
            precio_mensual="25.00",
        )
        self.client_profile.service = self.service
        self.client_profile.save(update_fields=["service"])

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
        password = "S3cure-Unique-Update-846!"
        payload = {"password": password}
        response = self.client.patch(
            reverse("user-detail", args=[self.client_user.pk]),
            payload,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self._get_token(self.client_user)}",
        )

        self.client_user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.client_user.check_password(password))
        self.assertNotIn("password", response.data)

    def test_user_creation_validates_and_hashes_password(self):
        self.client.force_authenticate(user=self.admin)
        password = "S3cure-Unique-Create-947!"
        response = self.client.post(
            reverse("user-list-create"),
            {
                "username": "newclient",
                "email": "newclient@example.com",
                "password": password,
                "role": User.Role.CLIENTE,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_user = User.objects.get(username="newclient")
        self.assertTrue(created_user.check_password(password))
        self.assertNotIn("password", response.data)

    def test_user_creation_rejects_weak_password(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            reverse("user-list-create"),
            {
                "username": "weakpassclient",
                "email": "weakpass@example.com",
                "password": "123",
                "role": User.Role.CLIENTE,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_user_password_update_rejects_weak_password(self):
        self.client.force_authenticate(user=self.client_user)
        response = self.client.patch(
            reverse("user-detail", args=[self.client_user.pk]),
            {"password": "123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_admin_can_create_client_with_client_user(self):
        self.client.force_authenticate(user=self.admin)
        user = User.objects.create_user(
            username="newprofileclient",
            password="Password123",
            role=User.Role.CLIENTE,
        )
        response = self.client.post(
            reverse("client-list-create"),
            {
                "user": user.pk,
                "nombres": "Nuevo",
                "apellidos": "Cliente",
                "documento": "33333333",
                "telefono": "555555555",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_client = Client.objects.get(user=user)
        self.assertEqual(created_client.documento, "33333333")

    def test_admin_cannot_create_client_without_user(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            reverse("client-list-create"),
            {
                "nombres": "Sin",
                "apellidos": "Usuario",
                "documento": "44444444",
                "telefono": "555555556",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Client.objects.filter(documento="44444444").exists())

    def test_admin_cannot_create_second_client_for_same_user(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            reverse("client-list-create"),
            {
                "user": self.client_user.pk,
                "nombres": "Duplicado",
                "apellidos": "Cliente",
                "documento": "55555555",
                "telefono": "555555557",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Client.objects.filter(documento="55555555").exists())

    def test_client_can_create_ticket_for_own_profile(self):
        self.client.force_authenticate(user=self.client_user)
        response = self.client.post(
            reverse("ticket-list-create"),
            {
                "titulo": "Conexión intermitente",
                "descripcion": "La conexión se interrumpe varias veces al día.",
                "prioridad": Ticket.Priority.ALTA,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_ticket = Ticket.objects.get(pk=response.data["id"])
        self.assertEqual(created_ticket.client, self.client_profile)
        self.assertEqual(created_ticket.service, self.service)
        self.assertEqual(created_ticket.estado, Ticket.Status.NUEVO)

    def test_client_cannot_set_internal_ticket_fields_on_create(self):
        self.client.force_authenticate(user=self.client_user)
        internal_fields = {
            "client": self.other_client_profile.pk,
            "service": self.service.pk,
            "estado": Ticket.Status.RESUELTO,
            "diagnostico": "Diagnóstico manipulado",
            "solucion": "Solución manipulada",
            "specialist": self.specialist.pk,
            "technician": self.technician.pk,
        }

        for field, value in internal_fields.items():
            with self.subTest(field=field):
                response = self.client.post(
                    reverse("ticket-list-create"),
                    {
                        "titulo": "Solicitud",
                        "descripcion": "Reporte de prueba",
                        field: value,
                    },
                    format="json",
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.data)

    def test_client_without_profile_gets_validation_error_creating_ticket(self):
        user_without_profile = User.objects.create_user(
            username="clientwithoutprofile",
            password="Password123",
            role=User.Role.CLIENTE,
        )
        self.client.force_authenticate(user=user_without_profile)
        response = self.client.post(
            reverse("ticket-list-create"),
            {"titulo": "Sin perfil", "descripcion": "Prueba", "prioridad": Ticket.Priority.MEDIA},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("client", response.data)

    def test_delete_protected_client_returns_conflict(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(reverse("client-detail", args=[self.client_profile.pk]))

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertTrue(Client.objects.filter(pk=self.client_profile.pk).exists())

    def test_ticket_transition_new_to_in_review(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            reverse("ticket-detail", args=[self.ticket.pk]),
            {"estado": Ticket.Status.EN_REVISION},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.estado, Ticket.Status.EN_REVISION)

    def test_specialist_can_transition_to_diagnosed(self):
        self.ticket.estado = Ticket.Status.EN_REVISION
        self.ticket.save(update_fields=["estado"])
        self.client.force_authenticate(user=self.specialist_user)
        response = self.client.patch(
            reverse("ticket-detail", args=[self.ticket.pk]),
            {"estado": Ticket.Status.DIAGNOSTICADO, "diagnostico": "Enlace óptico inestable."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.estado, Ticket.Status.DIAGNOSTICADO)

    def test_admin_cannot_skip_ticket_transitions(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            reverse("ticket-detail", args=[self.ticket.pk]),
            {"estado": Ticket.Status.CERRADO},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.estado, Ticket.Status.NUEVO)

    def test_client_cannot_change_ticket_status(self):
        self.client.force_authenticate(user=self.client_user)
        response = self.client.patch(
            reverse("ticket-detail", args=[self.ticket.pk]),
            {"estado": Ticket.Status.EN_REVISION},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_client_can_confirm_resolved_ticket(self):
        self.ticket.estado = Ticket.Status.RESUELTO
        self.ticket.save(update_fields=["estado"])
        self.client.force_authenticate(user=self.client_user)

        response = self.client.patch(
            reverse("ticket-detail", args=[self.ticket.pk]),
            {"estado": Ticket.Status.CERRADO},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.estado, Ticket.Status.CERRADO)

    def test_client_cannot_confirm_unresolved_ticket(self):
        self.client.force_authenticate(user=self.client_user)

        response = self.client.patch(
            reverse("ticket-detail", args=[self.ticket.pk]),
            {"estado": Ticket.Status.CERRADO},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.estado, Ticket.Status.NUEVO)

    def test_assigned_staff_receive_read_only_client_info(self):
        self.client.force_authenticate(user=self.specialist_user)

        response = self.client.get(reverse("ticket-detail", args=[self.ticket.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["client_info"]["nombres"], "Cliente")
        self.assertEqual(response.data["client_info"]["telefono"], "123456789")

    def test_client_can_create_and_list_own_address(self):
        self.client.force_authenticate(user=self.client_user)
        payload = {
            "direccion": "Calle 1 # 2-3",
            "referencia": "Frente al parque",
            "latitud": "4.711000",
            "longitud": "-74.072000",
            "principal": True,
        }

        create_response = self.client.post(
            reverse("address-list-create"), payload, format="json"
        )
        list_response = self.client.get(reverse("address-list-create"))

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data[0]["direccion"], payload["direccion"])
        self.assertEqual(Address.objects.get().client, self.client_profile)

    def test_client_can_request_specialist(self):
        self.client.force_authenticate(user=self.client_user)

        response = self.client.post(
            reverse("ticket-request-specialist", args=[self.ticket.pk]),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ticket.refresh_from_db()
        self.assertEqual(
            self.ticket.estado,
            Ticket.Status.ESPERANDO_ESPECIALISTA,
        )

    def test_technician_can_advance_assigned_ticket(self):
        self.ticket.estado = Ticket.Status.EN_CAMINO
        self.ticket.save(update_fields=["estado"])
        self.client.force_authenticate(user=self.technician_user)
        response = self.client.patch(
            reverse("ticket-detail", args=[self.ticket.pk]),
            {"estado": Ticket.Status.EN_DOMICILIO},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.estado, Ticket.Status.EN_DOMICILIO)

    def test_technician_cannot_perform_specialist_transition(self):
        self.ticket.estado = Ticket.Status.EN_REVISION
        self.ticket.save(update_fields=["estado"])
        self.client.force_authenticate(user=self.technician_user)
        response = self.client.patch(
            reverse("ticket-detail", args=[self.ticket.pk]),
            {"estado": Ticket.Status.DIAGNOSTICADO},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_close_resolved_ticket(self):
        self.ticket.estado = Ticket.Status.RESUELTO
        self.ticket.save(update_fields=["estado"])
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            reverse("ticket-detail", args=[self.ticket.pk]),
            {"estado": Ticket.Status.CERRADO},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.estado, Ticket.Status.CERRADO)

    def test_admin_can_list_specialists(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse("specialist-list-create"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_specialist_can_view_own_profile(self):
        self.client.force_authenticate(user=self.specialist_user)
        response = self.client.get(reverse("specialist-detail", args=[self.specialist.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.specialist.pk)

    def test_specialist_cannot_modify_another_specialist(self):
        other_user = User.objects.create_user(
            username="especialista2",
            password="Password123",
            role=User.Role.ESPECIALISTA,
        )
        other_specialist = Specialist.objects.create(user=other_user, especialidad="Radioenlaces")
        self.client.force_authenticate(user=self.specialist_user)
        response = self.client.patch(
            reverse("specialist-detail", args=[other_specialist.pk]),
            {"especialidad": "Modificada"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        other_specialist.refresh_from_db()
        self.assertEqual(other_specialist.especialidad, "Radioenlaces")

    def test_admin_can_list_technicians(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse("technician-list-create"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_technician_can_view_own_profile(self):
        self.client.force_authenticate(user=self.technician_user)
        response = self.client.get(reverse("technician-detail", args=[self.technician.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.technician.pk)
        self.assertIn("carga_trabajo", response.data)

    def test_technician_cannot_modify_another_technician(self):
        other_user = User.objects.create_user(
            username="tecnico2",
            password="Password123",
            role=User.Role.TECNICO,
        )
        other_technician = Technician.objects.create(user=other_user, especialidad="Radioenlaces")
        self.client.force_authenticate(user=self.technician_user)
        response = self.client.patch(
            reverse("technician-detail", args=[other_technician.pk]),
            {"especialidad": "Modificada"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        other_technician.refresh_from_db()
        self.assertEqual(other_technician.especialidad, "Radioenlaces")

    def test_admin_can_assign_specialist_to_ticket(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            reverse("ticket-detail", args=[self.other_ticket.pk]),
            {"specialist": self.specialist.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.other_ticket.refresh_from_db()
        self.assertEqual(self.other_ticket.specialist, self.specialist)

    def test_client_cannot_assign_specialist_to_ticket(self):
        self.client.force_authenticate(user=self.client_user)
        response = self.client.patch(
            reverse("ticket-detail", args=[self.ticket.pk]),
            {"specialist": self.specialist.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_assign_available_technician(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            reverse("ticket-detail", args=[self.other_ticket.pk]),
            {"technician": self.technician.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.other_ticket.refresh_from_db()
        self.assertEqual(self.other_ticket.technician, self.technician)

    def test_admin_cannot_assign_unavailable_technician(self):
        self.technician.disponible = False
        self.technician.save(update_fields=["disponible"])
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            reverse("ticket-detail", args=[self.other_ticket.pk]),
            {"technician": self.technician.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.other_ticket.refresh_from_db()
        self.assertIsNone(self.other_ticket.technician)

    def test_non_admin_roles_cannot_make_staff_assignments(self):
        attempts = (
            (self.client_user, self.ticket, {"specialist": self.specialist.pk}),
            (self.specialist_user, self.ticket, {"technician": self.technician.pk}),
            (self.technician_user, self.ticket, {"specialist": self.specialist.pk}),
        )

        for user, ticket, payload in attempts:
            with self.subTest(role=user.role):
                self.client.force_authenticate(user=user)
                response = self.client.patch(
                    reverse("ticket-detail", args=[ticket.pk]),
                    payload,
                    format="json",
                )
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_ticket_cannot_be_marked_technician_assigned_without_technician(self):
        self.other_ticket.estado = Ticket.Status.REQUIERE_VISITA
        self.other_ticket.save(update_fields=["estado"])
        self.client.force_authenticate(user=self.admin)
        url = reverse("ticket-detail", args=[self.other_ticket.pk])

        missing_technician_response = self.client.patch(
            url,
            {"estado": Ticket.Status.TECNICO_ASIGNADO},
            format="json",
        )
        self.assertEqual(missing_technician_response.status_code, status.HTTP_400_BAD_REQUEST)

        assigned_response = self.client.patch(
            url,
            {"technician": self.technician.pk, "estado": Ticket.Status.TECNICO_ASIGNADO},
            format="json",
        )
        self.assertEqual(assigned_response.status_code, status.HTTP_200_OK)
        self.other_ticket.refresh_from_db()
        self.assertEqual(self.other_ticket.technician, self.technician)
        self.assertEqual(self.other_ticket.estado, Ticket.Status.TECNICO_ASIGNADO)

    def test_admin_cannot_assign_profiles_with_wrong_user_roles(self):
        invalid_specialist = Specialist.objects.create(
            user=self.other_client_user,
            especialidad="Perfil inválido",
        )
        invalid_technician = Technician.objects.create(
            user=self.other_client_user,
            especialidad="Perfil inválido",
        )
        self.client.force_authenticate(user=self.admin)

        specialist_response = self.client.patch(
            reverse("ticket-detail", args=[self.other_ticket.pk]),
            {"specialist": invalid_specialist.pk},
            format="json",
        )
        technician_response = self.client.patch(
            reverse("ticket-detail", args=[self.other_ticket.pk]),
            {"technician": invalid_technician.pk},
            format="json",
        )

        self.assertEqual(specialist_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(technician_response.status_code, status.HTTP_400_BAD_REQUEST)

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
