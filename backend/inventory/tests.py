from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from clients.models import Client
from inventory.models import InventoryItem, InventoryUsage
from technicians.models import Technician
from tickets.models import Ticket
from visits.models import Visit

User = get_user_model()


class InventoryApiTests(APITestCase):
	def setUp(self):
		self.admin = User.objects.create_user(
			username="inventoryadmin",
			password="Password123",
			role=User.Role.ADMINISTRADOR,
		)
		self.client_user = User.objects.create_user(
			username="inventoryclient",
			password="Password123",
			role=User.Role.CLIENTE,
		)
		self.technician_user = User.objects.create_user(
			username="inventorytech",
			password="Password123",
			role=User.Role.TECNICO,
		)
		self.other_technician_user = User.objects.create_user(
			username="inventorytech2",
			password="Password123",
			role=User.Role.TECNICO,
		)
		client_profile = Client.objects.create(
			user=self.client_user,
			nombres="Cliente",
			apellidos="Inventario",
			documento="stock-001",
			telefono="123456789",
		)
		self.technician = Technician.objects.create(user=self.technician_user, especialidad="Fibra")
		self.other_technician = Technician.objects.create(user=self.other_technician_user, especialidad="Redes")
		self.ticket = Ticket.objects.create(
			client=client_profile,
			technician=self.technician,
			titulo="Falla de servicio",
			descripcion="Sin conexión",
			estado=Ticket.Status.TECNICO_ASIGNADO,
		)
		self.visit = Visit.objects.create(
			ticket=self.ticket,
			technician=self.technician,
			fecha_programada=timezone.now() + timedelta(days=1),
		)
		self.other_ticket = Ticket.objects.create(
			client=client_profile,
			technician=self.other_technician,
			titulo="Otra falla",
			descripcion="Intermitencia",
			estado=Ticket.Status.TECNICO_ASIGNADO,
		)
		self.other_visit = Visit.objects.create(
			ticket=self.other_ticket,
			technician=self.other_technician,
			fecha_programada=timezone.now() + timedelta(days=1),
		)
		self.item = InventoryItem.objects.create(
			nombre="Cable UTP",
			cantidad=10,
			unidad="metros",
		)

	def test_admin_can_create_inventory_item(self):
		self.client.force_authenticate(user=self.admin)
		response = self.client.post(
			reverse("inventory-list-create"),
			{"nombre": "Conector RJ45", "cantidad": 20, "unidad": "unidades"},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertTrue(InventoryItem.objects.filter(nombre="Conector RJ45", cantidad=20).exists())

	def test_technician_can_read_but_not_modify_inventory(self):
		self.client.force_authenticate(user=self.technician_user)
		list_response = self.client.get(reverse("inventory-list-create"))
		create_response = self.client.post(
			reverse("inventory-list-create"),
			{"nombre": "No permitido", "cantidad": 1},
			format="json",
		)
		update_response = self.client.patch(
			reverse("inventory-detail", args=[self.item.pk]),
			{"cantidad": 99},
			format="json",
		)

		self.assertEqual(list_response.status_code, status.HTTP_200_OK)
		self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)
		self.assertEqual(update_response.status_code, status.HTTP_403_FORBIDDEN)

	def test_technician_can_register_usage_on_own_visit_and_stock_is_deducted(self):
		self.client.force_authenticate(user=self.technician_user)
		response = self.client.post(
			reverse("inventory-usage-list-create"),
			{"visit": self.visit.pk, "item": self.item.pk, "cantidad": 3},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.item.refresh_from_db()
		self.assertEqual(self.item.cantidad, 7)

	def test_technician_cannot_register_usage_on_another_visit(self):
		self.client.force_authenticate(user=self.technician_user)
		response = self.client.post(
			reverse("inventory-usage-list-create"),
			{"visit": self.other_visit.pk, "item": self.item.pk, "cantidad": 1},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
		self.item.refresh_from_db()
		self.assertEqual(self.item.cantidad, 10)

	def test_usage_rejects_zero_negative_and_over_stock_quantities(self):
		self.client.force_authenticate(user=self.technician_user)
		for quantity in (0, -1, 11):
			with self.subTest(quantity=quantity):
				response = self.client.post(
					reverse("inventory-usage-list-create"),
					{"visit": self.visit.pk, "item": self.item.pk, "cantidad": quantity},
					format="json",
				)
				self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.item.refresh_from_db()
		self.assertEqual(self.item.cantidad, 10)

	def test_admin_editing_and_deleting_usage_adjusts_stock(self):
		self.item.cantidad = 7
		self.item.save(update_fields=["cantidad"])
		usage = InventoryUsage.objects.create(visit=self.visit, item=self.item, cantidad=3)
		self.client.force_authenticate(user=self.admin)
		detail_url = reverse("inventory-usage-detail", args=[usage.pk])

		increase_response = self.client.patch(detail_url, {"cantidad": 5}, format="json")
		self.item.refresh_from_db()
		self.assertEqual(increase_response.status_code, status.HTTP_200_OK)
		self.assertEqual(self.item.cantidad, 5)

		decrease_response = self.client.patch(detail_url, {"cantidad": 2}, format="json")
		self.item.refresh_from_db()
		self.assertEqual(decrease_response.status_code, status.HTTP_200_OK)
		self.assertEqual(self.item.cantidad, 8)

		delete_response = self.client.delete(detail_url)
		self.item.refresh_from_db()
		self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertEqual(self.item.cantidad, 10)

	def test_visit_with_usage_cannot_be_deleted_and_lose_stock_history(self):
		self.item.cantidad = 9
		self.item.save(update_fields=["cantidad"])
		InventoryUsage.objects.create(visit=self.visit, item=self.item, cantidad=1)
		self.client.force_authenticate(user=self.admin)
		response = self.client.delete(reverse("visit-detail", args=[self.visit.pk]))

		self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
		self.assertTrue(InventoryUsage.objects.filter(visit=self.visit).exists())
		self.item.refresh_from_db()
		self.assertEqual(self.item.cantidad, 9)

	def test_ticket_with_usage_cannot_be_deleted_and_lose_stock_history(self):
		self.item.cantidad = 9
		self.item.save(update_fields=["cantidad"])
		InventoryUsage.objects.create(visit=self.visit, item=self.item, cantidad=1)
		self.client.force_authenticate(user=self.admin)
		response = self.client.delete(reverse("ticket-detail", args=[self.ticket.pk]))

		self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
		self.assertTrue(Ticket.objects.filter(pk=self.ticket.pk).exists())
		self.assertTrue(InventoryUsage.objects.filter(visit=self.visit).exists())
		self.item.refresh_from_db()
		self.assertEqual(self.item.cantidad, 9)
