from django.urls import path
from . import views

urlpatterns = [
    path('panel-gestion/', views.panel_gestion, name='panel_gestion'),
    path('crear_productos/', views.crear_producto, name='crear_producto'),
    path('eliminar_producto/<int:id_producto>/', views.eliminar_producto, name='eliminar_producto'),
    path("editar_producto/<int:id_producto>/", views.editar_producto, name="editar_producto"),
    path("crear_proveedor/", views.crear_proveedor, name="crear_proveedor"),
    path("eliminar_proveedor/<int:id_proveedor>/", views.eliminar_proveedor, name='eliminar_proveedor'),
    path('editar_proveedor/<int:id_proveedor>/', views.editar_proveedor, name='editar_proveedor'),
    path('categorias/', views.categorias, name='categorias'),
    path('crear_categoria/', views.crear_categoria, name='crear_categoria'),
    path('eliminar_categoria/<int:id_categoria>/', views.eliminar_categoria, name='eliminar_categoria'),
    path('editar_categoria/<int:id_categoria>/', views.editar_categoria, name="editar_categoria"),
]