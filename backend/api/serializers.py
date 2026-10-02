from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from users.models import User
from clients.models import Client
from services.models import Service
from specialists.models import Specialist
from technicians.models import Technician
from tickets.models import Ticket
from visits.models import Visit
from django.utils import timezone
from inventory.models import InventoryItem, InventoryUsage
from evaluations.models import Evaluation
from history.models import TicketHistory


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

    @transaction.atomic
    def update(self, instance, validated_data):
        previous_status = instance.estado
        new_status = validated_data.get("estado", previous_status)
        ticket = super().update(instance, validated_data)

        if new_status != previous_status:
            request = self.context.get("request")
            user = request.user if request and request.user.is_authenticated else None
            TicketHistory.objects.create(
                ticket=ticket,
                user=user,
                estado_anterior=previous_status,
                estado_nuevo=new_status,
            )
        return ticket


class VisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visit
        fields = [
            "id",
            "ticket",
            "technician",
            "estado",
            "fecha_programada",
            "fecha_inicio",
            "fecha_fin",
            "resultado",
            "observaciones",
            "fecha_creacion",
        ]
        read_only_fields = ["id", "fecha_inicio", "fecha_fin", "fecha_creacion"]

    VALID_TRANSITIONS = {
        Visit.Status.PROGRAMADA: {Visit.Status.EN_CAMINO, Visit.Status.CANCELADA},
        Visit.Status.EN_CAMINO: {Visit.Status.EN_DOMICILIO},
        Visit.Status.EN_DOMICILIO: {Visit.Status.EN_ATENCION},
        Visit.Status.EN_ATENCION: {Visit.Status.COMPLETADA},
    }
    TECHNICIAN_READ_ONLY_FIELDS = {
        "ticket",
        "technician",
        "fecha_programada",
        "fecha_inicio",
        "fecha_fin",
        "fecha_creacion",
    }

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        if self.instance is None:
            fields["estado"].read_only = True
        if request and request.user.is_authenticated and request.user.role == "TECNICO":
            for field_name in self.TECHNICIAN_READ_ONLY_FIELDS:
                fields[field_name].read_only = True
        return fields

    def validate(self, attrs):
        request = self.context.get("request")
        is_admin = request and request.user.is_authenticated and request.user.role == User.Role.ADMINISTRADOR

        if self.instance is None:
            requested_status = self.initial_data.get("estado")
            if requested_status and requested_status != Visit.Status.PROGRAMADA:
                raise serializers.ValidationError({"estado": "Una visita nueva debe iniciar en estado PROGRAMADA."})

        if is_admin:
            ticket = attrs.get("ticket")
            technician = attrs.get("technician")
            if self.instance is not None:
                ticket = ticket or self.instance.ticket
                technician = technician or self.instance.technician

            if ticket is not None and ticket.estado != Ticket.Status.TECNICO_ASIGNADO:
                raise serializers.ValidationError({"ticket": "El ticket debe estar en estado TECNICO_ASIGNADO."})
            if ticket is not None and technician is not None and ticket.technician_id != technician.pk:
                raise serializers.ValidationError({"technician": "El técnico debe coincidir con el asignado al ticket."})
            if technician is not None:
                if technician.user.role != User.Role.TECNICO:
                    raise serializers.ValidationError({"technician": "El perfil debe pertenecer a un usuario TECNICO."})
                if not technician.activo or not technician.disponible:
                    raise serializers.ValidationError({"technician": "El técnico debe estar activo y disponible."})

        if self.instance is not None and "estado" in attrs:
            current_status = self.instance.estado
            new_status = attrs["estado"]
            if new_status not in self.VALID_TRANSITIONS.get(current_status, set()):
                raise serializers.ValidationError({"estado": "La transición solicitada no es válida."})

        if self.instance is not None:
            fecha_inicio = self.instance.fecha_inicio
            fecha_fin = self.instance.fecha_fin
            if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
                raise serializers.ValidationError({"fecha_fin": "No puede ser anterior al inicio de la visita."})
        return attrs

    def update(self, instance, validated_data):
        new_status = validated_data.get("estado")
        if new_status == Visit.Status.EN_CAMINO and instance.fecha_inicio is None:
            validated_data["fecha_inicio"] = timezone.now()
        if new_status in {Visit.Status.COMPLETADA, Visit.Status.CANCELADA} and instance.fecha_fin is None:
            validated_data["fecha_fin"] = timezone.now()
        return super().update(instance, validated_data)


class InventoryItemSerializer(serializers.ModelSerializer):
    cantidad = serializers.IntegerField(min_value=0)

    class Meta:
        model = InventoryItem
        fields = ["id", "nombre", "descripcion", "cantidad", "unidad", "activo", "fecha_creacion"]
        read_only_fields = ["id", "fecha_creacion"]


class InventoryUsageSerializer(serializers.ModelSerializer):
    cantidad = serializers.IntegerField(min_value=1)

    class Meta:
        model = InventoryUsage
        fields = ["id", "visit", "item", "cantidad", "fecha_registro"]
        read_only_fields = ["id", "fecha_registro"]

    def validate(self, attrs):
        visit = attrs.get("visit", getattr(self.instance, "visit", None))
        item = attrs.get("item", getattr(self.instance, "item", None))
        quantity = attrs.get("cantidad", getattr(self.instance, "cantidad", None))
        request = self.context.get("request")

        if request and request.user.is_authenticated and request.user.role == User.Role.TECNICO:
            if visit.technician.user_id != request.user.pk:
                raise PermissionDenied("Solo puedes registrar materiales en tus propias visitas.")

        if item is not None:
            changing_item = self.instance is None or item.pk != self.instance.item_id
            if changing_item and not item.activo:
                raise serializers.ValidationError({"item": "No se puede utilizar un material inactivo."})

            if quantity is not None:
                available = item.cantidad
                if self.instance is not None and item.pk == self.instance.item_id:
                    available += self.instance.cantidad
                if quantity > available:
                    raise serializers.ValidationError({"cantidad": "La cantidad supera el stock disponible."})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        item = InventoryItem.objects.select_for_update().get(pk=validated_data["item"].pk)
        quantity = validated_data["cantidad"]
        if not item.activo:
            raise serializers.ValidationError({"item": "No se puede utilizar un material inactivo."})
        if quantity > item.cantidad:
            raise serializers.ValidationError({"cantidad": "La cantidad supera el stock disponible."})

        item.cantidad -= quantity
        item.save(update_fields=["cantidad"])
        validated_data["item"] = item
        return InventoryUsage.objects.create(**validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        usage = InventoryUsage.objects.select_for_update().get(pk=instance.pk)
        old_item_id = usage.item_id
        new_item = validated_data.get("item", usage.item)
        new_quantity = validated_data.get("cantidad", usage.cantidad)

        locked_items = {
            item.pk: item
            for item in InventoryItem.objects.select_for_update()
            .filter(pk__in=sorted({old_item_id, new_item.pk}))
            .order_by("pk")
        }
        old_item = locked_items[old_item_id]
        target_item = locked_items[new_item.pk]

        if new_item.pk != old_item_id and not target_item.activo:
            raise serializers.ValidationError({"item": "No se puede utilizar un material inactivo."})

        available = target_item.cantidad + (usage.cantidad if target_item.pk == old_item_id else 0)
        if new_quantity > available:
            raise serializers.ValidationError({"cantidad": "La cantidad supera el stock disponible."})

        if target_item.pk == old_item_id:
            target_item.cantidad = available - new_quantity
            target_item.save(update_fields=["cantidad"])
        else:
            old_item.cantidad += usage.cantidad
            target_item.cantidad -= new_quantity
            old_item.save(update_fields=["cantidad"])
            target_item.save(update_fields=["cantidad"])

        usage.visit = validated_data.get("visit", usage.visit)
        usage.item = target_item
        usage.cantidad = new_quantity
        usage.save(update_fields=["visit", "item", "cantidad"])
        return usage


class EvaluationSerializer(serializers.ModelSerializer):
    puntuacion = serializers.IntegerField(min_value=1, max_value=5)
    ticket = serializers.PrimaryKeyRelatedField(queryset=Ticket.objects.all())

    class Meta:
        model = Evaluation
        fields = ["id", "ticket", "puntuacion", "comentario", "fecha_evaluacion"]
        read_only_fields = ["id", "fecha_evaluacion"]

    def get_fields(self):
        fields = super().get_fields()
        if self.instance is not None:
            fields["ticket"].read_only = True
        return fields

    def validate(self, attrs):
        request = self.context.get("request")
        if self.instance is None and request and request.user.is_authenticated:
            ticket = attrs.get("ticket")
            if ticket is None:
                raise serializers.ValidationError({"ticket": "Este campo es obligatorio."})
            if ticket.client.user_id != request.user.pk:
                raise PermissionDenied("Solo puedes evaluar tus propios tickets.")
            if ticket.estado not in {Ticket.Status.RESUELTO, Ticket.Status.CERRADO}:
                raise serializers.ValidationError({"ticket": "Solo se pueden evaluar tickets resueltos o cerrados."})
            if Evaluation.objects.filter(ticket=ticket).exists():
                raise serializers.ValidationError({"ticket": "Este ticket ya tiene una evaluación."})
        return attrs


class TicketHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketHistory
        fields = [
            "id",
            "ticket",
            "user",
            "estado_anterior",
            "estado_nuevo",
            "comentario",
            "fecha",
        ]
        read_only_fields = fields