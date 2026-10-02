from rest_framework import serializers

from users.models import User
from clients.models import Client
from services.models import Service
from tickets.models import Ticket


class UserSerializer(serializers.ModelSerializer):
    """Serializer para consultar y crear usuarios con password seguro."""

    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=False,
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

    def validate(self, attrs):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return attrs

        current_role = getattr(self.instance, "role", None)
        requested_role = attrs.get("role")

        if requested_role is not None and request.user.role != User.Role.ADMINISTRADOR:
            if self.instance is None or self.instance.pk != request.user.pk:
                raise serializers.ValidationError({"role": "No tienes permisos para modificar roles."})
            if str(requested_role) != str(current_role):
                raise serializers.ValidationError({"role": "No puedes cambiar tu propio rol."})

        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        if password is None:
            raise serializers.ValidationError({"password": "Este campo es obligatorio."})
        return User.objects.create_user(password=password, **validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        if password is not None:
            instance.set_password(password)
        return super().update(instance, validated_data)


class ClientSerializer(serializers.ModelSerializer):
    """Serializer seguro para clientes. No permite reasignar la relación del usuario."""

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    service = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Client
        fields = [
            "id",
            "user",
            "service",
            "nombres",
            "apellidos",
            "documento",
            "telefono",
            "servicio_activo",
            "fecha_registro",
        ]
        read_only_fields = ["id", "user", "service", "servicio_activo", "fecha_registro"]

    def validate(self, attrs):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            if "user" in self.initial_data and str(self.initial_data.get("user")) != str(request.user.pk):
                raise serializers.ValidationError({"user": "No puedes reasignar tu relación con el cliente."})
            if self.instance and self.instance.user != request.user and request.user.role != User.Role.ADMINISTRADOR:
                raise serializers.ValidationError("No tienes permisos para modificar este cliente.")
        return attrs


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer para consultar y administrar servicios."""

    class Meta:
        model = Service
        fields = "__all__"


class TicketSerializer(serializers.ModelSerializer):
    """Serializer para consultar y administrar tickets."""

    class Meta:
        model = Ticket
        fields = "__all__"

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated and request.user.role == User.Role.CLIENTE:
            validated_data["client"] = request.user.client_profile
        return super().create(validated_data)