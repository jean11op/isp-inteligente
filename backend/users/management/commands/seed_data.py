from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from clients.models import Client, Address
from specialists.models import Specialist
from technicians.models import Technician
from inventory.models import InventoryItem
from tickets.models import Ticket
from visits.models import Visit


class Command(BaseCommand):
    help = "Carga datos iniciales para desarrollo y pruebas"

    def handle(self, *args, **options):
        User = get_user_model()

        # =========================
        # USUARIOS
        # =========================

        users = [
            {
                "username": "admin",
                "password": "123456",
                "email": "admin@isp.com",
                "first_name": "Administrador",
                "last_name": "Sistema",
                "role": "ADMINISTRADOR",
                "is_staff": True,
                "is_superuser": True,
            },
            {
                "username": "tecnico1",
                "password": "123456",
                "email": "tecnico@isp.com",
                "first_name": "Tecnico",
                "last_name": "Prueba",
                "role": "TECNICO",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "especialista",
                "password": "123456",
                "email": "especialista@isp.com",
                "first_name": "Especialista",
                "last_name": "Prueba",
                "role": "ESPECIALISTA",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "cliente1",
                "password": "123456",
                "email": "cliente@isp.com",
                "first_name": "Cliente",
                "last_name": "Prueba",
                "role": "CLIENTE",
                "is_staff": False,
                "is_superuser": False,
            },
        ]

        created_users = {}

        for data in users:
            user_data = data.copy()
            username = user_data.pop("username")
            password = user_data.pop("password")

            user, created = User.objects.get_or_create(
                username=username,
                defaults=user_data,
            )

            if not created:
                for key, value in user_data.items():
                    setattr(user, key, value)

            user.set_password(password)
            user.save()

            created_users[username] = user

        # =========================
        # CLIENTE
        # =========================

        client_user = created_users["cliente1"]

        client, _ = Client.objects.get_or_create(
            user=client_user,
            defaults={
                "nombres": "Cliente",
                "apellidos": "Prueba",
                "documento": "00000001",
                "telefono": "999999999",
                "servicio_activo": True,
            },
        )

        # =========================
        # DIRECCION
        # =========================

        Address.objects.get_or_create(
            client=client,
            direccion="Av. España 1234, Trujillo",
            defaults={
                "referencia": "Cerca de la Plaza de Armas",
                "latitud": -8.111600,
                "longitud": -79.028700,
                "principal": True,
            },
        )

        # =========================
        # ESPECIALISTA
        # =========================

        Specialist.objects.get_or_create(
            user=created_users["especialista"],
            defaults={
                "especialidad": "Soporte de redes",
                "disponible": True,
                "activo": True,
            },
        )

        # =========================
        # TECNICO
        # =========================

        Technician.objects.get_or_create(
            user=created_users["tecnico1"],
            defaults={
                "especialidad": "Soporte tecnico",
                "disponible": True,
                "latitud": -8.111600,
                "longitud": -79.028700,
                "carga_trabajo": 0,
                "activo": True,
            },
        )

        # =========================
        # INVENTARIO
        # =========================

        inventory = [
            {
                "nombre": "Router WiFi",
                "descripcion": "Router inalambrico para instalaciones de clientes.",
                "cantidad": 15,
                "unidad": "unidad",
            },
            {
                "nombre": "ONU/ONT",
                "descripcion": "Equipo terminal para conexiones de fibra optica.",
                "cantidad": 20,
                "unidad": "unidad",
            },
            {
                "nombre": "Cable UTP Cat6",
                "descripcion": "Cable de red categoria 6.",
                "cantidad": 500,
                "unidad": "metro",
            },
            {
                "nombre": "Conector RJ45",
                "descripcion": "Conector para cable de red.",
                "cantidad": 200,
                "unidad": "unidad",
            },
            {
                "nombre": "Patch Cord",
                "descripcion": "Cable de conexion de red.",
                "cantidad": 50,
                "unidad": "unidad",
            },
            {
                "nombre": "Fuente de poder",
                "descripcion": "Fuente de alimentacion para equipos de red.",
                "cantidad": 30,
                "unidad": "unidad",
            },
            {
                "nombre": "Fibra optica",
                "descripcion": "Cable de fibra optica para instalaciones.",
                "cantidad": 1000,
                "unidad": "metro",
            },
            {
                "nombre": "Cinta aislante",
                "descripcion": "Cinta aislante para trabajos tecnicos.",
                "cantidad": 40,
                "unidad": "rollo",
            },
        ]

        for item in inventory:
            InventoryItem.objects.update_or_create(
                nombre=item["nombre"],
                defaults={
                    "descripcion": item["descripcion"],
                    "cantidad": item["cantidad"],
                    "unidad": item["unidad"],
                    "activo": True,
                },
            )

        # =========================
        # TICKETS
        # =========================

        specialist = Specialist.objects.get(
            user=created_users["especialista"]
        )

        technician = Technician.objects.get(
            user=created_users["tecnico1"]
        )

        ticket_nuevo, _ = Ticket.objects.get_or_create(
            client=client,
            titulo="Internet lento",
            defaults={
                "descripcion": (
                    "El cliente reporta que la velocidad de Internet "
                    "es menor a la contratada."
                ),
                "prioridad": Ticket.Priority.MEDIA,
                "estado": Ticket.Status.NUEVO,
            },
        )

        ticket_especialista, _ = Ticket.objects.get_or_create(
            client=client,
            titulo="Sin conexion a Internet",
            defaults={
                "descripcion": (
                    "El cliente indica que no tiene conexion a Internet "
                    "desde hace varias horas."
                ),
                "prioridad": Ticket.Priority.ALTA,
                "estado": Ticket.Status.ESPERANDO_ESPECIALISTA,
                "specialist": specialist,
            },
        )

        ticket_visita, _ = Ticket.objects.get_or_create(
            client=client,
            titulo="Intermitencia en la conexion",
            defaults={
                "descripcion": (
                    "La conexion presenta cortes intermitentes durante "
                    "el dia y requiere revision tecnica."
                ),
                "prioridad": Ticket.Priority.ALTA,
                "estado": Ticket.Status.TECNICO_ASIGNADO,
                "specialist": specialist,
                "technician": technician,
            },
        )

        # =========================
        # VISITA PROGRAMADA
        # =========================

        Visit.objects.get_or_create(
            ticket=ticket_visita,
            technician=technician,
            defaults={
                "estado": Visit.Status.PROGRAMADA,
                "fecha_programada": timezone.now() + timedelta(days=1),
                "resultado": "",
                "observaciones": "",
            },
        )

        # =========================
        # RESULTADO
        # =========================

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS("Seed completado correctamente.")
        )
        self.stdout.write("")
        self.stdout.write("Usuarios de prueba:")
        self.stdout.write("  admin / 123456")
        self.stdout.write("  tecnico1 / 123456")
        self.stdout.write("  especialista / 123456")
        self.stdout.write("  cliente1 / 123456")
        self.stdout.write("")
        self.stdout.write("Cliente creado: Cliente Prueba")
        self.stdout.write("Especialista creado: Soporte de redes")
        self.stdout.write("Tecnico creado: Soporte tecnico")
        self.stdout.write("Inventario cargado correctamente.")
        self.stdout.write("Tickets de prueba cargados correctamente.")
        self.stdout.write("Visita tecnica programada correctamente.")