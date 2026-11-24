"""Rutas de Categorías, Ubicaciones, Importación, Reportes y Anulación de ventas (archivo nuevo). Se incluyen desde config/urls.py."""
from django.urls import path

from . import views_catalogos as v
from . import views_importar as imp
from . import views_reportes as rep
from . import views_anular as anu

urlpatterns = [
    path('categorias/', v.categorias_lista, name='categorias'),
    path('categorias/nueva/', v.categoria_form, name='categoria_nueva'),
    path('categorias/<int:pk>/editar/', v.categoria_form, name='categoria_editar'),
    path('categorias/<int:pk>/eliminar/', v.categoria_eliminar, name='categoria_eliminar'),
    path('ubicaciones/', v.ubicaciones_lista, name='ubicaciones'),
    path('ubicaciones/nueva/', v.ubicacion_form, name='ubicacion_nueva'),
    path('ubicaciones/<int:pk>/editar/', v.ubicacion_form, name='ubicacion_editar'),
    path('ubicaciones/<int:pk>/eliminar/', v.ubicacion_eliminar, name='ubicacion_eliminar'),
    path('importar/', imp.importar_productos, name='importar'),
    path('importar/plantilla/', imp.plantilla_productos, name='plantilla_productos'),
    path('importar/exportar/', imp.exportar_productos, name='exportar_productos'),
    path('reportes/', rep.reportes, name='reportes'),
    path('ventas/<int:pk>/anular/', anu.venta_anular, name='venta_anular'),
]