from django.urls import path
from . import views

urlpatterns = [
    path('productos/', views.inicio_catalogo, name='inicio_catalogo'),
    path('agregar_carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_carrito'),
    path('mi-carrito/', views.ver_carrito, name='ver_carrito'),
    path('vaciar_carrito/', views.vaciar_carrito, name='vaciar_carrito'),
    path('procesar_compra/', views.procesar_compra, name='procesar_compra'),
    path('recibo/<int:id_pedido>/', views.ver_recibo, name='ver_recibo'),
    path('panel_pedidos/', views.panel_pedidos, name='panel_pedidos'),
    path('pago/qr/<int:id_pedido>/', views.pantalla_pago_qr, name='pantalla_pago_qr'),
    path('api/verificar-pago/<int:id_pedido>/', views.verificar_estado_pago, name='verificar_estado_pago'),
    path('admin-oculto/banco/', views.panel_simulador_banco, name='panel_simulador_banco'),
    path('cancelar-pago/<int:id_pedido>/', views.cancelar_pago_cliente, name='cancelar_pago_cliente'),
]