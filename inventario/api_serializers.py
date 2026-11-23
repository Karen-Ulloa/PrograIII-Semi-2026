"""
Serializers de la API REST (archivo nuevo).
Replican las validaciones y reglas de negocio de los formularios de views.py.
"""
import re
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from .api_auth import ADMIN, GESTORES
from .models import (
    Categorias, Clientes, DetalleCompra, DetalleVenta, MetodosPago, MotivosMerma,
    OrdenesCompra, Productos, Proveedores, RegistrosMerma, Ubicaciones, Ventas,
)

CODIGO_VALIDO = re.compile(r'[A-Za-z0-9._\-]{3,50}')


def _rol(serializer):
    request = serializer.context.get('request')
    return getattr(getattr(request, 'user', None), 'rol', None)


class ProductoSerializer(serializers.ModelSerializer):
    id_categoria = serializers.PrimaryKeyRelatedField(queryset=Categorias.objects.all())
    id_ubicacion = serializers.PrimaryKeyRelatedField(
        queryset=Ubicaciones.objects.all(), required=False, allow_null=True)
    categoria = serializers.SerializerMethodField()
    ubicacion = serializers.SerializerMethodField()

    class Meta:
        model = Productos
        fields = ['id_producto', 'nombre_producto', 'id_categoria', 'categoria',
                  'id_ubicacion', 'ubicacion', 'precio_compra', 'precio_producto',
                  'stock', 'stock_minimo', 'codigo_barras']
        extra_kwargs = {
            'precio_compra': {'min_value': Decimal('0')},
            'precio_producto': {'min_value': Decimal('0')},
            'stock': {'min_value': 0},
            'stock_minimo': {'min_value': 0},
            # la unicidad se valida abajo (permite vacío = sin código)
            'codigo_barras': {'validators': [], 'required': False,
                              'allow_null': True, 'allow_blank': True},
        }

    def get_categoria(self, p):
        return p.id_categoria.nombre_categoria if p.id_categoria else None

    def get_ubicacion(self, p):
        return p.id_ubicacion.texto_corto() if p.id_ubicacion else None

    def validate_nombre_producto(self, valor):
        nombre = valor.strip()
        repetido = Productos.objects.filter(nombre_producto__iexact=nombre)
        if self.instance:
            repetido = repetido.exclude(pk=self.instance.pk)
        if repetido.exists():
            raise serializers.ValidationError('Ya existe un producto con ese nombre.')
        return nombre

    def validate_codigo_barras(self, valor):
        codigo = (valor or '').strip()
        if not codigo:
            return None
        if not CODIGO_VALIDO.fullmatch(codigo):
            raise serializers.ValidationError(
                'Usa solo letras, números, punto, guion o guion bajo (de 3 a 50 caracteres).')
        repetido = Productos.objects.filter(codigo_barras=codigo)
        if self.instance:
            repetido = repetido.exclude(pk=self.instance.pk)
        if repetido.exists():
            raise serializers.ValidationError('Ese código ya está asignado a otro producto.')
        return codigo

    def to_representation(self, instance):
        datos = super().to_representation(instance)
        if _rol(self) not in GESTORES:  # el costo solo lo ven Administrador y Encargado
            datos.pop('precio_compra', None)
        return datos


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clientes
        fields = ['id_cliente', 'nombre', 'telefono']

    def validate_nombre(self, valor):
        nombre = ' '.join(valor.split())
        if len(nombre) < 3:
            raise serializers.ValidationError('Escribe el nombre del cliente.')
        return nombre

    def validate_telefono(self, valor):
        digitos = re.sub(r'\D', '', valor)
        if len(digitos) != 8:
            raise serializers.ValidationError('El teléfono debe tener 8 dígitos.')
        telefono = f'{digitos[:4]}-{digitos[4:]}'
        repetido = Clientes.objects.filter(telefono=telefono)
        if self.instance:
            repetido = repetido.exclude(pk=self.instance.pk)
        if repetido.exists():
            raise serializers.ValidationError('Ya existe un cliente con ese teléfono.')
        return telefono


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedores
        fields = ['id_proveedor', 'nombre_proveedor', 'contacto_proveedor']

    def validate_nombre_proveedor(self, valor):
        nombre = valor.strip()
        repetido = Proveedores.objects.filter(nombre_proveedor__iexact=nombre)
        if self.instance:
            repetido = repetido.exclude(pk=self.instance.pk)
        if repetido.exists():
            raise serializers.ValidationError('Ya existe un proveedor con ese nombre.')
        return nombre

    def validate_contacto_proveedor(self, valor):
        return valor.strip()


class DetalleVentaSerializer(serializers.ModelSerializer):
    producto = serializers.CharField(source='id_producto.nombre_producto', read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = DetalleVenta
        fields = ['id_producto', 'producto', 'cantidad', 'precio_venta', 'subtotal']

    def get_subtotal(self, d):
        return d.cantidad * d.precio_venta


class VentaSerializer(serializers.ModelSerializer):
    """Salida (lectura) de una venta con su detalle."""
    cliente = serializers.SerializerMethodField()
    empleado = serializers.SerializerMethodField()
    metodo_pago = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    detalles = DetalleVentaSerializer(source='detalleventa_set', many=True, read_only=True)

    class Meta:
        model = Ventas
        fields = ['id_venta', 'fecha_venta', 'id_cliente', 'cliente', 'id_empleado',
                  'empleado', 'id_metodo_pago', 'metodo_pago', 'total', 'detalles']

    def get_cliente(self, v):
        return v.id_cliente.nombre if v.id_cliente else None

    def get_empleado(self, v):
        e = v.id_empleado
        return f'{e.nombre} {e.apellido}'.strip() if e else None

    def get_metodo_pago(self, v):
        return v.id_metodo_pago.nombre_metodo if v.id_metodo_pago else None

    def get_total(self, v):
        return sum((d.cantidad * d.precio_venta for d in v.detalleventa_set.all()), Decimal('0'))

    def to_representation(self, instance):
        datos = super().to_representation(instance)
        if _rol(self) != ADMIN:  # los datos de clientes los maneja solo el administrador
            datos.pop('id_cliente', None)
            datos.pop('cliente', None)
        return datos


class LineaVentaSerializer(serializers.Serializer):
    id_producto = serializers.IntegerField()
    cantidad = serializers.IntegerField(min_value=1, max_value=9999)


class VentaCrearSerializer(serializers.Serializer):
    """Entrada para registrar una venta. El precio siempre sale de la base de datos."""
    id_cliente = serializers.PrimaryKeyRelatedField(
        queryset=Clientes.objects.all(), required=False, allow_null=True)
    id_metodo_pago = serializers.PrimaryKeyRelatedField(queryset=MetodosPago.objects.all())
    lineas = LineaVentaSerializer(many=True, allow_empty=False)

    def validate_lineas(self, lineas):
        if len(lineas) > 100:
            raise serializers.ValidationError('Hay demasiados productos en una sola venta.')
        return lineas

    def validate(self, datos):
        if datos.get('id_cliente') and _rol(self) != ADMIN:
            raise serializers.ValidationError(
                {'id_cliente': 'Solo el administrador puede asignar un cliente a la venta.'})
        return datos

    def create(self, datos):
        empleado = self.context['request'].user.empleado
        lineas = {}
        for linea in datos['lineas']:
            pid = linea['id_producto']
            lineas[pid] = lineas.get(pid, 0) + linea['cantidad']

        with transaction.atomic():
            productos = {p.pk: p for p in
                         Productos.objects.select_for_update().filter(pk__in=lineas.keys())}
            if len(productos) != len(lineas):
                raise serializers.ValidationError({'lineas': 'Uno de los productos no existe.'})
            for pid, cantidad in lineas.items():
                p = productos[pid]
                if p.stock < cantidad:
                    raise serializers.ValidationError({'lineas': (
                        f'No hay suficiente stock de "{p.nombre_producto}" (disponible: {p.stock}).')})

            venta = Ventas.objects.create(
                id_cliente=datos.get('id_cliente'), id_empleado=empleado,
                id_metodo_pago=datos['id_metodo_pago'], fecha_venta=timezone.now())
            for pid, cantidad in lineas.items():
                p = productos[pid]
                DetalleVenta.objects.create(
                    id_venta=venta, id_producto=p, cantidad=cantidad,
                    precio_venta=p.precio_producto)
                p.stock -= cantidad
                p.save(update_fields=['stock'])
        return venta


class MermaSerializer(serializers.ModelSerializer):
    """Lectura y registro de una merma (un producto y un motivo por registro)."""
    producto = serializers.SerializerMethodField()
    motivo = serializers.SerializerMethodField()
    costo = serializers.SerializerMethodField()

    class Meta:
        model = RegistrosMerma
        fields = ['id_merma', 'id_producto', 'producto', 'id_motivo', 'motivo',
                  'cantidad', 'fecha_merma', 'costo']
        read_only_fields = ['fecha_merma']
        extra_kwargs = {'cantidad': {'min_value': 1, 'max_value': 9999}}

    def get_producto(self, m):
        return m.id_producto.nombre_producto

    def get_motivo(self, m):
        return m.id_motivo.descripcion

    def get_costo(self, m):
        return m.id_producto.precio_compra * m.cantidad

    def to_representation(self, instance):
        datos = super().to_representation(instance)
        if _rol(self) not in GESTORES:
            datos.pop('costo', None)
        return datos

    def create(self, datos):
        with transaction.atomic():
            p = Productos.objects.select_for_update().get(pk=datos['id_producto'].pk)
            if p.stock < datos['cantidad']:
                raise serializers.ValidationError({'cantidad': (
                    f'No puedes dar de baja {datos["cantidad"]} de "{p.nombre_producto}": '
                    f'en el sistema hay {p.stock}.')})
            merma = RegistrosMerma.objects.create(
                id_producto=p, id_motivo=datos['id_motivo'],
                cantidad=datos['cantidad'], fecha_merma=timezone.now())
            p.stock -= datos['cantidad']
            p.save(update_fields=['stock'])
        return merma


class DetalleCompraSerializer(serializers.ModelSerializer):
    producto = serializers.CharField(source='id_producto.nombre_producto', read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = DetalleCompra
        fields = ['id_producto', 'producto', 'cantidad', 'precio_compra', 'subtotal']

    def get_subtotal(self, d):
        return d.cantidad * d.precio_compra


class OrdenSerializer(serializers.ModelSerializer):
    """Salida (lectura) de una orden de compra con su detalle."""
    proveedor = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    detalles = DetalleCompraSerializer(source='detallecompra_set', many=True, read_only=True)

    class Meta:
        model = OrdenesCompra
        fields = ['id_compra', 'id_proveedor', 'proveedor', 'fecha_compra', 'estado',
                  'fecha_recepcion', 'total', 'detalles']

    def get_proveedor(self, o):
        return o.id_proveedor.nombre_proveedor

    def get_total(self, o):
        return sum((d.cantidad * d.precio_compra for d in o.detallecompra_set.all()), Decimal('0'))


class LineaOrdenSerializer(serializers.Serializer):
    id_producto = serializers.IntegerField()
    cantidad = serializers.IntegerField(min_value=1, max_value=99999)
    precio_compra = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal('0'))


class OrdenCrearSerializer(serializers.Serializer):
    id_proveedor = serializers.PrimaryKeyRelatedField(queryset=Proveedores.objects.all())
    lineas = LineaOrdenSerializer(many=True, allow_empty=False)

    def validate_lineas(self, lineas):
        if len(lineas) > 100:
            raise serializers.ValidationError('Hay demasiados productos en una sola orden.')
        return lineas

    def create(self, datos):
        lineas = {}
        for linea in datos['lineas']:
            pid = linea['id_producto']
            anterior = lineas.get(pid, (0, None))[0]
            lineas[pid] = (anterior + linea['cantidad'], linea['precio_compra'])

        with transaction.atomic():
            productos = {p.pk: p for p in Productos.objects.filter(pk__in=lineas.keys())}
            if len(productos) != len(lineas):
                raise serializers.ValidationError({'lineas': 'Uno de los productos no existe.'})
            orden = OrdenesCompra.objects.create(
                id_proveedor=datos['id_proveedor'], fecha_compra=timezone.now(),
                estado='Pendiente')
            for pid, (cantidad, precio) in lineas.items():
                DetalleCompra.objects.create(
                    id_compra=orden, id_producto=productos[pid],
                    cantidad=cantidad, precio_compra=precio)
        return orden