from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from users.models import User
from clients.models import Client
from services.models import Service
from specialists.models import Specialist
from technicians.models import Technician
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


class UserBoundProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    profile_model = None
    user_role = None

    def get_fields(self):
        fields = super().get_fields()
        if self.instance is not None:
            fields["user"].read_only = True
        return fields

    def validate(self, attrs):
        user = attrs.get("user", getattr(self.instance, "user", None))
        if user and user.role != self.user_role:
            raise serializers.ValidationError({"user": f"El usuario asociado debe tener el rol {self.user_role}."})

        if user and self.profile_model.objects.filter(user=user).exclude(pk=getattr(self.instance, "pk", None)).exists():
            raise serializers.ValidationError({"user": "El usuario ya tiene un perfil de este tipo."})
        return attrs


class SpecialistSerializer(UserBoundProfileSerializer):
    profile_model = Specialist
    user_role = User.Role.ESPECIALISTA

    class Meta:
        model = Specialist
        fields = ["id", "user", "especialidad", "disponible", "activo", "fecha_registro"]
        read_only_fields = ["id", "fecha_registro"]


class TechnicianSerializer(UserBoundProfileSerializer):
    profile_model = Technician
    user_role = User.Role.TECNICO

    class Meta:
        model = Technician
        fields = [
            "id",
            "user",
            "especialidad",
            "disponible",
            "latitud",
            "longitud",
            "carga_trabajo",
            "activo",
            "fecha_registro",
        ]
        read_only_fields = ["id", "carga_trabajo", "fecha_registro"]


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
    VALID_TRANSITIONS = {
        Ticket.Status.NUEVO: {Ticket.Status.EN_REVISION},
        Ticket.Status.EN_REVISION: {
            Ticket.Status.ESPERANDO_ESPECIALISTA,
            Ticket.Status.DIAGNOSTICADO,
        },
        Ticket.Status.ESPERANDO_ESPECIALISTA: {
            Ticket.Status.DIAGNOSTICADO,
            Ticket.Status.ESCALADO,
        },
        Ticket.Status.DIAGNOSTICADO: {
            Ticket.Status.REQUIERE_VISITA,
            Ticket.Status.RESUELTO,
        },
        Ticket.Status.REQUIERE_VISITA: {Ticket.Status.TECNICO_ASIGNADO},
        Ticket.Status.TECNICO_ASIGNADO: {Ticket.Status.EN_CAMINO},
        Ticket.Status.EN_CAMINO: {Ticket.Status.EN_DOMICILIO},
        Ticket.Status.EN_DOMICILIO: {Ticket.Status.EN_ATENCION},
        Ticket.Status.EN_ATENCION: {
            Ticket.Status.RESUELTO,
            Ticket.Status.NO_RESUELTO,
        },
        Ticket.Status.NO_RESUELTO: {Ticket.Status.SEGUNDA_VISITA},
        Ticket.Status.SEGUNDA_VISITA: {Ticket.Status.TECNICO_ASIGNADO},
        Ticket.Status.RESUELTO: {Ticket.Status.CERRADO},
    }
    SPECIALIST_TRANSITIONS = {
        (Ticket.Status.NUEVO, Ticket.Status.EN_REVISION),
        (Ticket.Status.EN_REVISION, Ticket.Status.ESPERANDO_ESPECIALISTA),
        (Ticket.Status.EN_REVISION, Ticket.Status.DIAGNOSTICADO),
        (Ticket.Status.ESPERANDO_ESPECIALISTA, Ticket.Status.DIAGNOSTICADO),
        (Ticket.Status.ESPERANDO_ESPECIALISTA, Ticket.Status.ESCALADO),
        (Ticket.Status.DIAGNOSTICADO, Ticket.Status.REQUIERE_VISITA),
        (Ticket.Status.DIAGNOSTICADO, Ticket.Status.RESUELTO),
    }
    TECHNICIAN_TRANSITIONS = {
        (Ticket.Status.TECNICO_ASIGNADO, Ticket.Status.EN_CAMINO),
        (Ticket.Status.EN_CAMINO, Ticket.Status.EN_DOMICILIO),
        (Ticket.Status.EN_DOMICILIO, Ticket.Status.EN_ATENCION),
        (Ticket.Status.EN_ATENCION, Ticket.Status.RESUELTO),
        (Ticket.Status.EN_ATENCION, Ticket.Status.NO_RESUELTO),
    }
    ROLE_UPDATE_FIELDS = {
        User.Role.ESPECIALISTA: {"estado", "diagnostico"},
        User.Role.TECNICO: {"estado", "solucion"},
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
        if self.instance is None:
            requested_status = self.initial_data.get("estado")
            if requested_status and requested_status != Ticket.Status.NUEVO:
                raise serializers.ValidationError({"estado": "Un ticket nuevo debe iniciar en estado NUEVO."})

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

        if request and request.user.is_authenticated and self.instance is not None:
            role = request.user.role
            if role in self.ROLE_UPDATE_FIELDS:
                unexpected_fields = set(attrs) - self.ROLE_UPDATE_FIELDS[role]
                if unexpected_fields:
                    raise PermissionDenied("No tienes permisos para modificar esos campos del ticket.")

            specialist = attrs.get("specialist")
            if specialist is not None and specialist.user.role != User.Role.ESPECIALISTA:
                raise serializers.ValidationError({"specialist": "El perfil debe pertenecer a un usuario ESPECIALISTA."})

            technician = attrs.get("technician")
            if technician is not None:
                if technician.user.role != User.Role.TECNICO:
                    raise serializers.ValidationError({"technician": "El perfil debe pertenecer a un usuario TECNICO."})
                if technician != self.instance.technician and (not technician.activo or not technician.disponible):
                    raise serializers.ValidationError({"technician": "El técnico debe estar activo y disponible para asignarse."})

            if "estado" in attrs:
                current_status = self.instance.estado
                new_status = attrs["estado"]
                if new_status not in self.VALID_TRANSITIONS.get(current_status, set()):
                    raise serializers.ValidationError({"estado": "La transición solicitada no es válida."})

                transition = (current_status, new_status)
                if role == User.Role.ESPECIALISTA and transition not in self.SPECIALIST_TRANSITIONS:
                    raise PermissionDenied("No tienes permisos para realizar esta transición.")
                if role == User.Role.TECNICO and transition not in self.TECHNICIAN_TRANSITIONS:
                    raise PermissionDenied("No tienes permisos para realizar esta transición.")

                if new_status == Ticket.Status.TECNICO_ASIGNADO:
                    technician = attrs.get("technician", self.instance.technician)
                    if technician is None:
                        raise serializers.ValidationError({"technician": "Asigna un técnico antes de cambiar el estado."})
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