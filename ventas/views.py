from django.shortcuts import render, redirect, get_object_or_404
from .models import Cliente, Pedido, DetallePedido
from inventario.models import Producto, Stock, Talla, Categoria
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Create your views here.

# VISTA 1: LISTAR CATALOGO DE PRODUCTOS
def inicio_catalogo(request):
    palabra_clave = request.GET.get('buscar')

    categoria_id = request.GET.get('categoria')
    
    # Iniciando la consulta base con la suma del stock total
    # Recordando que 'stock__cantidad' es la ruta: Modelo Stock -> campo cantidad
    consulta = Producto.objects.annotate(stock_total=Sum('stock__cantidad'))

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
        'categoria_actual' : categoria_id
    }

    return render(request, 'ventas/catalogo_productos.html', contexto)

# VISTA 2: AGREGAR AL CARRITO
@login_required
def agregar_al_carrito(request, producto_id):
    producto = Producto.objects.get(pk=producto_id)
    
    if request.method == 'POST':
        # Pedimos la canasta actual de la sesion
        # Si el cliente no es nuevo y no tiene canasta, le damos una canasta vacia
        carrito = request.session.get('carrito', {}) # El "{}" crea un carrito nuevo si el cliente no lo tiene
        talla_id = request.POST.get('talla_id')
        talla_obj = Talla.objects.get(id_talla=talla_id)
        id_str = f"{producto.id_producto}_{talla_id}"

        # Capturamos la cantidad, si algo falla, ponemos 1
        try:
            nueva_cantidad = int(request.POST.get('cantidad'))
        except ValueError:
            nueva_cantidad = 1

        if id_str in carrito:
            if nueva_cantidad > 0:
                carrito[id_str]['cantidad'] += nueva_cantidad
                carrito[id_str]['subtotal'] += nueva_cantidad * carrito[id_str]['precio']
            else:
                # Si el cliente escribe 0 eliminamos ese producto del carrito
                del carrito[id_str]
        else:
            if nueva_cantidad > 0:
                carrito[id_str] = {
                    'producto_id': producto.id_producto,
                    'nombre': producto.nombre,
                    'talla_id': talla_id,
                    'talla_nombre': talla_obj.nombre_talla,
                    'precio': float(producto.precio),
                    'cantidad': nueva_cantidad,
                    'subtotal': float(producto.precio) * nueva_cantidad
                }    
        # Guardando la canasta actualizada de vuelta en la sesion
        request.session['carrito'] = carrito
        # Avisando a Django de que hubo un cambio en la sesion
        request.session.modified = True

        messages.success(request, f"¡Se agregó {producto.nombre} a tu carrito!")

    return redirect('inicio_catalogo')

# VISTA 3: VER CARRITO
def ver_carrito(request):
    # Obteniendo la canasta de la sesion
    carrito = request.session.get('carrito', {})

    total_a_pagar = 0

    for item in carrito.values():
        total_a_pagar += item['subtotal']

    contexto = {
        'carrito': carrito.values(), # Mandando solo los valores del diccionario
        'total': total_a_pagar
    }
    return render(request, 'ventas/carrito.html', contexto)

# VISTA 4: VACIAR CARRITO
def vaciar_carrito(request):
    if request.method == 'POST':
        request.session.get('carrito', {})
        request.session['carrito'] = {}
    return redirect('inicio_catalogo')

# VISTA 5: PROCESAR COMPRAR
@login_required(login_url='iniciar_sesion')
def procesar_compra(request):
    carrito = request.session.get('carrito', {})

    # transaction.atomic() asegura que o se guarda todo (pedidos, detalles y resta de stock) o no se guarda nada
    # Previene que un error deje un pedido a medias o cobre sin descontar stock
    try:
        with transaction.atomic():
            # 1. Identificar al cliente que esta comprando
            cliente_actual = Cliente.objects.get(usuario_id=request.user.id)

            # 2. Crear el registro general del Pedido (El Pedido)
            nuevo_pedido = Pedido.objects.create(
                id_cliente = cliente_actual,
                fecha = timezone.now(),
                estado_pedido = 'Pendiente',
                estado_pago = 'Pendiente'
            )

            # 3. Recorrer el carrito, descontar stock y crear los detalles
            for key, item in carrito.items():
                producto = Producto.objects.get(id_producto=item['producto_id'])

                # Obtenemos el objeto de la talla exacta que esta en el carrito
                talla_obj = Talla.objects.get(id_talla=item['talla_id'])

                # Buscamos el stock en la tabla correcta y lo bloqueamos para evitar compras simultaneas
                stock_producto = Stock.objects.select_for_update().filter(id_producto=producto, id_talla=talla_obj).first()

                if not stock_producto or stock_producto.cantidad < item['cantidad']:
                    raise ValueError(f"Lo sentimos, no hay suficiente stock de {producto.nombre}.")
                stock_producto.cantidad -= item['cantidad']
                stock_producto.save()

                DetallePedido.objects.create(
                    id_pedido = nuevo_pedido,
                    id_producto = producto,
                    id_talla = talla_obj,
                    cantidad = item['cantidad'],
                    precio_unitario = item['precio']
                )
            
            # 4. Limpiamos el carrito porque la compra fue un exito
            del request.session['carrito']
            request.session.modified = True

            messages.success(request, "¡Tu pedido ha sido registrado con éxito!")
            return redirect('ver_recibo', id_pedido=nuevo_pedido.id_pedido)
    
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('ver_carrito')
    except Exception as e:
        messages.error(request, f"Hubo un error al procesar tu compra: {e}")
        return redirect('ver_carrito')
    
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

        pedido = get_object_or_404(Pedido, pk=id_pedido)
        pedido.estado_pedido = nuevo_estado
        pedido.save()

        return redirect('panel_pedidos')
    
    # 2. FILTRAR PEDIDOS
    filtro_estado = request.GET.get('estado')

    consulta_pedidos = Pedido.objects.all().order_by('-id_pedido')

    if filtro_estado:
        consulta_pedidos = consulta_pedidos.filter(estado_pedido=filtro_estado)
    
    contexto = {
        'pedidos': consulta_pedidos,
        'estado_actual': filtro_estado # Para saber que boton pintar de rojo
    }

    return render(request, 'ventas/panel_pedidos.html', contexto)