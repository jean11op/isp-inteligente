from rest_framework import generics
from rest_framework.exceptions import APIException
from django.db.models.deletion import ProtectedError

from users.models import User
from clients.models import Client
from services.models import Service
from specialists.models import Specialist
from technicians.models import Technician
from tickets.models import Ticket
from .permissions import (
    IsAdmin,
    IsAdminOrClientCreate,
    IsAdminOrReadOnly,
    IsAdminOrOwnSpecialistProfile,
    IsAdminOrOwnTechnicianProfile,
    IsAdminOrSelfClient,
    IsAdminOrSelfProfile,
    IsTicketRelatedOrAdmin,
)

from .serializers import (
    UserSerializer,
    ClientSerializer,
    ServiceSerializer,
    SpecialistSerializer,
    TechnicianSerializer,
    TicketSerializer,
)


class ProtectedRelationConflict(APIException):
    status_code = 409
    default_detail = "No se puede eliminar el recurso porque tiene registros relacionados."
    default_code = "protected_relation"


class ProtectedDeleteMixin:
    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError as error:
            raise ProtectedRelationConflict() from error


class UserListCreateView(generics.ListCreateAPIView):
    """Lista usuarios y crea nuevos usuarios solo para administradores."""

    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        if self.request.user.role == "ADMINISTRADOR":
            return User.objects.all()
        return User.objects.filter(pk=self.request.user.pk)


class ClientListCreateView(generics.ListCreateAPIView):
    """Lista y crea clientes únicamente para administradores."""

    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAdmin]


class ServiceListCreateView(generics.ListCreateAPIView):
    """Servicios: lectura autenticada y escritura solo para administradores."""

    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminOrReadOnly]


class TicketListCreateView(generics.ListCreateAPIView):
    """Tickets: clientes y administradores pueden crear; acceso filtrado por relación."""

    serializer_class = TicketSerializer
    permission_classes = [IsAdminOrClientCreate]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Ticket.objects.none()
        if user.role == "ADMINISTRADOR":
            return Ticket.objects.all()
        if user.role == "CLIENTE":
            return Ticket.objects.filter(client__user=user)
        if user.role == "ESPECIALISTA":
            return Ticket.objects.filter(specialist__user=user)
        if user.role == "TECNICO":
            return Ticket.objects.filter(technician__user=user)
        return Ticket.objects.none()

    def perform_create(self, serializer):
        serializer.save()


class UserDetailView(ProtectedDeleteMixin, generics.RetrieveUpdateDestroyAPIView):
    """Usuario: cada usuario ve su propio perfil y los administradores todo."""

    serializer_class = UserSerializer
    permission_classes = [IsAdminOrSelfProfile]

    def get_queryset(self):
        if self.request.user.role == "ADMINISTRADOR":
            return User.objects.all()
        return User.objects.filter(pk=self.request.user.pk)


class ClientDetailView(ProtectedDeleteMixin, generics.RetrieveUpdateDestroyAPIView):
    """Cliente: el dueño del cliente o el administrador pueden acceder."""

    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAdminOrSelfClient]

    def get_queryset(self):
        if self.request.user.role == "ADMINISTRADOR":
            return Client.objects.all()
        return Client.objects.filter(user=self.request.user)


class ServiceDetailView(ProtectedDeleteMixin, generics.RetrieveUpdateDestroyAPIView):
    """Servicio: lectura autenticada y escritura solo por administradores."""

    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminOrReadOnly]


class SpecialistListCreateView(generics.ListCreateAPIView):
    queryset = Specialist.objects.select_related("user").all()
    serializer_class = SpecialistSerializer
    permission_classes = [IsAdmin]


class SpecialistDetailView(ProtectedDeleteMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SpecialistSerializer
    permission_classes = [IsAdminOrOwnSpecialistProfile]

    def get_queryset(self):
        if self.request.user.role == User.Role.ADMINISTRADOR:
            return Specialist.objects.select_related("user").all()
        return Specialist.objects.filter(user=self.request.user).select_related("user")


class TechnicianListCreateView(generics.ListCreateAPIView):
    queryset = Technician.objects.select_related("user").all()
    serializer_class = TechnicianSerializer
    permission_classes = [IsAdmin]


class TechnicianDetailView(ProtectedDeleteMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TechnicianSerializer
    permission_classes = [IsAdminOrOwnTechnicianProfile]

    def get_queryset(self):
        if self.request.user.role == User.Role.ADMINISTRADOR:
            return Technician.objects.select_related("user").all()
        return Technician.objects.filter(user=self.request.user).select_related("user")


class TicketDetailView(ProtectedDeleteMixin, generics.RetrieveUpdateDestroyAPIView):
    """Ticket: lectura permitida solo a usuarios relacionados o administradores; escritura solo admin."""

    serializer_class = TicketSerializer
    permission_classes = [IsTicketRelatedOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Ticket.objects.none()
        if user.role == "ADMINISTRADOR":
            return Ticket.objects.all()
        if user.role == "CLIENTE":
            return Ticket.objects.filter(client__user=user)
        if user.role == "ESPECIALISTA":
            return Ticket.objects.filter(specialist__user=user)
        if user.role == "TECNICO":
            return Ticket.objects.filter(technician__user=user)
        return Ticket.objects.none()