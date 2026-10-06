from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    UserListCreateView,
    UserDetailView,
    ClientListCreateView,
    ClientDetailView,
    AddressListCreateView,
    AddressDetailView,
    ServiceListCreateView,
    ServiceDetailView,
    SpecialistListCreateView,
    SpecialistDetailView,
    TechnicianListCreateView,
    TechnicianDetailView,
    VisitListCreateView,
    VisitDetailView,
    InventoryItemListCreateView,
    InventoryItemDetailView,
    InventoryUsageListCreateView,
    InventoryUsageDetailView,
    EvaluationListCreateView,
    EvaluationDetailView,
    TicketHistoryListView,
    TicketHistoryDetailView,
    TicketListCreateView,
    TicketDetailView,
    TicketRequestSpecialistView,
)


urlpatterns = [

    # Usuarios
    path(
        "users/",
        UserListCreateView.as_view(),
        name="user-list-create"
    ),

    path(
        "users/<int:pk>/",
        UserDetailView.as_view(),
        name="user-detail"
    ),

    # Clientes
    path(
        "clients/",
        ClientListCreateView.as_view(),
        name="client-list-create"
    ),

    path(
        "clients/<int:pk>/",
        ClientDetailView.as_view(),
        name="client-detail"
    ),

    path("addresses/", AddressListCreateView.as_view(), name="address-list-create"),
    path("addresses/<int:pk>/", AddressDetailView.as_view(), name="address-detail"),

    # Servicios
    path(
        "services/",
        ServiceListCreateView.as_view(),
        name="service-list-create"
    ),

    path(
        "services/<int:pk>/",
        ServiceDetailView.as_view(),
        name="service-detail"
    ),

    # Especialistas
    path(
        "specialists/",
        SpecialistListCreateView.as_view(),
        name="specialist-list-create"
    ),
    path(
        "specialists/<int:pk>/",
        SpecialistDetailView.as_view(),
        name="specialist-detail"
    ),

    # Tecnicos
    path(
        "technicians/",
        TechnicianListCreateView.as_view(),
        name="technician-list-create"
    ),
    path(
        "technicians/<int:pk>/",
        TechnicianDetailView.as_view(),
        name="technician-detail"
    ),

    # Visitas tecnicas
    path(
        "visits/",
        VisitListCreateView.as_view(),
        name="visit-list-create"
    ),
    path(
        "visits/<int:pk>/",
        VisitDetailView.as_view(),
        name="visit-detail"
    ),

    # Inventario
    path(
        "inventory/",
        InventoryItemListCreateView.as_view(),
        name="inventory-list-create"
    ),
    path(
        "inventory/<int:pk>/",
        InventoryItemDetailView.as_view(),
        name="inventory-detail"
    ),
    path(
        "inventory-usage/",
        InventoryUsageListCreateView.as_view(),
        name="inventory-usage-list-create"
    ),
    path(
        "inventory-usage/<int:pk>/",
        InventoryUsageDetailView.as_view(),
        name="inventory-usage-detail"
    ),

    # Evaluaciones
    path(
        "evaluations/",
        EvaluationListCreateView.as_view(),
        name="evaluation-list-create"
    ),
    path(
        "evaluations/<int:pk>/",
        EvaluationDetailView.as_view(),
        name="evaluation-detail"
    ),

    # Historial de tickets
    path(
        "history/",
        TicketHistoryListView.as_view(),
        name="history-list"
    ),
    path(
        "history/<int:pk>/",
        TicketHistoryDetailView.as_view(),
        name="history-detail"
    ),

    # Tickets
    path(
        "tickets/",
        TicketListCreateView.as_view(),
        name="ticket-list-create"
    ),

    path(
        "tickets/<int:pk>/",
        TicketDetailView.as_view(),
        name="ticket-detail"
    ),
    path(
        "tickets/<int:pk>/request-specialist/",
        TicketRequestSpecialistView.as_view(),
        name="ticket-request-specialist",
    ),
    
    #AUTENTICACION 
    
    path(
        "auth/token/",
        TokenObtainPairView.as_view(),
        name="token-obtain-pair",
    ),

    path(
        "auth/token/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),
]