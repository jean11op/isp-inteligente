from rest_framework import generics

from users.models import User
from clients.models import Client
from services.models import Service
from tickets.models import Ticket

from .serializers import (
    UserSerializer,
    ClientSerializer,
    ServiceSerializer,
    TicketSerializer,
)


class UserListCreateView(generics.ListCreateAPIView):
    """
    GET  → obtiene todos los usuarios.
    POST → crea un nuevo usuario.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer


class ClientListCreateView(generics.ListCreateAPIView):
    """
    GET  → obtiene todos los clientes.
    POST → crea un nuevo cliente.
    """

    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class ServiceListCreateView(generics.ListCreateAPIView):
    """
    GET  → obtiene todos los servicios.
    POST → crea un nuevo servicio.
    """

    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


class TicketListCreateView(generics.ListCreateAPIView):
    """
    GET  → obtiene todos los tickets.
    POST → crea un nuevo ticket.
    """

    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    → obtiene un usuario.
    PUT    → reemplaza un usuario.
    PATCH  → modifica parcialmente un usuario.
    DELETE → elimina un usuario.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer


class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET, PUT, PATCH y DELETE para un cliente.
    """

    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET, PUT, PATCH y DELETE para un servicio.
    """

    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


class TicketDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET, PUT, PATCH y DELETE para un ticket.
    """

    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer