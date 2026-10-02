from django.urls import path

from .views import (
    UserListCreateView,
    UserDetailView,
    ClientListCreateView,
    ClientDetailView,
    ServiceListCreateView,
    ServiceDetailView,
    SpecialistListCreateView,
    SpecialistDetailView,
    TechnicianListCreateView,
    TechnicianDetailView,
    VisitListCreateView,
    VisitDetailView,
    TicketListCreateView,
    TicketDetailView,
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
]