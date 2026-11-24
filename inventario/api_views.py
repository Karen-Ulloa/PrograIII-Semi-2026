"""
Vistas de la API REST (archivo nuevo). No modifica views.py ni views_ia.py.

Permisos por rol (mismos que la web):
  Productos   : ver = todos | crear/editar = Admin y Encargado | eliminar = Admin
  Clientes    : solo Admin
  Proveedores : ver/crear/editar = Admin y Encargado | eliminar = Admin
  Ventas      : ver y registrar = todos (Empleado y Encargado solo ven las suyas; Admin ve todas)
                anular = cada quien las suyas (Admin cualquiera), siempre con el código de autorización
  Mermas      : ver y registrar = todos | anular (DELETE) = Admin
  Órdenes     : Admin y Encargado (crear, ver, recibir, cancelar)
"""
from datetime import timedelta

from django.db import transaction
from django.db.models import F, Q
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from .api_auth import (
    ADMIN, GESTORES, SOLO_ADMIN, TODOS, EmpleadoSessionAuthentication, PorRol,
)
from .anulaciones import (
    AnulacionInvalida, CodigoBloqueado, CodigoIncorrecto, SinPermisoAnular, VentaNoExiste,
    VentaYaAnulada, anular_venta,
)
from .api_serializers import (
    ClienteSerializer, MermaSerializer, OrdenCrearSerializer, OrdenSerializer,
    ProductoSerializer, ProveedorSerializer, VentaCrearSerializer, VentaSerializer,
)
from .models import (
    Categorias, Clientes, DetalleCompra, DetalleVenta, OrdenesCompra, ProductoProveedo,
    Productos, Proveedores, RegistrosMerma, Ubicaciones, Ventas,
)
from .views import _metodos_pago, _motivos_merma, contexto, login_requerido


class PaginaEstandar(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class ApiBase:
    """Configuración común: sesión del sistema + permisos por rol + solo JSON."""
    authentication_classes = [EmpleadoSessionAuthentication]
    permission_classes = [PorRol]
    renderer_classes = [JSONRenderer]
    pagination_class = PaginaEstandar
    roles_default = SOLO_ADMIN


def _filtrar_periodo(qs, campo, periodo):
    inicio = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
    if periodo == 'hoy':
        return qs.filter(**{f'{campo}__gte': inicio})
    if periodo == 'semana':
        return qs.filter(**{f'{campo}__gte': inicio - timedelta(days=6)})
    return qs


def _conflicto(mensaje):
    return Response({'detail': mensaje}, status=409)


# ---------------------------------------------------------------
# CATÁLOGOS (ids necesarios para crear ventas, mermas, productos...)
# ---------------------------------------------------------------
class CatalogosView(ApiBase, APIView):
    roles_default = TODOS

    def get(self, request):
        return Response({
            'categorias': list(Categorias.objects.order_by('nombre_categoria')
                               .values('id_categoria', 'nombre_categoria')),
            'ubicaciones': [{'id_ubicacion': u.pk, 'texto': u.texto_corto()}
                            for u in Ubicaciones.objects.order_by('bodega', 'pasillo', 'estante', 'nivel')],
            'metodos_pago': list(_metodos_pago().values('id_metodo_pago', 'nombre_metodo')),
            'motivos_merma': list(_motivos_merma().values('id_motivo', 'descripcion')),
        })


# ---------------------------------------------------------------
# PRODUCTOS
# ---------------------------------------------------------------
class ProductoViewSet(ApiBase, viewsets.ModelViewSet):
    """Filtros: ?q=texto  ?categoria=ID  ?alerta=1 (stock en o bajo el mínimo)"""
    serializer_class = ProductoSerializer
    roles_por_accion = {
        'list': TODOS, 'retrieve': TODOS,
        'create': GESTORES, 'update': GESTORES, 'partial_update': GESTORES,
        'destroy': SOLO_ADMIN,
    }

    def get_queryset(self):
        qs = Productos.objects.select_related('id_categoria', 'id_ubicacion').order_by('nombre_producto')
        params = self.request.query_params
        q = params.get('q', '').strip()
        if q:
            qs = qs.filter(Q(nombre_producto__icontains=q) |
                           Q(id_categoria__nombre_categoria__icontains=q) |
                           Q(codigo_barras__iexact=q))
        if params.get('categoria', '').isdigit():
            qs = qs.filter(id_categoria_id=int(params['categoria']))
        if params.get('alerta') in ('1', 'true'):
            qs = qs.filter(stock__lte=F('stock_minimo'))
        return qs

    def destroy(self, request, *args, **kwargs):
        p = self.get_object()
        if (DetalleVenta.objects.filter(id_producto=p).exists()
                or DetalleCompra.objects.filter(id_producto=p).exists()
                or RegistrosMerma.objects.filter(id_producto=p).exists()):
            return _conflicto('No se puede eliminar: el producto tiene ventas, compras o mermas '
                              'registradas. Puedes dejar su stock en 0.')
        return super().destroy(request, *args, **kwargs)


# ---------------------------------------------------------------
# CLIENTES (solo administrador)
# ---------------------------------------------------------------
class ClienteViewSet(ApiBase, viewsets.ModelViewSet):
    """Filtro: ?q=texto"""
    serializer_class = ClienteSerializer

    def get_queryset(self):
        qs = Clientes.objects.order_by('nombre')
        q = self.request.query_params.get('q', '').strip()
        if q:
            qs = qs.filter(Q(nombre__icontains=q) | Q(telefono__icontains=q))
        return qs

    def destroy(self, request, *args, **kwargs):
        cliente = self.get_object()
        if Ventas.objects.filter(id_cliente=cliente).exists():
            return _conflicto('No se puede eliminar: el cliente tiene ventas registradas.')
        return super().destroy(request, *args, **kwargs)


# ---------------------------------------------------------------
# PROVEEDORES
# ---------------------------------------------------------------
class ProveedorViewSet(ApiBase, viewsets.ModelViewSet):
    """Filtro: ?q=texto"""
    serializer_class = ProveedorSerializer
    roles_por_accion = {
        'list': GESTORES, 'retrieve': GESTORES, 'create': GESTORES,
        'update': GESTORES, 'partial_update': GESTORES, 'destroy': SOLO_ADMIN,
    }

    def get_queryset(self):
        qs = Proveedores.objects.order_by('nombre_proveedor')
        q = self.request.query_params.get('q', '').strip()
        if q:
            qs = qs.filter(Q(nombre_proveedor__icontains=q) | Q(contacto_proveedor__icontains=q))
        return qs

    def destroy(self, request, *args, **kwargs):
        prov = self.get_object()
        if (OrdenesCompra.objects.filter(id_proveedor=prov).exists()
                or ProductoProveedo.objects.filter(id_proveedor=prov).exists()):
            return _conflicto('No se puede eliminar: el proveedor tiene órdenes de compra '
                              'o productos asociados.')
        return super().destroy(request, *args, **kwargs)


# ---------------------------------------------------------------
# VENTAS (listar, ver y registrar; anular se hará en la tarea 5)
# ---------------------------------------------------------------
class VentaViewSet(ApiBase, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    """Filtro: ?periodo=hoy|semana|todas"""
    serializer_class = VentaSerializer
    roles_por_accion = {'list': TODOS, 'retrieve': TODOS, 'create': TODOS, 'anular': TODOS}

    def get_queryset(self):
        qs = (Ventas.objects
              .select_related('id_cliente', 'id_empleado', 'id_metodo_pago')
              .prefetch_related('detalleventa_set__id_producto')
              .order_by('-fecha_venta'))
        user = self.request.user
        if user.rol != ADMIN:  # cada persona ve solo sus ventas
            qs = qs.filter(id_empleado_id=user.empleado.id_empleado)
        return _filtrar_periodo(qs, 'fecha_venta', self.request.query_params.get('periodo', 'todas'))

    def create(self, request, *args, **kwargs):
        entrada = VentaCrearSerializer(data=request.data, context=self.get_serializer_context())
        entrada.is_valid(raise_exception=True)
        venta = entrada.save()
        venta = self.get_queryset().get(pk=venta.pk)
        return Response(VentaSerializer(venta, context=self.get_serializer_context()).data, status=201)

    @action(detail=True, methods=['post'])
    def anular(self, request, pk=None):
        """Anula la venta y devuelve las cantidades al stock. Cuerpo JSON: motivo y codigo."""
        try:
            anular_venta(pk, request.user.empleado, request.data.get('motivo', ''),
                         request.data.get('codigo', ''))
        except VentaNoExiste:
            raise NotFound('Esa venta no existe.')
        except VentaYaAnulada as problema:
            return _conflicto(str(problema))
        except CodigoBloqueado as problema:
            return Response({'detail': str(problema)}, status=429)
        except (CodigoIncorrecto, SinPermisoAnular) as problema:
            return Response({'detail': str(problema)}, status=403)
        except AnulacionInvalida as problema:
            return Response({'detail': str(problema)}, status=400)
        venta = self.get_queryset().get(pk=pk)
        return Response(VentaSerializer(venta, context=self.get_serializer_context()).data)


# ---------------------------------------------------------------
# MERMAS (anular = DELETE, devuelve el stock)
# ---------------------------------------------------------------
class MermaViewSet(ApiBase, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                   mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Filtro: ?periodo=hoy|semana|todas"""
    serializer_class = MermaSerializer
    roles_por_accion = {'list': TODOS, 'retrieve': TODOS, 'create': TODOS, 'destroy': SOLO_ADMIN}

    def get_queryset(self):
        qs = RegistrosMerma.objects.select_related('id_producto', 'id_motivo').order_by('-fecha_merma', '-id_merma')
        return _filtrar_periodo(qs, 'fecha_merma', self.request.query_params.get('periodo', 'todas'))

    def destroy(self, request, pk=None):
        with transaction.atomic():
            merma = RegistrosMerma.objects.select_for_update().filter(pk=pk).first()
            if merma is None:
                raise NotFound('Ese registro de merma ya no existe.')
            producto = Productos.objects.select_for_update().get(pk=merma.id_producto_id)
            producto.stock += merma.cantidad
            producto.save(update_fields=['stock'])
            merma.delete()
        return Response(status=204)


# ---------------------------------------------------------------
# ÓRDENES DE COMPRA (Admin y Encargado)
# ---------------------------------------------------------------
class OrdenCompraViewSet(ApiBase, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    """Filtro: ?estado=Pendiente|Recibida|Cancelada.  Acciones: POST .../recibir/ y .../cancelar/"""
    serializer_class = OrdenSerializer
    roles_default = GESTORES

    def get_queryset(self):
        qs = (OrdenesCompra.objects.select_related('id_proveedor')
              .prefetch_related('detallecompra_set__id_producto').order_by('-fecha_compra'))
        estado = self.request.query_params.get('estado')
        if estado in ('Pendiente', 'Recibida', 'Cancelada'):
            qs = qs.filter(estado=estado)
        return qs

    def _responder(self, pk):
        orden = (OrdenesCompra.objects.select_related('id_proveedor')
                 .prefetch_related('detallecompra_set__id_producto').get(pk=pk))
        return Response(OrdenSerializer(orden, context=self.get_serializer_context()).data)

    def create(self, request, *args, **kwargs):
        entrada = OrdenCrearSerializer(data=request.data, context=self.get_serializer_context())
        entrada.is_valid(raise_exception=True)
        orden = entrada.save()
        respuesta = self._responder(orden.pk)
        respuesta.status_code = 201
        return respuesta

    @action(detail=True, methods=['post'])
    def recibir(self, request, pk=None):
        with transaction.atomic():
            orden = OrdenesCompra.objects.select_for_update().filter(pk=pk).first()
            if orden is None:
                raise NotFound('Esa orden no existe.')
            if orden.estado != 'Pendiente':
                return _conflicto('Esa orden ya fue procesada.')
            for d in DetalleCompra.objects.filter(id_compra=orden):
                producto = Productos.objects.select_for_update().get(pk=d.id_producto_id)
                producto.stock += d.cantidad
                producto.save(update_fields=['stock'])
            orden.estado = 'Recibida'
            orden.fecha_recepcion = timezone.now()
            orden.save(update_fields=['estado', 'fecha_recepcion'])
        return self._responder(orden.pk)

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        with transaction.atomic():
            orden = OrdenesCompra.objects.select_for_update().filter(pk=pk).first()
            if orden is None:
                raise NotFound('Esa orden no existe.')
            if orden.estado != 'Pendiente':
                return _conflicto('Solo se pueden cancelar órdenes pendientes.')
            orden.estado = 'Cancelada'
            orden.save(update_fields=['estado'])
        return self._responder(orden.pk)


# ---------------------------------------------------------------
# PÁGINA WEB DE PRUEBA DE ENDPOINTS (cualquier rol con sesión iniciada)
# ---------------------------------------------------------------
@ensure_csrf_cookie
@login_requerido
def api_prueba(request):
    return render(request, 'inventario/api_prueba.html', contexto(request, 'api'))