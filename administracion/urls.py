from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.iniciar_sesion, name='iniciar_sesion'),
    path('logout/', views.cerrar_sesion, name='cerrar_sesion'),
    path('panel-admin/registrar', views.registrar_usuario_admin, name='registrar_usuarios'),
    path('panel-admin/usuarios', views.listar_usuarios, name='listar_usuarios'),
    path('panel-gestion/eliminar_usuario/<int:id_usuario>/', views.eliminar_usuarios, name="eliminar_usuarios"),
    path('panel-gestion/editar_usuario/<int:id_usuario>/', views.editar_usuarios, name='editar_usuarios'),
    path('signup/', views.signup_cliente, name='signup_cliente'),
    path('perfil/<int:id_cliente>/', views.edicion_perfil_usuario, name='edicion_perfil_usuario'),
]