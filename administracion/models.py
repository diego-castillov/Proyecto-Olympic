from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class Usuario(AbstractUser):
    # Definimos roles
    ROLES = (
        ('admin', 'Administrador'),
        ('vendedor', 'Vendedor'),
        ('cliente', 'Cliente'),
    )

    rol = models.CharField(max_length=20, choices=ROLES, default='cliente')

    def __str__(self):
        return f"{self.username} - {self.get_rol_display()}"


class Cliente(models.Model):
    # Relación con el usuario 
    # (Al llamarse 'usuario', Django buscará automáticamente la columna 'usuario_id' en la BD)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_cliente', null=True, blank=True)

    id_cliente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=75) # Ajustado a varchar(75)
    apellido = models.CharField(max_length=75, blank=True, null=True) # NUEVO
    email = models.CharField(max_length=150, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion_envio = models.TextField(blank=True, null=True) # NUEVO
    fecha_registro = models.DateTimeField(blank=True, null=True) # NUEVO

    class Meta:
        managed = False
        db_table = 'cliente'
    
    def __str__(self):
        # Ahora podemos devolver el nombre y el apellido juntos
        if self.apellido:
            return f"{self.nombre} {self.apellido}"
        return self.nombre