"""
Importación masiva de productos desde Excel/CSV (archivo nuevo, no modifica views.py).

Dos modos, que no se mezclan:
  nuevos     -> solo CREA productos. Si el producto ya existe, esa fila es un error.
  actualizar -> solo MODIFICA productos. Si no existe, esa fila es un error.
Permisos: Administrador y Encargado (los mismos que pueden crear/editar productos).
"""
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render

from .importador import (
    ErrorArchivo, generar_exportacion, generar_plantilla, leer_archivo, validar_fila,
)
from .models import Categorias, Productos, Ubicaciones
from .views import contexto, gestor

TIPOS = ('nuevos', 'actualizar')
MODOS_STOCK = ('mantener', 'reemplazar', 'sumar')
MAX_ERRORES_MOSTRADOS = 200
XLSX = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


def _procesar(nombre_archivo, contenido, tipo, modo_stock):
    """Lee, valida y guarda. Las filas buenas se guardan; las malas se reportan."""
    filas = leer_archivo(nombre_archivo, contenido, tipo)

    errores = []   # [(fila, producto, mensaje)]
    validas = []   # [(fila, datos)]
    nombres_vistos, codigos_vistos = {}, {}
    for numero, valores in filas:
        datos, problemas = validar_fila(valores, tipo)
        if datos is not None:
            if datos['nombre'] and datos['nombre'].lower() in nombres_vistos:
                problemas.append(f'El producto está repetido en el archivo (ya aparece en la fila '
                                 f'{nombres_vistos[datos["nombre"].lower()]}).')
            if datos['codigo'] and datos['codigo'] in codigos_vistos:
                problemas.append(f'El código de barras está repetido en el archivo (ya aparece en '
                                 f'la fila {codigos_vistos[datos["codigo"]]}).')
        if problemas:
            etiqueta = ((datos or {}).get('nombre') or str(valores.get('nombre_producto') or '')
                        or str(valores.get('codigo_barras') or ''))
            errores.append((numero, etiqueta, ' '.join(problemas)))
            continue
        if datos['nombre']:
            nombres_vistos[datos['nombre'].lower()] = numero
        if datos['codigo']:
            codigos_vistos[datos['codigo']] = numero
        validas.append((numero, datos))

    creados = actualizados = 0
    categorias_nuevas, ubicaciones_nuevas = [], 0

    with transaction.atomic():
        categorias = {c.nombre_categoria.lower(): c for c in Categorias.objects.all()}
        ubicaciones = {}

        def obtener_categoria(nombre):
            clave = nombre.lower()
            categoria = categorias.get(clave)
            if categoria is None:
                categoria = Categorias.objects.create(nombre_categoria=nombre)
                categorias[clave] = categoria
                categorias_nuevas.append(nombre)
            return categoria

        def obtener_ubicacion(partes):
            nonlocal ubicaciones_nuevas
            bodega, pasillo, estante, nivel = partes
            clave = (bodega.lower(), pasillo.lower(), estante.lower(), nivel.lower())
            ubicacion = ubicaciones.get(clave)
            if ubicacion is None:
                ubicacion = Ubicaciones.objects.filter(
                    bodega__iexact=bodega, pasillo__iexact=pasillo,
                    estante__iexact=estante, nivel__iexact=nivel).first()
                if ubicacion is None:
                    ubicacion = Ubicaciones.objects.create(
                        bodega=bodega, pasillo=pasillo, estante=estante, nivel=nivel, detalle='')
                    ubicaciones_nuevas += 1
                ubicaciones[clave] = ubicacion
            return ubicacion

        for numero, d in validas:
            etiqueta = d['nombre'] or d['codigo']

            # --- buscar el producto: primero por código de barras y luego por nombre
            producto = None
            if d['codigo']:
                producto = Productos.objects.filter(codigo_barras=d['codigo']).first()
            por_codigo = producto is not None
            if producto is None and d['nombre']:
                producto = Productos.objects.filter(nombre_producto__iexact=d['nombre']).first()


            if tipo == 'nuevos':
                if producto is not None:
                    errores.append((numero, etiqueta,
                                    'Ese producto ya existe (mismo nombre o código de barras). '
                                    'Para modificarlo usa la pestaña "Actualizar productos".'))
                    continue
                Productos.objects.create(
                    nombre_producto=d['nombre'], id_categoria=obtener_categoria(d['categoria']),
                    id_ubicacion=obtener_ubicacion(d['ubicacion']) if d['ubicacion'] else None,
                    precio_producto=d['precio_venta'],
                    precio_compra=d['precio_compra'] if d['precio_compra'] is not None else 0,
                    stock=d['stock'] if d['stock'] is not None else 0,
                    stock_minimo=d['stock_minimo'] if d['stock_minimo'] is not None else 5,
                    codigo_barras=d['codigo'])
                creados += 1
                continue

            if producto is None:
                errores.append((numero, etiqueta,
                                'No existe un producto con ese código o nombre. Si es un producto '
                                'nuevo, súbelo en la pestaña "Productos nuevos".'))
                continue
            if d['codigo'] and producto.codigo_barras and producto.codigo_barras != d['codigo']:
                errores.append((numero, etiqueta,
                                f'Ese producto ya tiene otro código de barras ({producto.codigo_barras}).'))
                continue
            if (por_codigo and d['nombre'] and producto.nombre_producto.lower() != d['nombre'].lower()
                    and Productos.objects.filter(nombre_producto__iexact=d['nombre'])
                    .exclude(pk=producto.pk).exists()):
                errores.append((numero, etiqueta,
                                'No se puede cambiar el nombre: ya hay otro producto con ese nombre.'))
                continue

            if d['nombre']:
                producto.nombre_producto = d['nombre']
            if d['categoria']:
                producto.id_categoria = obtener_categoria(d['categoria'])
            if d['precio_venta'] is not None:
                producto.precio_producto = d['precio_venta']
            if d['precio_compra'] is not None:
                producto.precio_compra = d['precio_compra']
            if d['stock_minimo'] is not None:
                producto.stock_minimo = d['stock_minimo']
            if d['ubicacion']:
                producto.id_ubicacion = obtener_ubicacion(d['ubicacion'])
            if d['codigo'] and not producto.codigo_barras:
                producto.codigo_barras = d['codigo']
            if d['stock'] is not None:
                if modo_stock == 'reemplazar':
                    producto.stock = d['stock']
                elif modo_stock == 'sumar':
                    producto.stock += d['stock']
            producto.save()
            actualizados += 1

    errores.sort(key=lambda e: e[0])
    return {
        'tipo': tipo,
        'total': len(filas),
        'creados': creados,
        'actualizados': actualizados,
        'n_errores': len(errores),
        'errores': errores[:MAX_ERRORES_MOSTRADOS],
        'errores_ocultos': max(len(errores) - MAX_ERRORES_MOSTRADOS, 0),
        'categorias_nuevas': categorias_nuevas,
        'ubicaciones_nuevas': ubicaciones_nuevas,
    }


@gestor
def importar_productos(request):
    resultado = None
    tab = request.GET.get('tab') if request.GET.get('tab') in TIPOS else 'nuevos'
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        tab = tipo if tipo in TIPOS else 'nuevos'
        modo = request.POST.get('modo_stock', 'mantener')
        if modo not in MODOS_STOCK:
            modo = 'mantener'
        archivo = request.FILES.get('archivo')
        if not archivo:
            messages.error(request, 'Selecciona un archivo .xlsx o .csv.')
        else:
            try:
                resultado = _procesar(archivo.name, archivo.read(), tab, modo)
            except ErrorArchivo as problema:
                messages.error(request, str(problema))
    return render(request, 'inventario/importar_productos.html', contexto(
        request, 'productos', resultado=resultado, tab=tab))


@gestor
def plantilla_productos(request):
    respuesta = HttpResponse(generar_plantilla(), content_type=XLSX)
    respuesta['Content-Disposition'] = 'attachment; filename="plantilla_productos_nuevos.xlsx"'
    return respuesta


@gestor
def exportar_productos(request):
    """Descarga los productos actuales para editarlos y subirlos en el modo "actualizar"."""
    filas = []
    consulta = Productos.objects.select_related('id_categoria', 'id_ubicacion').order_by('nombre_producto')
    for p in consulta:
        u = p.id_ubicacion
        # Las ubicaciones antiguas sin bodega se dejan vacías (vacío = no cambiar al volver a subir).
        usa_ubicacion = u is not None and u.bodega
        filas.append([
            p.nombre_producto,
            p.id_categoria.nombre_categoria if p.id_categoria else '',
            float(p.precio_compra), float(p.precio_producto),
            p.stock, p.stock_minimo, p.codigo_barras or '',
            u.bodega if usa_ubicacion else '', u.pasillo if usa_ubicacion else '',
            u.estante if usa_ubicacion else '', u.nivel if usa_ubicacion else '',
        ])
    respuesta = HttpResponse(generar_exportacion(filas), content_type=XLSX)
    respuesta['Content-Disposition'] = 'attachment; filename="productos_actuales.xlsx"'
    return respuesta