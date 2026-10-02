from django.conf import settings
from django.db import models


class Client(models.Model):
    """
    Representa al cliente del ISP dentro del sistema.

    El modelo User se encarga de la cuenta y autenticación,
    mientras que Client contiene la información propia
    del cliente como persona y como usuario del servicio ISP.
    """

    # Cuenta de usuario asociada al perfil del cliente.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_profile"
    )

    # Servicio de Internet contratado por el cliente.
    service = models.ForeignKey(
        "services.Service",
        on_delete=models.PROTECT,
        related_name="clients",
        null=True,
        blank=True
    )

    # Información personal básica del cliente.
    nombres = models.CharField(
        max_length=100
    )

    apellidos = models.CharField(
        max_length=100
    )

    # Documento de identidad del cliente.
    documento = models.CharField(
        max_length=20,
        unique=True
    )

    # Número telefónico de contacto.
    telefono = models.CharField(
        max_length=20
    )

    # Indica si el servicio del cliente se encuentra activo.
    servicio_activo = models.BooleanField(
        default=True
    )

    # Fecha en la que se registró el cliente en el sistema.
    fecha_registro = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        """
        Representación legible del cliente.
        """
        return f"{self.nombres} {self.apellidos}"
    
class Address(models.Model):
    """
    Representa un domicilio registrado por un cliente.

    Un cliente puede tener uno o varios domicilios.
    """

    # Cliente propietario del domicilio.
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="addresses"
    )

    # Dirección escrita del domicilio.
    direccion = models.CharField(
        max_length=255
    )

    # Referencia adicional para facilitar la ubicación.
    referencia = models.CharField(
        max_length=255,
        blank=True
    )

    # Coordenadas geográficas del domicilio.
    latitud = models.DecimalField(
        max_digits=9,
        decimal_places=6
    )

    longitud = models.DecimalField(
        max_digits=9,
        decimal_places=6
    )

    # Permite identificar el domicilio principal del cliente.
    principal = models.BooleanField(
        default=False
    )

    # Fecha de registro del domicilio.
    fecha_registro = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.direccion