from django.shortcuts import render, redirect, get_object_or_404
from .models import Cliente, Pedido, DetallePedido
from inventario.models import Producto, Stock, Talla, Categoria
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
# Create your views here.

# VISTA 1: LISTAR CATALOGO DE PRODUCTOS
def inicio_catalogo(request):
    palabra_clave = request.GET.get('buscar')

    categoria_id = request.GET.get('categoria')
    
    # Iniciando la consulta base con la suma del stock total
    # Recordando que 'stock__cantidad' es la ruta: Modelo Stock -> campo cantidad
    consulta = Producto.objects.annotate(stock_total=Sum('stock__cantidad'))

    # Consulta de Pedidos del usuario de la sesion
    if request.user.is_authenticated:
        consulta_pedidos = Pedido.objects.filter(id_cliente__usuario_id=request.user.id).order_by('-id_pedido')
    else:
        consulta_pedidos = []

    if categoria_id:
        consulta = consulta.filter(id_categoria=categoria_id)
        
    if palabra_clave:
        productos = consulta.filter(nombre__icontains=palabra_clave)
    else:
        productos = consulta.all()
    
    categorias = Categoria.objects.all()

    contexto = {
        'productos' : productos,
        'busqueda' : palabra_clave,
        'categorias' : categorias,
        'categoria_actual' : categoria_id,
        'pedidos': consulta_pedidos
    }

    return render(request, 'ventas/catalogo_productos.html', contexto)

    # # 1. Cambiar de estado cuando se hace click en el boton
    # if request.method == 'POST':
    #     id_pedido = request.POST.get('id_pedido')
    #     nuevo_estado = request.POST.get('nuevo_estado')

    #     pedido = get_object_or_404(Pedido, pk=id_pedido)
    #     pedido.estado_pedido = nuevo_estado
    #     pedido.save()

    #     return redirect('panel_pedidos')
    
    # # 2. FILTRAR PEDIDOS
    # filtro_estado = request.GET.get('estado')

    # consulta_pedidos = Pedido.objects.all().order_by('-id_pedido')

    # if filtro_estado:
    #     consulta_pedidos = consulta_pedidos.filter(estado_pedido=filtro_estado)
    
    # contexto = {
    #     'pedidos': consulta_pedidos,
    #     'estado_actual': filtro_estado # Para saber que boton pintar de rojo
    # }

    # return render(request, 'ventas/panel_pedidos.html', contexto)

# VISTA 2: AGREGAR AL CARRITO
@login_required
def agregar_al_carrito(request, producto_id):
    producto = Producto.objects.get(pk=producto_id)
    
    if request.method == 'POST':
        talla_id = request.POST.get('talla_id')
        talla_obj = Talla.objects.get(id_talla=talla_id)

        # Capturamos la cantidad, si algo falla, ponemos 1
        try:
            nueva_cantidad = int(request.POST.get('cantidad'))
        except ValueError:
            nueva_cantidad = 1

        if nueva_cantidad > 0:
            cliente_actual = Cliente.objects.get(usuario_id=request.user.id)

            # 1. Buscamos o creamos el carrito en la base de datos MySQL
            pedido_carrito, created = Pedido.objects.get_or_create(
                id_cliente=cliente_actual,
                estado_pedido='En Carrito',
                defaults={'fecha': timezone.now(), 'estado_pago': 'Pendiente'}
            )

            # 2. Buscamos si ese producto con esa talla ya esta en el carrito
            detalle, detalle_created = DetallePedido.objects.get_or_create(
                id_pedido=pedido_carrito,
                id_producto=producto,
                id_talla=talla_obj,
                defaults={'cantidad': 0, 'precio_unitario': producto.precio}
            )

            # 3. Sumamos la cantidad y guardamos en BD
            detalle.cantidad += nueva_cantidad
            detalle.save()
            messages.success(request, f"¡Se agregó {producto.nombre} a tu carrito!")

    return redirect('inicio_catalogo')

# VISTA 3: VER CARRITO
def ver_carrito(request):
    cliente_actual = Cliente.objects.get(usuario_id=request.user.id)

    # Buscando el carrito activo del usuario
    pedido_carrito = Pedido.objects.filter(id_cliente=cliente_actual, estado_pedido='En Carrito').first()

    detalles = []
    total_a_pagar = 0

    if pedido_carrito:
        detalles = DetallePedido.objects.filter(id_pedido=pedido_carrito)
        total_a_pagar = sum(detalle.cantidad * detalle.precio_unitario for detalle in detalles)
    contexto = {
        'carrito': detalles,
        'total': total_a_pagar
    }
    return render(request, 'ventas/carrito.html', contexto)

# VISTA 4: VACIAR CARRITO
def vaciar_carrito(request):
    if request.method == 'POST':
        cliente_actual = Cliente.objects.get(usuario_id=request.user.id)
        pedido_carrito = Pedido.objects.filter(id_cliente=cliente_actual, estado_pedido='En carrito').first()

        if pedido_carrito:
            DetallePedido.objects.filter(id_pedido=pedido_carrito).delete()
            pedido_carrito.delete()
    return redirect('inicio_catalogo')

# VISTA 5: PROCESAR COMPRAR
@login_required(login_url='iniciar_sesion')
def procesar_compra(request):
    cliente_actual = Cliente.objects.get(usuario_id=request.user.id)
    pedido_carrito = Pedido.objects.filter(id_cliente=cliente_actual, estado_pedido='En Carrito').first()

    if not pedido_carrito:
        messages.error(request, "Tu carrito esta vacio.")
        return redirect('ver_carrito')
    
    # El carrito se convierte en un pedido formal
    pedido_carrito.estado_pedido = 'Pendiente'
    pedido_carrito.fecha = timezone.now()
    pedido_carrito.save()
    
    return redirect('ver_recibo', id_pedido=pedido_carrito.id_pedido)
    
# VISTA 6: VER RECIBO / PAGO QR
@login_required(login_url='iniciar_sesion')
def ver_recibo(request, id_pedido):
    # Por seguridad nos aseguramos de que el pedido pertenezca al usuario logueado
    try:
        cliente_actual = Cliente.objects.get(usuario_id=request.user.id)
        pedido = Pedido.objects.get(id_pedido=id_pedido, id_cliente=cliente_actual)
    except Cliente.DoesNotExist:
        messages.error(request, "Error de Perfil: No se encontro tu cuenta de cliente.")
        return redirect('inicio_catalogo')
    except Pedido.DoesNotExist:
        messages.error(request, "El pedido no existe o no tienes permiso para verlo.")
        return redirect('inicio_catalogo')
    
    detalles =DetallePedido.objects.filter(id_pedido=pedido)

    total_pagar = sum(detalle.cantidad * detalle.precio_unitario for detalle in detalles)

    contexto = {
        'pedido': pedido,
        'detalles': detalles,
        'total': total_pagar
    }
    return render(request, 'ventas/recibo.html', contexto)

# VISTA 7: PANEL DE PEDIDOS
@login_required
def panel_pedidos(request):
    # 1. Cambiar de estado cuando se hace click en el boton
    if request.method == 'POST':
        id_pedido = request.POST.get('id_pedido')
        nuevo_estado = request.POST.get('nuevo_estado')

        detalles_del_pedido = DetallePedido.objects.filter(id_pedido=id_pedido)

        for detalle in detalles_del_pedido:
            producto_comprado = detalle.id_producto
            nombre_producto = producto_comprado.nombre

        pedido = get_object_or_404(Pedido, pk=id_pedido)
        pedido.estado_pedido = nuevo_estado
        pedido.save()

        return redirect('panel_pedidos')
    
    # 2. FILTRAR PEDIDOS
    filtro_estado = request.GET.get('estado')

    consulta_pedidos = Pedido.objects.exclude(estado_pago='Pendiente').order_by('-id_pedido')

    if filtro_estado:
        consulta_pedidos = consulta_pedidos.filter(estado_pedido=filtro_estado)
    
    contexto = {
        # 'detalles': detalle,
        'pedidos': consulta_pedidos,
        'estado_actual': filtro_estado # Para saber que boton pintar de rojo
    }

    return render(request, 'ventas/panel_pedidos.html', contexto)

# VISTA 8: PANTALLA DE PAGO POR QRx
@login_required
def pantalla_pago_qr(request, id_pedido):
    pedido = get_object_or_404(Pedido, pk=id_pedido)

    # Verificando la columna de la base de datos
    if pedido.estado_pago == 'Pagado':
        return redirect('inicio')
    
    contexto = {
        'pedido': pedido
    }
    return render(request, 'ventas/pago_qr.html', contexto)

# VISTA 9: VERIFICAR ESTADO DEL PAGO
def verificar_estado_pago(request, id_pedido):
    pedido = get_object_or_404(Pedido, pk=id_pedido)
    return JsonResponse({'estado_pago': pedido.estado_pago})

# VISTA 10: PANEL SIMULADOR DEL BANCO
@login_required
def panel_simulador_banco(request):
    if request.user.rol not in ['admin', 'vendedor']:
        return redirect('inicio')
    
    # Filtramos usando la columna 'estado_pago'
    pedidos_pendientes = Pedido.objects.filter(estado_pago='Pendiente', estado_pedido='Pendiente').order_by('-id_pedido')

    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        accion = request.POST.get('accion')

        # Usar transaction.atomic() para asegurar que si falla el descuento de el pedido no se marque como pagado por error
        with transaction.atomic():
            pedido_a_actualizar = Pedido.objects.get(pk=pedido_id)

            if accion == 'aprobar':
                # Simulando que el banco confirmo el pago
                pedido_a_actualizar.estado_pago = 'Pagado'
                pedido_a_actualizar.save()

                detalles_del_pedido = DetallePedido.objects.filter(id_pedido=pedido_a_actualizar)

                for detalle in detalles_del_pedido:
                    # Buscando el stock especifico de ese producto y esa talla
                    stock_producto = Stock.objects.get(
                        id_producto = detalle.id_producto,
                        id_talla = detalle.id_talla
                    )

                    stock_producto.cantidad -= detalle.cantidad
                    stock_producto.save()
            elif accion == 'rechazar':
                pedido_a_actualizar.estado_pago = 'Cancelado'
                pedido_a_actualizar.estado_pedido = 'Cancelado'
            
            pedido_a_actualizar.save()
                
        return redirect('panel_simulador_banco')
    
    contexto = {
        'pedidos': pedidos_pendientes
    }
    return render(request, 'administracion/simulador.html', contexto)

# VISTA 11: CANCELAR PAGO (CLIENTE)
@login_required(login_url='iniciar_sesion')
def cancelar_pago_cliente(request, id_pedido):
    if request.method == 'POST':
        cliete_actual = Cliente.objects.get(usuario_id=request.user.id)
        pedido = get_object_or_404(Pedido, id_pedido=id_pedido, id_cliente=cliete_actual)

        # Solo permitir cancelar si el pago aun no ha sido aprobado
        if pedido.estado_pago == 'Pendiente':
            pedido.estado_pedido = 'En carrito'
            pedido.save()

            messages.success(request, "Pago cancelado. Los productos han vuelto al carrito.")
            return redirect('ver_carrito')
        else:
            messages.error(request, "No puedes cancelar un pedido que ya ha sido pagado.")
            return redirect('inicio_catalogo')
    return redirect('inicio_catalogo')