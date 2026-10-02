from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """Permite el acceso únicamente a usuarios con rol ADMINISTRADOR."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "ADMINISTRADOR"

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsClient(BasePermission):
    """Permite el acceso únicamente a usuarios con rol CLIENTE."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "CLIENTE"


class IsSpecialist(BasePermission):
    """Permite el acceso únicamente a usuarios con rol ESPECIALISTA."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "ESPECIALISTA"


class IsTechnician(BasePermission):
    """Permite el acceso únicamente a usuarios con rol TECNICO."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "TECNICO"


class IsAdminOrOwnSpecialistProfile(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in {"ADMINISTRADOR", "ESPECIALISTA"}

    def has_object_permission(self, request, view, obj):
        if request.user.role == "ADMINISTRADOR":
            return True
        if obj.user != request.user:
            return False
        return request.method in SAFE_METHODS or request.method in {"PUT", "PATCH"}


class IsAdminOrOwnTechnicianProfile(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in {"ADMINISTRADOR", "TECNICO"}

    def has_object_permission(self, request, view, obj):
        if request.user.role == "ADMINISTRADOR":
            return True
        if obj.user != request.user:
            return False
        return request.method in SAFE_METHODS or request.method in {"PUT", "PATCH"}


class IsAdminOrVisitParticipant(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        if request.user.role == "ADMINISTRADOR":
            return True
        return request.method in {"PUT", "PATCH"} and request.user.role == "TECNICO"

    def has_object_permission(self, request, view, obj):
        if request.user.role == "ADMINISTRADOR":
            return True

        if request.method in SAFE_METHODS:
            if request.user.role == "CLIENTE":
                return obj.ticket.client.user == request.user
            if request.user.role == "ESPECIALISTA":
                return obj.ticket.specialist is not None and obj.ticket.specialist.user == request.user
            if request.user.role == "TECNICO":
                return obj.technician.user == request.user
            return False

        return (
            request.method in {"PUT", "PATCH"}
            and request.user.role == "TECNICO"
            and obj.technician.user == request.user
        )


class IsAdminOrReadOnly(BasePermission):
    """Permite lectura a cualquier usuario autenticado y escritura solo a administradores."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role == "ADMINISTRADOR"


class IsAdminOrSelfProfile(BasePermission):
    """Permite a un usuario editar solo su propio perfil, y a administradores todo."""

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.role == "ADMINISTRADOR":
            return True
        if obj != request.user:
            return False
        if request.method in SAFE_METHODS:
            return True

        role_change = "role" in request.data and str(request.data.get("role")) != str(obj.role)
        return not role_change


class IsAdminOrSelfClient(BasePermission):
    """Permite a un cliente gestionar solo su propio registro y a administradores todo."""

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.role == "ADMINISTRADOR":
            return True
        if getattr(obj, "user", None) != request.user:
            return False
        if request.method in SAFE_METHODS:
            return True

        if "user" in request.data and str(request.data.get("user")) != str(request.user.pk):
            return False
        return True


class IsTicketRelatedOrAdmin(BasePermission):
    """Permite lectura relacionada y PATCH acotado a especialista/técnico asignados."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        if request.user.role == "ADMINISTRADOR":
            return True
        return request.method == "PATCH" and request.user.role in {"ESPECIALISTA", "TECNICO"}

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if request.user.role == "ADMINISTRADOR":
            return True

        if request.user.role == "CLIENTE":
            return request.method in SAFE_METHODS and obj.client.user == request.user

        if request.user.role == "ESPECIALISTA":
            return (
                (request.method in SAFE_METHODS or request.method == "PATCH")
                and obj.specialist is not None
                and obj.specialist.user == request.user
            )

        if request.user.role == "TECNICO":
            return (
                (request.method in SAFE_METHODS or request.method == "PATCH")
                and obj.technician is not None
                and obj.technician.user == request.user
            )

        return False


class IsAdminOrClientCreate(BasePermission):
    """Permite crear tickets a clientes y administradores; lectura por usuarios autenticados."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role in {"ADMINISTRADOR", "CLIENTE"}