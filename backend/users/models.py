from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):

    """
    Usuario principal del sistema ISP Inteligente.

    Django utiliza este modelo para manejar la autenticación
    y los datos básicos de acceso al sistema.
    """
    
    # Roles disponibles dentro del sistema ISP Inteligente.
    class Role(models.TextChoices):
        CLIENTE = "CLIENTE", "Cliente"
        ESPECIALISTA = "ESPECIALISTA", "Especialista"
        TECNICO = "TECNICO", "Técnico"
        ADMINISTRADOR = "ADMINISTRADOR", "Administrador"

    # Define el tipo de usuario dentro del sistema ISP Inteligente.
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CLIENTE
        
    )