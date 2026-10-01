from django.urls import path

from .views import (
    UserListCreateView,
    UserDetailView,
    ClientListCreateView,
    ClientDetailView,
    ServiceListCreateView,
    ServiceDetailView,
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