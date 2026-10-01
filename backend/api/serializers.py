from rest_framework import serializers

from users.models import User
from clients.models import Client
from services.models import Service
from tickets.models import Ticket


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer utilizado para consultar y crear usuarios.
    """

    password = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "role",
        ]

    def create(self, validated_data):
        """
        Crea el usuario utilizando create_user()
        para que Django almacene la contraseña de forma segura.
        """
        return User.objects.create_user(**validated_data)


class ClientSerializer(serializers.ModelSerializer):
    """
    Serializer para consultar y administrar clientes.
    """

    class Meta:
        model = Client
        fields = "__all__"


class ServiceSerializer(serializers.ModelSerializer):
    """
    Serializer para consultar y administrar servicios.
    """

    class Meta:
        model = Service
        fields = "__all__"


class TicketSerializer(serializers.ModelSerializer):
    """
    Serializer para consultar y administrar tickets.
    """

    class Meta:
        model = Ticket
        fields = "__all__"