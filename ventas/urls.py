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
]