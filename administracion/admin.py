from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Cliente
# Register your models here.

# Esto permite ver el campo 'rol' en el panel de administracion
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Informacion de Rol', {'fields': ('rol',)}),
    )
    list_display = ['username', 'email', 'rol', 'is_staff']

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Cliente)