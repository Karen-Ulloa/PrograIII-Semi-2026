"""
Módulo de reportes (archivo nuevo, no modifica views.py). Solo Administrador.

Reportes: ventas por día, productos más vendidos, valorización del inventario y mermas.
Cada reporte se puede ver en pantalla, exportar a Excel (?formato=xlsx) e imprimir / guardar como PDF.
"""
from datetime import datetime, time, timedelta
from decimal import Decimal

from django.db.models import Count, DecimalField, F, Sum
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.dateparse import parse_date

from .models import DetalleVenta, Productos, RegistrosMerma
from .reportes_util import XLSX, construir_excel, vista_resumen, vista_seccion
from .views import contexto, solo_admin

CERO = Decimal('0')
MAX_DIAS = 366
DIAS = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
PESTANAS = [
    ('ventas', 'Ventas por día', 'bi-calendar3'),
    ('productos', 'Más vendidos', 'bi-trophy'),
    ('inventario', 'Valorización', 'bi-cash-stack'),
    ('mermas', 'Mermas', 'bi-trash3'),
]
TIPOS = {clave for clave, _, _ in PESTANAS}
OPCIONES_TOP = (10, 20, 50, 100, 0)  # 0 = todos


def _fecha(d):
    return d.strftime('%d/%m/%Y')


def _total_lineas():
    return Sum(F('cantidad') * F('precio_venta'), output_field=DecimalField())


def _detalles_vendidos(inicio, fin):
    """
    Líneas de venta del período. Cuando exista la anulación de ventas (Punto 5),
    aquí se excluirán las ventas anuladas y todos los reportes se corrigen a la vez.
    """
    return DetalleVenta.objects.filter(id_venta__fecha_venta__gte=inicio,
                                       id_venta__fecha_venta__lt=fin)


def _fecha_param(texto):
    try:
        return parse_date(texto or '')
    except ValueError:
        return None


def _leer_rango(params):
    hoy = timezone.localdate()
    hasta = _fecha_param(params.get('hasta')) or hoy
    desde = _fecha_param(params.get('desde')) or hasta - timedelta(days=29)
    aviso = ''
    if desde > hasta:
        desde, hasta = hasta, desde
    if (hasta - desde).days > MAX_DIAS - 1:
        desde = hasta - timedelta(days=MAX_DIAS - 1)
        aviso = f'El rango máximo es de {MAX_DIAS} días; se ajustó la fecha inicial.'
    inicio = timezone.make_aware(datetime.combine(desde, time.min))
    fin = timezone.make_aware(datetime.combine(hasta + timedelta(days=1), time.min))
    return desde, hasta, inicio, fin, aviso


# ---------------------------------------------------------------
# 1. Ventas por día
# ---------------------------------------------------------------
def _reporte_ventas(desde, hasta, inicio, fin):
    # Se agrupa en Python (y no con TruncDate) para no depender de las tablas de zonas horarias de MySQL.
    dias = {}
    ventas, unidades, total = set(), 0, CERO
    lineas = _detalles_vendidos(inicio, fin).values_list(
        'id_venta_id', 'id_venta__fecha_venta', 'cantidad', 'precio_venta')
    for venta_id, fecha, cantidad, precio in lineas:
        dia = timezone.localtime(fecha).date()
        d = dias.setdefault(dia, {'ventas': set(), 'unidades': 0, 'total': CERO})
        d['ventas'].add(venta_id)
        d['unidades'] += cantidad
        d['total'] += cantidad * precio
        ventas.add(venta_id)
        unidades += cantidad
        total += cantidad * precio

    filas = [(_fecha(dia), DIAS[dia.weekday()], len(d['ventas']), d['unidades'], d['total'])
             for dia, d in sorted(dias.items())]
    por_dia = {
        'titulo': 'Ventas por día',
        'columnas': [('Fecha', 'texto'), ('Día', 'texto'), ('Ventas', 'num'),
                     ('Unidades', 'num'), ('Total vendido', 'dinero')],
        'filas': filas,
        'totales': ('Total', '', len(ventas), unidades, total) if filas else None,
    }

    metodos = (_detalles_vendidos(inicio, fin)
               .values('id_venta__id_metodo_pago__nombre_metodo')
               .annotate(n=Count('id_venta', distinct=True), unidades=Sum('cantidad'), total=_total_lineas())
               .order_by('-total'))
    filas_metodo = [(m['id_venta__id_metodo_pago__nombre_metodo'] or 'Sin método', m['n'],
                     m['unidades'], m['total']) for m in metodos]
    por_metodo = {
        'titulo': 'Ventas por método de pago',
        'columnas': [('Método de pago', 'texto'), ('Ventas', 'num'),
                     ('Unidades', 'num'), ('Total vendido', 'dinero')],
        'filas': filas_metodo,
        'totales': ('Total', len(ventas), unidades, total) if filas_metodo else None,
    }

    promedio = (total / len(ventas)).quantize(Decimal('0.01')) if ventas else CERO
    return {
        'titulo': 'Ventas por día',
        'subtitulo': f'Del {_fecha(desde)} al {_fecha(hasta)}',
        'resumen': [('Total vendido', total, 'dinero'), ('Ventas realizadas', len(ventas), 'num'),
                    ('Unidades vendidas', unidades, 'num'), ('Venta promedio', promedio, 'dinero')],
        'secciones': [por_dia, por_metodo],
        'nota': None,
    }


# ---------------------------------------------------------------
# 2. Productos más vendidos
# ---------------------------------------------------------------
def _reporte_productos(desde, hasta, inicio, fin, top):
    consulta = (_detalles_vendidos(inicio, fin)
                .values('id_producto', 'id_producto__nombre_producto',
                        'id_producto__id_categoria__nombre_categoria')
                .annotate(unidades=Sum('cantidad'), total=_total_lineas(),
                          n=Count('id_venta', distinct=True))
                .order_by('-unidades', '-total', 'id_producto__nombre_producto'))
    todos = list(consulta)
    elegidos = todos[:top] if top else todos
    filas = [(i, p['id_producto__nombre_producto'],
              p['id_producto__id_categoria__nombre_categoria'] or 'Sin categoría',
              p['unidades'], p['total'], p['n'])
             for i, p in enumerate(elegidos, start=1)]
    unidades = sum(p['unidades'] for p in todos)
    total = sum((p['total'] for p in todos), CERO)
    return {
        'titulo': 'Productos más vendidos',
        'subtitulo': f'Del {_fecha(desde)} al {_fecha(hasta)}',
        'resumen': [('Productos distintos vendidos', len(todos), 'num'),
                    ('Unidades vendidas', unidades, 'num'), ('Total vendido', total, 'dinero')],
        'secciones': [{
            'titulo': f'Los {len(filas)} productos con más unidades vendidas' if top else 'Todos los productos vendidos',
            'columnas': [('#', 'texto'), ('Producto', 'texto'), ('Categoría', 'texto'),
                         ('Unidades', 'num'), ('Total vendido', 'dinero'), ('Ventas', 'num')],
            'filas': filas, 'totales': None,
        }],
        'nota': None,
    }


# ---------------------------------------------------------------
# 3. Valorización del inventario (stock de hoy; no depende de las fechas)
# ---------------------------------------------------------------
def _reporte_inventario():
    productos = Productos.objects.select_related('id_categoria').order_by('nombre_producto')
    detalle, por_categoria = [], {}
    for p in productos:
        costo = p.stock * p.precio_compra
        venta = p.stock * p.precio_producto
        categoria = p.id_categoria.nombre_categoria if p.id_categoria else 'Sin categoría'
        detalle.append((p.nombre_producto, categoria, p.stock, p.precio_compra,
                        p.precio_producto, costo, venta))
        c = por_categoria.setdefault(categoria, {'productos': 0, 'unidades': 0, 'costo': CERO, 'venta': CERO})
        c['productos'] += 1
        c['unidades'] += p.stock
        c['costo'] += costo
        c['venta'] += venta

    detalle.sort(key=lambda f: (-f[5], f[0].lower()))
    unidades = sum(f[2] for f in detalle)
    costo_total = sum((f[5] for f in detalle), CERO)
    venta_total = sum((f[6] for f in detalle), CERO)

    filas_cat = [(nombre, c['productos'], c['unidades'], c['costo'], c['venta'], c['venta'] - c['costo'])
                 for nombre, c in sorted(por_categoria.items(), key=lambda kv: -kv[1]['costo'])]
    hoy = _fecha(timezone.localdate())
    return {
        'titulo': 'Valorización del inventario',
        'subtitulo': f'Stock al {hoy}',
        'resumen': [('Valor a precio de compra', costo_total, 'dinero'),
                    ('Valor a precio de venta', venta_total, 'dinero'),
                    ('Ganancia potencial', venta_total - costo_total, 'dinero'),
                    ('Productos / unidades', f'{len(detalle):,} / {unidades:,}', 'texto')],
        'secciones': [
            {'titulo': 'Resumen por categoría',
             'columnas': [('Categoría', 'texto'), ('Productos', 'num'), ('Unidades', 'num'),
                          ('Valor a compra', 'dinero'), ('Valor a venta', 'dinero'),
                          ('Ganancia potencial', 'dinero')],
             'filas': filas_cat,
             'totales': ('Total', len(detalle), unidades, costo_total, venta_total,
                         venta_total - costo_total) if filas_cat else None},
            {'titulo': 'Detalle por producto (de mayor a menor valor)',
             'columnas': [('Producto', 'texto'), ('Categoría', 'texto'), ('Stock', 'num'),
                          ('P. compra', 'dinero'), ('P. venta', 'dinero'),
                          ('Valor a compra', 'dinero'), ('Valor a venta', 'dinero')],
             'filas': detalle,
             'totales': ('Total', '', unidades, '', '', costo_total, venta_total) if detalle else None,
             'limite': 100},
        ],
        'nota': 'La valorización usa el stock actual y no depende de las fechas. '
                '"Ganancia potencial" es el valor a precio de venta menos el valor a precio de compra.',
    }


# ---------------------------------------------------------------
# 4. Mermas
# ---------------------------------------------------------------
def _reporte_mermas(desde, hasta, inicio, fin):
    registros = list(RegistrosMerma.objects.filter(fecha_merma__gte=inicio, fecha_merma__lt=fin)
                     .select_related('id_producto', 'id_motivo')
                     .order_by('-fecha_merma', '-id_merma'))
    detalle, por_motivo = [], {}
    unidades, costo_total = 0, CERO
    for m in registros:
        costo = m.id_producto.precio_compra * m.cantidad
        detalle.append((timezone.localtime(m.fecha_merma).strftime('%d/%m/%Y %H:%M'),
                        m.id_producto.nombre_producto, m.id_motivo.descripcion, m.cantidad, costo))
        c = por_motivo.setdefault(m.id_motivo.descripcion, {'n': 0, 'unidades': 0, 'costo': CERO})
        c['n'] += 1
        c['unidades'] += m.cantidad
        c['costo'] += costo
        unidades += m.cantidad
        costo_total += costo

    filas_motivo = [(motivo, c['n'], c['unidades'], c['costo'])
                    for motivo, c in sorted(por_motivo.items(), key=lambda kv: -kv[1]['costo'])]
    return {
        'titulo': 'Reporte de mermas',
        'subtitulo': f'Del {_fecha(desde)} al {_fecha(hasta)}',
        'resumen': [('Costo total de mermas', costo_total, 'dinero'),
                    ('Unidades dadas de baja', unidades, 'num'), ('Registros', len(registros), 'num')],
        'secciones': [
            {'titulo': 'Mermas por motivo',
             'columnas': [('Motivo', 'texto'), ('Registros', 'num'), ('Unidades', 'num'), ('Costo', 'dinero')],
             'filas': filas_motivo,
             'totales': ('Total', len(registros), unidades, costo_total) if filas_motivo else None},
            {'titulo': 'Detalle de mermas',
             'columnas': [('Fecha y hora', 'texto'), ('Producto', 'texto'), ('Motivo', 'texto'),
                          ('Cantidad', 'num'), ('Costo', 'dinero')],
             'filas': detalle,
             'totales': ('Total', '', '', unidades, costo_total) if detalle else None,
             'limite': 200},
        ],
        'nota': 'El costo se calcula con el precio de compra actual de cada producto.',
    }


# ---------------------------------------------------------------
# Vista
# ---------------------------------------------------------------
@solo_admin
def reportes(request):
    tipo = request.GET.get('tipo') if request.GET.get('tipo') in TIPOS else 'ventas'
    desde, hasta, inicio, fin, aviso = _leer_rango(request.GET)
    try:
        top = int(request.GET.get('top', 20))
    except ValueError:
        top = 20
    if top not in OPCIONES_TOP:
        top = 20

    if tipo == 'ventas':
        reporte = _reporte_ventas(desde, hasta, inicio, fin)
    elif tipo == 'productos':
        reporte = _reporte_productos(desde, hasta, inicio, fin, top)
    elif tipo == 'inventario':
        reporte = _reporte_inventario()
    else:
        reporte = _reporte_mermas(desde, hasta, inicio, fin)

    generado = timezone.localtime().strftime('%d/%m/%Y %H:%M')

    if request.GET.get('formato') == 'xlsx':
        sufijo = _fecha(timezone.localdate()).replace('/', '-') if tipo == 'inventario' \
            else f'{desde.isoformat()}_a_{hasta.isoformat()}'
        respuesta = HttpResponse(construir_excel(reporte, generado), content_type=XLSX)
        respuesta['Content-Disposition'] = f'attachment; filename="reporte_{tipo}_{sufijo}.xlsx"'
        return respuesta

    return render(request, 'inventario/reportes.html', contexto(
        request, 'reportes',
        tipo=tipo, pestanas=PESTANAS, desde=desde.isoformat(), hasta=hasta.isoformat(),
        top=top, opciones_top=OPCIONES_TOP, aviso=aviso, generado=generado,
        titulo=reporte['titulo'], subtitulo=reporte['subtitulo'], nota=reporte['nota'],
        resumen=vista_resumen(reporte['resumen']),
        secciones=[vista_seccion(s) for s in reporte['secciones']]))