from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Producto, Stock, Categoria, Proveedor, ProductoProveedor, Talla
from .forms import ProductoForm
from django.db.models import Sum

# Create your views here.

# VISTA 1: PANEL DE GESTION (PRODUCTOS)
@login_required
def panel_gestion(request):
    if request.user.rol not in ['admin', 'vendedor']:
        return redirect('iniciar_sesion')
    
    # Le decimos a Django: "Trae todos los productos y anotales una nueva columna virtual
    # llama 'stock_total' que sea la suma de todas sus cantidades en la tabla stock"
    productos = Producto.objects.annotate(
        stock_total = Sum('stock__cantidad')
    ).order_by('precio')
    alertas_stock = Stock.objects.select_related('id_producto', 'id_talla').filter(cantidad__lt=20)

    contexto = {
        'productos' : productos,
        'productos_bajo_stock' : alertas_stock
    }

    return render(request, 'inventario/panel_gestion_inventario.html', contexto)

# VISTA 2: PANEL DE GESTION (CREACION PRODUCTOS)
@login_required
def crear_producto(request):
    if request.user.rol not in ['admin', 'vendedor']:
        return redirect('iniciar_sesion')
    
    if request.method == 'POST':
        nombre_ingresado = request.POST.get('nuevo_nombre')
        descripcion_ingresada = request.POST.get('nueva_descripcion')
        precio_ingresado = request.POST.get('nuevo_precio')
        categoria_id = request.POST.get('nueva_categoria')
        proveedor_id = request.POST.get('nuevo_proveedor')

        # Buscando los objetos reales en la base de datos usando esos IDs
        categoria_obj = get_object_or_404(Categoria, pk=categoria_id)
        proveedor_obj = get_object_or_404(Proveedor, pk=proveedor_id)

        nuevo_producto = Producto.objects.create(
            nombre = nombre_ingresado,
            descripcion = descripcion_ingresada,
            precio = precio_ingresado,
            id_categoria = categoria_obj
        )

        # Guardando la relacion en la tabla intermedia
        ProductoProveedor.objects.create(
            id_producto = nuevo_producto,
            id_proveedor = proveedor_obj
        )

        return redirect('panel_gestion')
    
    # Trayendo los registros para mostrar en los menus desplegables
    categorias = Categoria.objects.all()
    proveedores = Proveedor.objects.all()

    contexto = {
        'categorias' : categorias,
        'proveedores' : proveedores
    }

    return render(request, 'inventario/crear_productos.html', contexto)

# VISTA 3: PANEL DE GESTION (ELIMINAR PRODUCTOS)
@login_required
def eliminar_producto(request, id_producto):
    if request.user.rol not in ['admin', 'vendedor']:
        return redirect('iniciar_sesion')

    if request.method == 'POST':
        producto_a_borrar = Producto.objects.get(pk=id_producto)

        # Buscar si existe stock asociado a este producto y lo borramos primero
        Stock.objects.filter(id_producto=producto_a_borrar).delete()

        # Buscar si existe producto proveedor asociado a este producto y lo borramos primero
        ProductoProveedor.objects.filter(id_producto=producto_a_borrar).delete()
        producto_a_borrar.delete()
    return redirect('panel_gestion')

# VISTA 4: PANEL DE GESTION (EDITAR PRODUCTOS)
@login_required
def editar_producto(request, id_producto):
    if request.user.rol not in ['admin', 'vendedor']:
        return redirect('iniciar_sesion')
    
    producto_a_editar = Producto.objects.get(pk=id_producto)

    if request.method == 'POST':
        producto_a_editar.nombre = request.POST.get('nombre')
        producto_a_editar.descripcion = request.POST.get('descripcion')
        producto_a_editar.precio = request.POST.get('precio')

        # Obtenemos los nuevos IDs de categoria y proveedor
        cat_id = request.POST.get('categoria')
        producto_a_editar.id_categoria = get_object_or_404(Categoria, pk=cat_id)
        producto_a_editar.save()

        # Actualizando Proveedores (Tabla Intermedia)
        proveedores_ids = request.POST.getlist('proveedores')

        ProductoProveedor.objects.filter(id_producto=producto_a_editar).delete()
        
        for prov_id in proveedores_ids:
            prov_obj = get_object_or_404(Proveedor, pk=prov_id)
            ProductoProveedor.objects.create(id_producto=producto_a_editar, id_proveedor=prov_obj)

        # Actualizando el Stock Dinamico por Tallas
        tallas_disponibles = Talla.objects.all()
        for talla in tallas_disponibles:
            cantidad = request.POST.get(f'talla_{talla.id_talla}')

            if cantidad and int(cantidad) > 0:
                # Actualizamos si existe o creamos si es nuevo
                stock_obj, created = Stock.objects.get_or_create(
                    id_producto=producto_a_editar,
                    id_talla=talla,
                    defaults={
                        'cantidad': cantidad,
                        'stock_minimo' : 5
                    }
                )
                if not created:
                    stock_obj.cantidad = cantidad
                    stock_obj.save()
            else:
                Stock.objects.filter(id_producto=producto_a_editar, id_talla=talla).delete()
        
        return redirect('panel_gestion')
    
    categorias = Categoria.objects.all()
    proveedores = Proveedor.objects.all()
    tallas = Talla.objects.all()

    proveedores_actuales = ProductoProveedor.objects.filter(id_producto=producto_a_editar).values_list('id_proveedor', flat=True)

    stock_actual = Stock.objects.filter(id_producto=producto_a_editar)
    datos_tallas = []
    for t in tallas:
        # Buscando si ya tiene stock de esta talla, si no, le mandamos 0
        stock_item = stock_actual.filter(id_talla=t).first()
        cantidad_actual = stock_item.cantidad if stock_item else 0
        datos_tallas.append({
            'id' : t.id_talla,
            'nombre' : t.nombre_talla,
            'cantidad' : cantidad_actual
        })
    contexto = {
        'producto' : producto_a_editar,
        'categorias' : categorias,
        'proveedores' : proveedores,
        'proveedores_actuales' : proveedores_actuales,
        'datos_tallas' : datos_tallas
    }

    return render(request, 'inventario/edicion_productos.html', contexto)

# VISTA 5: PANEL DE GESTION (CREAR PROVEEDORES)
@login_required
def crear_proveedor(request):
    if request.user.rol not in ['admin', 'vendedor']:
        return redirect('iniciar_sesion')
    
    if request.method == 'POST':
        nombre_ingresado = request.POST.get('nombre')
        telefono_ingresado = request.POST.get('telefono')
        email_ingresado = request.POST.get('email')

        Proveedor.objects.create(
            nombre_empresa = nombre_ingresado,
            telefono = telefono_ingresado,
            email = email_ingresado
        )

        messages.success(request, "Proveedor creado con exito!")

        return redirect('panel_gestion')
    
    proveedores = Proveedor.objects.all().order_by('nombre_empresa')

    contexto = {
        'proveedores': proveedores
    }

    return render(request, 'inventario/proveedores.html', contexto)

# VISTA 5: PANEL DE GESTION (ELIMINAR PROVEEDORES)
@login_required
def eliminar_proveedor(request, id_proveedor):
    if request.user.rol not in ['admin', 'vendedor']:
        return redirect('iniciar_sesion')
    
    if request.method == 'POST':
        proveedor_a_borrar = Proveedor.objects.get(pk=id_proveedor)
        proveedor_a_borrar.delete()

    return redirect('panel_gestion')

# VISTA 6: PANEL DE GESTION (EDITAR PROVEEDORES)
@login_required
def editar_proveedor(request, id_proveedor):
    if request.user.rol not in ['admin', 'vendedor']:
        return redirect('iniciar_sesion')
    
    proveedor_a_editar = Proveedor.objects.get(pk=id_proveedor)

    if request.method == 'POST':
        proveedor_a_editar.nombre_empresa = request.POST.get('nombre_editar')
        proveedor_a_editar.telefono = request.POST.get('telefono_editar')
        proveedor_a_editar.email = request.POST.get('email_editar')

        proveedor_a_editar.save()
    
    return redirect('panel_gestion')

# VISTA 7: PANEL DE GESTION (CATEGORIAS)
@login_required
def categorias(request):
    categorias = Categoria.objects.all()

    contexto = {
        'categorias': categorias
    }

    return render(request, 'inventario/categorias.html', contexto)

# VISTA 8: PANEL DE GESTION (CREAR CATEGORIAS)
@login_required
def crear_categoria(request):
    if request.user.rol not in ['admin', 'vendedor']:
        return redirect('categorias')
    
    if request.method == 'POST':
        nombre_ingresado = request.POST.get('nombre')

        Categoria.objects.create(
            nombre = nombre_ingresado
        )

        messages.success(request, "Categoria creada con exito!")

    return redirect('categorias')

# VISTA 8: PANEL DE GESTION (ELIMINAR CATEGORIAS)
@login_required
def eliminar_categoria(request, id_categoria):
    if request.user.rol not in ['admin', 'vendedor']:
        return redirect('categorias')
    
    if request.method == 'POST':
        categoria_a_eliminar = Categoria.objects.get(pk=id_categoria)
        categoria_a_eliminar.delete()

    return redirect('categorias')

# VISTA 9: PANEL DE GESTION (EDITAR CATEGORIAS)
@login_required
def editar_categoria(request, id_categoria):
    if request.user.rol not in ['admin', 'vendedor']:
        return redirect('categorias')
    
    categoria_a_editar = Categoria.objects.get(pk=id_categoria)

    if request.method == 'POST':
        categoria_a_editar.nombre = request.POST.get('nuevo_nombre')
        categoria_a_editar.save()
    
    return redirect('categorias')