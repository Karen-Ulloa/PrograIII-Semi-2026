"""
Rutas de la API REST (archivo nuevo). Se montan en config/urls.py bajo 'api/v1/'.
Se usa SimpleRouter (no DefaultRouter) para no exponer una raíz con navegador de DRF.
"""
from django.urls import path
from rest_framework.routers import SimpleRouter

from . import api_views

router = SimpleRouter()
router.register('productos', api_views.ProductoViewSet, basename='api-productos')
router.register('clientes', api_views.ClienteViewSet, basename='api-clientes')
router.register('proveedores', api_views.ProveedorViewSet, basename='api-proveedores')
router.register('ventas', api_views.VentaViewSet, basename='api-ventas')
router.register('mermas', api_views.MermaViewSet, basename='api-mermas')
router.register('ordenes-compra', api_views.OrdenCompraViewSet, basename='api-ordenes')

urlpatterns = [
    path('prueba/', api_views.api_prueba, name='api_prueba'),
    path('catalogos/', api_views.CatalogosView.as_view(), name='api-catalogos'),
] + router.urls