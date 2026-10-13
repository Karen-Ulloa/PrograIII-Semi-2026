"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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
from django.urls import path
from inventario import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio, name='inicio'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('recuperar/', views.recuperar, name='recuperar'),
    path('verificar/', views.verificar_codigo, name='verificar'),
    path('restablecer/', views.restablecer, name='restablecer'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('terminos/', views.terminos, name='terminos'),
    path('api/sugerir-usuario/', views.sugerir_usuario, name='sugerir_usuario'),
    path('productos/', views.productos_lista, name='productos'),
    path('productos/nuevo/', views.producto_form, name='producto_nuevo'),
    path('productos/<int:pk>/editar/', views.producto_form, name='producto_editar'),
    path('productos/<int:pk>/eliminar/', views.producto_eliminar, name='producto_eliminar'),
    path('api/productos/', views.api_productos, name='api_productos'),
    path('empleados/', views.empleados_lista, name='empleados'),
    path('empleados/nuevo/', views.empleado_form, name='empleado_nuevo'),
    path('empleados/<int:pk>/editar/', views.empleado_form, name='empleado_editar'),
    path('empleados/<int:pk>/estado/', views.empleado_estado, name='empleado_estado'),
    path('empleados/<int:pk>/eliminar/', views.empleado_eliminar, name='empleado_eliminar'),
    path('perfil/', views.perfil, name='perfil'),
    path('proveedores/', views.proveedores_lista, name='proveedores'),
    path('proveedores/nuevo/', views.proveedor_form, name='proveedor_nuevo'),
    path('proveedores/<int:pk>/editar/', views.proveedor_form, name='proveedor_editar'),
    path('proveedores/<int:pk>/eliminar/', views.proveedor_eliminar, name='proveedor_eliminar'),
]
