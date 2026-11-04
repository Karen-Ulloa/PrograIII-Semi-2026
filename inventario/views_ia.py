import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from . import asistente
from .views import contexto, login_requerido

SUGERENCIAS = [
    '¿Qué productos están bajo el mínimo?',
    '¿Qué debo reabastecer?',
    'Dame un resumen del inventario',
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