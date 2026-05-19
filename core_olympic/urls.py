"""
URL configuration for core_olympic project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('admin/', admin.site.urls),
    # Conectando los modulos
    path('', include('administracion.urls')),
    path('inventario/', include('inventario.urls')),
    path('ventas/', include('ventas.urls')),
    path('nosotros/', TemplateView.as_view(template_name="nosotros.html"), name='nosotros'),
    path('ubicacion', TemplateView.as_view(template_name="ubicacion.html"), name='ubicacion'),
    path('terminos-condiciones/', TemplateView.as_view(template_name="terminos_condiciones.html"), name='terminos_condiciones'),
    # path('api/verificar-pago/<int:id_pedido>/', views.verificar_estado_pago, name='verificar_estado_pago'),
    # path('admin-oculto/banco/', views.panel_simulador_banco, name='panel_simulador_banco'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)