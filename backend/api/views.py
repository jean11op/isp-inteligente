from rest_framework import generics

from users.models import User
from clients.models import Client
from services.models import Service
from tickets.models import Ticket
from .permissions import (
    IsAdmin,
    IsAdminOrClientCreate,
    IsAdminOrReadOnly,
    IsAdminOrSelfClient,
    IsAdminOrSelfProfile,
    IsTicketRelatedOrAdmin,
)

from .serializers import (
    UserSerializer,
    ClientSerializer,
    ServiceSerializer,
    TicketSerializer,
)


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


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Usuario: cada usuario ve su propio perfil y los administradores todo."""

    serializer_class = UserSerializer
    permission_classes = [IsAdminOrSelfProfile]

    def get_queryset(self):
        if self.request.user.role == "ADMINISTRADOR":
            return User.objects.all()
        return User.objects.filter(pk=self.request.user.pk)


class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Cliente: el dueño del cliente o el administrador pueden acceder."""

    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAdminOrSelfClient]

    def get_queryset(self):
        if self.request.user.role == "ADMINISTRADOR":
            return Client.objects.all()
        return Client.objects.filter(user=self.request.user)


class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Servicio: lectura autenticada y escritura solo por administradores."""

    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminOrReadOnly]


class TicketDetailView(generics.RetrieveUpdateDestroyAPIView):
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