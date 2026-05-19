from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model # Hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .forms import RegistroUsuarioForm
from .models import Usuario, Cliente

Usuario = get_user_model()
# Create your views here.

# VISTA 1: INICIAR SESION
def iniciar_sesion(request):
    error = None
    if request.method == 'POST':
        usuario = request.POST.get('username')
        contrasena = request.POST.get('password')

        print(f"INTENTO DE LOGIN - Usuario ingresado: '{usuario}'")
        # Verificamos si el usuario y la contraseña coinciden en la BD
        user = authenticate(request, username=usuario, password=contrasena)

        if user is not None:
            print(f"¡LOGIN EXITOSO! - Rol del usuario: '{user.rol}'")
            login(request, user)

            # Logica de redireccion segun el rol
            if user.rol == 'admin':
                return redirect('inicio')
            elif user.rol == 'vendedor':
                return redirect('inicio')
            else:
                return redirect('inicio')
        else:
            print(f"ERROR - FALLO LA AUTENTICACIÓN")
            error = "Usuario o contraseña incorrectos."
    return render(request, 'administracion/login.html', {'error': error})

# VISTA 2: REGISTRO EXCLUSIVO PARA ADMIN
@login_required
def registrar_usuario_admin(request):
    if request.user.rol != 'admin':
        return redirect('iniciar_sesion')
    
    mensaje = None
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)

        username_ingresado = request.POST.get('username')

        if Usuario.objects.filter(username=username_ingresado).exists():
            messages.error(request, "Ese usuario ya existe. Elige otro.")

        if form.is_valid():
            form.save()
            mensaje = "¡Usuario creado exitosamente!"
            form = RegistroUsuarioForm() # Limpiamos el formulario
    else:
        form = RegistroUsuarioForm()
    return render(request, 'administracion/registro_usuarios_admin.html', {
        'form': form,
        'mensaje': mensaje
    })

# VISTA 3: CERRAR SESION (LOGOUT)
def cerrar_sesion(request):
    # Esto destruira la sesion instantaneamente
    logout(request)
    return redirect('iniciar_sesion')

# VISTA 4: LISTAR USUARIOS
@login_required
def listar_usuarios(request):
    if request.user.rol != "admin":
        return redirect('iniciar_sesion')
    
    usuarios_registrados = Usuario.objects.all()
    total_usuarios = Usuario.objects.count()

    contexto = {
        'usuarios_registrados': usuarios_registrados,
        'total_usuarios': total_usuarios
    }

    return render(request, 'administracion/panel_gestion_admin.html', contexto)

# VISTA 5: ELIMINAR USUARIOS
@login_required
def eliminar_usuarios(request, id_usuario):
    if request.user.rol != "admin":
        return redirect('iniciar_sesion')

    usuario_a_eliminar = Usuario.objects.get(pk=id_usuario)

    if request.user.id == usuario_a_eliminar.id:
        messages.error(request, "Error. No puedes eliminar tu propia cuenta de administrador.")
        return redirect('listar_usuarios')
    
    usuario_a_eliminar.delete()
    messages.success(request, f"El usuario {usuario_a_eliminar.username} ha sido eliminado correctamente.")

    return redirect('listar_usuarios')

# VISTA 6: EDITAR USUARIOS
@login_required
def editar_usuarios(request, id_usuario):
    if request.user.rol != "admin":
        return redirect("iniciar_sesion")
    
    usuario_a_editar = Usuario.objects.get(pk=id_usuario)

    if request.method == 'POST':
        usuario_a_editar.username = request.POST.get('username')
        usuario_a_editar.email = request.POST.get('email')
        usuario_a_editar.rol = request.POST.get('rol')

        usuario_a_editar.save()
        messages.success(request, "Usuario actualizado correctamente")

        return redirect("listar_usuarios")
    
    contexto = {
        'usuario': usuario_a_editar
    }

    return render(request, 'administracion/edicion_usuarios.html', contexto)

# VISTA 7: SIGN UP CLIENTES
def signup_cliente(request):
    if request.method == 'POST':
        username_ingresado = request.POST.get('username')
        nombre_ingresado = request.POST.get('nombre')
        apellido_ingresado = request.POST.get('apellido')
        email_ingresado = request.POST.get('email')
        telefono_ingresado = request.POST.get('telefono')
        contrasena_ingresada = request.POST.get('password')
        foto_ingresada = request.FILES.get('foto_de_perfil')

        if Usuario.objects.filter(username=username_ingresado).exists():
            messages.error(request, "Ese nombre de usuario ya esta en uso. Elige otro.")
            return redirect('signup_cliente')

        nuevo_usuario = Usuario.objects.create_user(
            username = username_ingresado,
            email = email_ingresado,
            password = contrasena_ingresada,
            rol = 'cliente'
        )

        Cliente.objects.create(
            usuario = nuevo_usuario,
            nombre = nombre_ingresado,
            apellido = apellido_ingresado,
            email = email_ingresado,
            telefono = telefono_ingresado,
            fecha_registro = timezone.now(),
            foto_perfil = foto_ingresada
        )

        messages.success(request, "Tu cuenta ha sido creada con exito! Por favor inicia sesion")

        return redirect('iniciar_sesion')
    return render(request, 'administracion/signup.html')

# VISTA 8: EDITAR PERFIL CLIENTES
@login_required
def edicion_perfil_usuario(request, id_cliente):
    if request.user.rol not in ['admin', 'vendedor', 'cliente']:
        return redirect('iniciar_sesion')
    
    cliente_a_editar = Cliente.objects.get(pk=id_cliente)
    usuario_a_editar = cliente_a_editar.usuario

    if request.user.rol == 'cliente' and request.user.id != usuario_a_editar.id:
        return redirect('inicio')

    if request.method == 'POST':
        cliente_a_editar.nombre = request.POST.get('nombre')
        cliente_a_editar.apellido = request.POST.get('apellido')
        usuario_a_editar.username = request.POST.get('username')
        cliente_a_editar.email = request.POST.get('email')
        cliente_a_editar.telefono = request.POST.get('telefono')
        cliente_a_editar.direccion_envio = request.POST.get('direccion')

        if request.FILES.get('foto_de_perfil'):
            cliente_a_editar.foto_perfil = request.FILES.get('foto_de_perfil')

        cliente_a_editar.save()
        usuario_a_editar.save()

        return redirect('inicio')
    
    contexto = {
        'cliente': cliente_a_editar,
        'usuario': usuario_a_editar
    }
    
    return render(request, 'administracion/edicion_perfil_usuario.html', contexto)