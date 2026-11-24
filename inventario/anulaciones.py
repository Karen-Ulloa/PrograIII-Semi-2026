"""
Anulación de ventas (archivo nuevo). La usan la pantalla web y la API.

Reglas:
  - Cualquier usuario puede anular SUS propias ventas; el Administrador puede anular cualquiera.
  - Siempre hace falta el código de autorización (el mismo de "Código admin") y un motivo.
  - Tras 5 códigos incorrectos seguidos, esa cuenta queda bloqueada 15 minutos para anular.
  - Anular NO borra la venta: queda marcada (fecha, quién la anuló, motivo) y las cantidades
    vuelven al stock. Todo ocurre en una sola transacción.
"""
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from .models import DetalleVenta, Productos, Ventas
from .views import codigo_admin_correcto, obtener_config

MAX_INTENTOS = 5
SEGUNDOS_BLOQUEO = 15 * 60


class VentaNoExiste(Exception):
    pass


class AnulacionInvalida(ValueError):
    pass


class VentaYaAnulada(AnulacionInvalida):
    pass


class CodigoIncorrecto(AnulacionInvalida):
    pass


class CodigoBloqueado(AnulacionInvalida):
    pass


class SinPermisoAnular(AnulacionInvalida):
    pass


def _verificar_codigo(empleado, codigo):
    if not obtener_config('codigo_admin_hash'):
        raise AnulacionInvalida('Todavía no hay un código de autorización. El Administrador debe '
                                'crearlo en el menú "Código admin".')
    clave = f'anular_fallos_{empleado.pk}'
    if cache.get(clave, 0) >= MAX_INTENTOS:
        raise CodigoBloqueado('Demasiados intentos con el código. Inténtalo de nuevo en 15 minutos.')
    if not codigo_admin_correcto(codigo or ''):
        cache.add(clave, 0, SEGUNDOS_BLOQUEO)
        try:
            cache.incr(clave)
        except ValueError:
            cache.set(clave, 1, SEGUNDOS_BLOQUEO)
        raise CodigoIncorrecto('El código de autorización no es correcto.')
    cache.delete(clave)


def anular_venta(venta_id, empleado, motivo, codigo):
    motivo = ' '.join((motivo or '').split())
    if len(motivo) < 3:
        raise AnulacionInvalida('Escribe el motivo de la anulación (mínimo 3 caracteres).')
    if len(motivo) > 200:
        raise AnulacionInvalida('El motivo es demasiado largo (máximo 200 caracteres).')
    _verificar_codigo(empleado, codigo)

    with transaction.atomic():
        venta = Ventas.objects.select_for_update().filter(pk=venta_id).first()
        if venta is None:
            raise VentaNoExiste()
        if empleado.rol != 'Administrador' and venta.id_empleado_id != empleado.pk:
            raise SinPermisoAnular('Solo puedes anular las ventas que registraste tú.')
        if venta.anulada:
            raise VentaYaAnulada('Esa venta ya está anulada.')

        cantidades = {}
        for d in DetalleVenta.objects.filter(id_venta=venta):
            cantidades[d.id_producto_id] = cantidades.get(d.id_producto_id, 0) + d.cantidad
        for producto in Productos.objects.select_for_update().filter(pk__in=cantidades.keys()):
            producto.stock += cantidades[producto.pk]
            producto.save(update_fields=['stock'])

        venta.anulada = True
        venta.fecha_anulacion = timezone.now()
        venta.id_empleado_anula = empleado
        venta.motivo_anulacion = motivo
        venta.save(update_fields=['anulada', 'fecha_anulacion', 'id_empleado_anula', 'motivo_anulacion'])
    return venta