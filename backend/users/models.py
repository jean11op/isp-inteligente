from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):

    class Role(models.TextChoices):
        CLIENTE = "CLIENTE", "Cliente"
        ESPECIALISTA = "ESPECIALISTA", "Especialista"
        TECNICO = "TECNICO", "Técnico"
        ADMINISTRADOR = "ADMINISTRADOR", "Administrador"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CLIENTE
    )