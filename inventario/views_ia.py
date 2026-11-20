import json
from io import BytesIO

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from PIL import Image, ImageOps, UnidentifiedImageError

from . import asistente
from .models import Productos
from .views import _datos_producto, contexto, login_requerido

SUGERENCIAS = [
    '¿Qué necesito para pintar una reja de metal?',
    '¿Qué broca uso para taladrar concreto?',
    '¿Qué materiales necesito para cambiar una llave de agua?',
    '¿Qué debo reabastecer?',
    '¿Dónde está el cemento?',
]


@login_requerido
def asistente_pagina(request):
    historial = request.session.get('chat_ia', [])
    return render(request, 'inventario/asistente.html', contexto(
        request, 'asistente', historial=historial, sugerencias=SUGERENCIAS,
        max_mensaje=asistente.MAX_MENSAJE))


@login_requerido
@require_POST
def api_asistente(request):
    try:
        datos = json.loads(request.body.decode('utf-8'))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({'respuesta': 'No entendí el mensaje. Intenta de nuevo.'}, status=400)

    mensaje = str(datos.get('mensaje', '')).strip()
    if not mensaje:
        return JsonResponse({'respuesta': 'Escribe tu pregunta.'}, status=400)
    if len(mensaje) > asistente.MAX_MENSAJE:
        return JsonResponse(
            {'respuesta': f'Tu mensaje es muy largo (máximo {asistente.MAX_MENSAJE} caracteres).'},
            status=400)
    if not asistente.dentro_del_limite(request.empleado.id_empleado):
        return JsonResponse(
            {'respuesta': 'Hiciste muchas preguntas seguidas. Espera un rato e inténtalo de nuevo.'},
            status=429)

    historial = request.session.get('chat_ia', [])
    respuesta = asistente.responder(request.empleado, historial, mensaje)

    historial.append({'r': 'u', 't': mensaje[:asistente.MAX_MENSAJE]})
    historial.append({'r': 'm', 't': respuesta[:1500]})
    request.session['chat_ia'] = historial[-16:]
    return JsonResponse({'respuesta': respuesta})


@login_requerido
@require_POST
def limpiar_asistente(request):
    request.session.pop('chat_ia', None)
    return JsonResponse({'ok': True})


# ---------------------------------------------------------------
# RECONOCER UNA HERRAMIENTA POR FOTO
# ---------------------------------------------------------------
def _preparar_imagen(archivo):
    """Valida que sea una imagen real y la deja como JPEG de hasta 1280 px."""
    if archivo.size > 8 * 1024 * 1024:
        raise ValueError('La foto pesa demasiado (máximo 8 MB).')
    try:
        imagen = Image.open(archivo)
        formato = imagen.format
        imagen.verify()
        archivo.seek(0)
        imagen = Image.open(archivo)
        imagen.load()
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        raise ValueError('El archivo no es una imagen válida.')
    if formato not in ('JPEG', 'PNG', 'WEBP'):
        raise ValueError('Usa una foto JPG, PNG o WEBP.')
    imagen = ImageOps.exif_transpose(imagen)
    if imagen.mode in ('RGBA', 'LA', 'P'):
        imagen = imagen.convert('RGBA')
        fondo = Image.new('RGB', imagen.size, (255, 255, 255))
        fondo.paste(imagen, mask=imagen.split()[-1])
        imagen = fondo
    else:
        imagen = imagen.convert('RGB')
    imagen.thumbnail((1280, 1280))
    salida = BytesIO()
    imagen.save(salida, format='JPEG', quality=85)
    return salida.getvalue()


def _coincidencias(palabras, es_gestor):
    """Busca en el inventario los productos que mejor coinciden con las palabras clave."""
    terminos = []
    for palabra in palabras:
        if len(palabra) < 3:
            continue
        terminos.append(palabra)
        if palabra.endswith('s') and len(palabra) > 4:
            terminos.append(palabra[:-1])
    puntos = {}
    for termino in terminos:
        encontrados = (Productos.objects.select_related('id_categoria', 'id_ubicacion')
                       .filter(Q(nombre_producto__icontains=termino)
                               | Q(id_categoria__nombre_categoria__icontains=termino)))
        for p in encontrados:
            en_nombre = termino.lower() in p.nombre_producto.lower()
            actual = puntos.setdefault(p.pk, [p, 0])
            actual[1] += 2 if en_nombre else 1
    candidatos = list(puntos.values())
    con_nombre = [c for c in candidatos if c[1] >= 2]
    elegidos = sorted(con_nombre or candidatos, key=lambda c: (-c[1], c[0].nombre_producto))[:5]
    return [_datos_producto(p, es_gestor) for p, _ in elegidos]


@login_requerido
def reconocer_pagina(request):
    return render(request, 'inventario/reconocer.html', contexto(request, 'reconocer'))


@login_requerido
@require_POST
def api_reconocer(request):
    archivo = request.FILES.get('foto')
    if archivo is None:
        return JsonResponse({'ok': False, 'mensaje': 'No se recibió ninguna foto.'}, status=400)
    if not asistente.dentro_del_limite(request.empleado.id_empleado, 'foto'):
        return JsonResponse({'ok': False, 'mensaje': 'Hiciste muchas consultas seguidas. '
                             'Espera un rato e inténtalo de nuevo.'}, status=429)
    try:
        jpeg = _preparar_imagen(archivo)
    except ValueError as problema:
        return JsonResponse({'ok': False, 'mensaje': str(problema)}, status=400)

    resultado = asistente.reconocer_imagen(jpeg)
    if resultado is None:
        return JsonResponse({'ok': False, 'mensaje': asistente.MENSAJE_OCUPADO}, status=503)

    es_gestor = request.empleado.rol in ('Administrador', 'Encargado')
    productos = []
    if resultado['nombre'] != 'no identificado':
        productos = _coincidencias(resultado['palabras_clave'], es_gestor)
    return JsonResponse({'ok': True, 'identificado': resultado, 'productos': productos})