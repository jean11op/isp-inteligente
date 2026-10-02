from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
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
        password = attrs.get("password")
        if password:
            password_user = self.instance or User(
                username=attrs.get("username", ""),
                email=attrs.get("email", ""),
                role=attrs.get("role", User.Role.CLIENTE),
            )
            try:
                validate_password(password, user=password_user)
            except DjangoValidationError as error:
                raise serializers.ValidationError({"password": error.messages}) from error

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
    """Serializer seguro para clientes y asignación administrativa de usuario."""

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
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
        read_only_fields = ["id", "service", "servicio_activo", "fecha_registro"]

    def validate(self, attrs):
        request = self.context.get("request")
        user = attrs.get("user", getattr(self.instance, "user", None))

        if user and user.role != User.Role.CLIENTE:
            raise serializers.ValidationError({"user": "El usuario asociado debe tener el rol CLIENTE."})

        if user and Client.objects.filter(user=user).exclude(pk=getattr(self.instance, "pk", None)).exists():
            raise serializers.ValidationError({"user": "Este usuario ya tiene un perfil de cliente."})

        if request and request.user.is_authenticated:
            if "user" in self.initial_data and str(self.initial_data.get("user")) != str(request.user.pk):
                if request.user.role != User.Role.ADMINISTRADOR:
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
    """Serializer para tickets con campos de creación limitados para clientes."""

    class Meta:
        model = Ticket
        fields = [
            "id",
            "client",
            "service",
            "titulo",
            "descripcion",
            "prioridad",
            "estado",
            "diagnostico",
            "solucion",
            "specialist",
            "technician",
            "fecha_creacion",
            "fecha_actualizacion",
        ]
        read_only_fields = ["id", "fecha_creacion", "fecha_actualizacion"]

    CLIENT_CREATE_FIELDS = {"titulo", "descripcion", "prioridad"}
    CLIENT_INTERNAL_FIELDS = {
        "client",
        "service",
        "estado",
        "diagnostico",
        "solucion",
        "specialist",
        "technician",
    }

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        if request and request.user.is_authenticated and request.user.role == User.Role.CLIENTE:
            for field_name in self.CLIENT_INTERNAL_FIELDS:
                fields[field_name].read_only = True
        return fields

    def validate(self, attrs):
        request = self.context.get("request")
        if request and request.user.is_authenticated and request.user.role == User.Role.CLIENTE:
            unexpected_fields = set(self.initial_data) - self.CLIENT_CREATE_FIELDS
            if unexpected_fields:
                errors = {
                    field: "Este campo no puede ser enviado por un cliente."
                    for field in sorted(unexpected_fields)
                }
                raise serializers.ValidationError(errors)

            client = Client.objects.filter(user=request.user).select_related("service").first()
            if client is None:
                raise serializers.ValidationError({"client": "El usuario no tiene un perfil de cliente asociado."})
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated and request.user.role == User.Role.CLIENTE:
            client = Client.objects.filter(user=request.user).select_related("service").first()
            if client is None:
                raise serializers.ValidationError({"client": "El usuario no tiene un perfil de cliente asociado."})
            validated_data["client"] = client
            validated_data["service"] = client.service
        return super().create(validated_data)