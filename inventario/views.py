from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password, make_password
from .models import Empleados
from django.http import JsonResponse
from django.conf import settings
from django.core.mail import send_mail
from requests.exceptions import RequestException
from twilio.base.exceptions import TwilioException
from twilio.rest import Client
import logging
import secrets
import re
import hmac
from smtplib import SMTPException
import time
from django.db.models import Sum, F, DecimalField
from django.utils import timezone
from .models import Productos, Ventas, DetalleVenta, OrdenesCompra

logger = logging.getLogger(__name__)
def validar_password(p):
    faltan = []
    if len(p) < 8:
        faltan.append('mínimo 8 caracteres')
    if not re.search(r'[A-Z]', p):
        faltan.append('una mayúscula')
    if not re.search(r'[a-z]', p):
        faltan.append('una minúscula')
    if not re.search(r'\d', p):
        faltan.append('un número')
    if not re.search(r'[^A-Za-z0-9]', p):
        faltan.append('un símbolo (por ejemplo ! @ # $ %)')
    if faltan:
        return 'La contraseña necesita: ' + ', '.join(faltan) + '.'
    return None


def _telefono_e164(telefono):
    digitos = re.sub(r'\D', '', telefono)
    codigo_pais = re.sub(r'\D', '', settings.TWILIO_DEFAULT_COUNTRY_CODE)

    if len(digitos) == 8:
        return f'+{codigo_pais}{digitos}'
    if len(digitos) == len(codigo_pais) + 8 and digitos.startswith(codigo_pais):
        return f'+{digitos}'
    return None


def _buscar_empleado_por_telefono(telefono):
    digitos = re.sub(r'\D', '', telefono)
    codigo_pais = re.sub(r'\D', '', settings.TWILIO_DEFAULT_COUNTRY_CODE)
    if digitos.startswith(codigo_pais) and len(digitos) == len(codigo_pais) + 8:
        digitos = digitos[len(codigo_pais):]

    opciones = {telefono.strip(), digitos}
    if len(digitos) == 8:
        opciones.add(f'{digitos[:4]}-{digitos[4:]}')
        opciones.add(f'+{codigo_pais}{digitos}')
    return Empleados.objects.filter(telefono__in=opciones).first()

def inicio(request):
    return render(request, 'inventario/inicio.html')

def registro(request):
    if request.method == 'POST':
        datos = request.POST.copy()
        datos['password'] = ''
        datos['password2'] = ''

        def volver(error, limpiar=None):
            if limpiar:
                datos[limpiar] = ''
            return render(request, 'inventario/registro.html', {'error': error, 'datos': datos})

        password = request.POST.get('password', '')
        if password != request.POST.get('password2', ''):
            return volver('Las contraseñas no coinciden.')

        error_pw = validar_password(password)
        if error_pw:
            return volver(error_pw)

        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        correo = request.POST.get('correo', '').strip().lower()
        usuario = request.POST.get('usuario', '').strip().lower()
        rol = request.POST.get('rol', 'Empleado')
        if rol not in ('Administrador', 'Empleado'):
            rol = 'Empleado'

        if Empleados.objects.filter(correo=correo).exists():
            return volver(f'El correo {correo} ya está registrado.', limpiar='correo')

        if usuario:
            if not re.fullmatch(r'[a-z0-9._]{3,30}', usuario):
                return volver('El usuario solo puede tener letras, números, punto y guion bajo (mínimo 3).', limpiar='usuario')
            if Empleados.objects.filter(usuario=usuario).exists():
                return volver(f'El usuario {usuario} ya está en uso. Elige otro.')
            usuario_final = usuario
        else:
            n = re.sub(r'[^a-z]', '', nombre.lower().split()[0]) if nombre else ''
            a = re.sub(r'[^a-z]', '', apellido.lower().split()[0]) if apellido else ''
            usuario_base = f"{n}.{a}" if n and a else correo.split('@')[0]
            usuario_final = usuario_base
            c = 1
            while Empleados.objects.filter(usuario=usuario_final).exists():
                usuario_final = f"{usuario_base}{c}"
                c += 1

        Empleados.objects.create(
            nombre=nombre, apellido=apellido,
            direccion=request.POST.get('direccion'), correo=correo,
            telefono=request.POST.get('telefono'), usuario=usuario_final,
            password=make_password(password),
            rol=rol
        )
        return redirect('login')
    return render(request, 'inventario/registro.html', {'datos': {}})


def sugerir_usuario(request):
    nombre = request.GET.get('nombre', '').strip().lower()
    apellido = request.GET.get('apellido', '').strip().lower()
    actual = request.GET.get('usuario', '').strip().lower()

    n = re.sub(r'[^a-z]', '', nombre.split()[0]) if nombre else ''
    a = re.sub(r'[^a-z]', '', apellido.split()[0]) if apellido else ''
    if not n or not a:
        return JsonResponse({'sugerencias': [], 'base': '', 'ocupado': False})

    base = f"{n}.{a}"
    ocupado = Empleados.objects.filter(usuario=(actual or base)).exists()

    sugerencias = []
    if ocupado:
        posibles = [f"{n}{a}", f"{n}_{a}", f"{base}1", f"{base}2", f"{base}123"]
        for cand in posibles:
            if cand != actual and not Empleados.objects.filter(usuario=cand).exists():
                sugerencias.append(cand)
            if len(sugerencias) >= 3:
                break

    return JsonResponse({'sugerencias': sugerencias, 'base': base, 'ocupado': ocupado})


def login_view(request):
    if request.method == 'POST':
        try:
            dato = request.POST.get('usuario', '').strip()
            emp = (Empleados.objects.filter(usuario=dato).first()
                   or Empleados.objects.filter(correo__iexact=dato).first())
            if emp is None:
                raise ValueError('Usuario no encontrado')
            password = request.POST.get('password', '')
            if not check_password(password, emp.password):
                if not hmac.compare_digest(password, emp.password):
                    raise ValueError('Contraseña incorrecta')
                emp.password = make_password(password)
                emp.save(update_fields=['password'])
            request.session['empleado_id'] = emp.id_empleado
            return redirect('dashboard')
        except ValueError:
            return render(request, 'inventario/login.html', {'error': 'Usuario o contraseña incorrectos'})
    return render(request, 'inventario/login.html')
def recuperar(request):
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        if tipo == 'correo':
            correo = request.POST.get('correo', '').strip()
            empleado = Empleados.objects.filter(correo__iexact=correo).first()
        elif tipo == 'telefono':
            telefono = request.POST.get('telefono', '').strip()
            empleado = _buscar_empleado_por_telefono(telefono)
        else:
            empleado = None

        tab = tipo if tipo in ('correo', 'telefono') else 'correo'

        if empleado is None:
            return render(request, 'inventario/recuperar.html', {
                'error': 'No encontramos una cuenta con esos datos.',
                'active_tab': tab,
            })

        if not (settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD):
            return render(request, 'inventario/recuperar.html', {
                'error': 'El envío de correo no está configurado. Contacta al administrador.',
                'active_tab': tab,
            })

        codigo = str(secrets.randbelow(900000) + 100000)
        request.session['codigo_recuperacion'] = codigo
        request.session['empleado_recuperar_id'] = empleado.id_empleado
        request.session['codigo_recuperacion_expira'] = int(time.time()) + 300
        request.session['intentos_codigo_recuperacion'] = 0
        request.session.pop('recuperacion_verificada', None)
        request.session.pop('correo_recuperacion_error', None)

        mensaje = f'Tu código para restablecer la contraseña es {codigo}. Vence en 5 minutos.'

        # Envío por correo (principal)
        try:
            enviado = send_mail(
                'Código para restablecer tu contraseña',
                mensaje,
                settings.EMAIL_HOST_USER,
                [empleado.correo],
                fail_silently=False,
            )
            if enviado != 1:
                raise OSError('El correo no se envió')
        except (SMTPException, OSError):
            logger.exception('No se pudo enviar el correo de recuperación.')
            for clave in ('codigo_recuperacion', 'empleado_recuperar_id',
                          'codigo_recuperacion_expira', 'intentos_codigo_recuperacion'):
                request.session.pop(clave, None)
            return render(request, 'inventario/recuperar.html', {
                'error': 'No se pudo enviar el correo. Inténtalo de nuevo.',
                'active_tab': tab,
            })

        # Envío por SMS (opcional: solo si Twilio está configurado)
        telefono_destino = _telefono_e164(empleado.telefono)
        if telefono_destino and all((settings.TWILIO_ACCOUNT_SID,
                                     settings.TWILIO_AUTH_TOKEN,
                                     settings.TWILIO_PHONE_NUMBER)):
            try:
                Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN).messages.create(
                    body=mensaje,
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=telefono_destino,
                )
            except (TwilioException, RequestException, OSError):
                logger.exception('No se pudo enviar el SMS de recuperación.')

        return redirect('verificar')

    return render(request, 'inventario/recuperar.html', {'active_tab': 'correo'})

def verificar_codigo(request):
    codigo_sesion = request.session.get('codigo_recuperacion')
    empleado_id = request.session.get('empleado_recuperar_id')
    if not codigo_sesion or not empleado_id:
        return redirect('recuperar')
    if int(time.time()) > request.session.get('codigo_recuperacion_expira', 0):
        request.session.pop('codigo_recuperacion', None)
        request.session.pop('empleado_recuperar_id', None)
        request.session.pop('codigo_recuperacion_expira', None)
        request.session.pop('correo_recuperacion_error', None)
        return render(request, 'inventario/recuperar.html', {
            'error': 'El código venció. Solicita uno nuevo.',
            'active_tab': 'correo',
        })

    if request.method == 'POST':
        codigo_ingresado = request.POST.get('codigo', '').strip()
        if hmac.compare_digest(codigo_ingresado, codigo_sesion):
            request.session.pop('codigo_recuperacion', None)
            request.session.pop('codigo_recuperacion_expira', None)
            request.session.pop('intentos_codigo_recuperacion', None)
            request.session.pop('correo_recuperacion_error', None)
            request.session['recuperacion_verificada'] = True
            return redirect('restablecer')

        intentos = request.session.get('intentos_codigo_recuperacion', 0) + 1
        request.session['intentos_codigo_recuperacion'] = intentos
        if intentos >= 5:
            request.session.pop('codigo_recuperacion', None)
            request.session.pop('empleado_recuperar_id', None)
            request.session.pop('codigo_recuperacion_expira', None)
            request.session.pop('intentos_codigo_recuperacion', None)
            request.session.pop('correo_recuperacion_error', None)
            return render(request, 'inventario/recuperar.html', {
                'error': 'Se agotaron los intentos. Solicita un código nuevo.',
                'active_tab': 'correo',
            })
        return render(request, 'inventario/verificar.html', {
            'error': 'El código ingresado no es válido.',
            'correo_error': request.session.get('correo_recuperacion_error', False),
        })

    return render(request, 'inventario/verificar.html', {
        'correo_error': request.session.get('correo_recuperacion_error', False),
    })


def restablecer(request):
    empleado_id = request.session.get('empleado_recuperar_id')
    if not empleado_id or not request.session.get('recuperacion_verificada'):
        return redirect('recuperar')

    empleado = Empleados.objects.filter(id_empleado=empleado_id).first()
    if empleado is None:
        request.session.pop('empleado_recuperar_id', None)
        request.session.pop('recuperacion_verificada', None)
        return redirect('recuperar')

    if request.method == 'POST':
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        if password != password2:
            return render(request, 'inventario/restablecer.html', {
                'error': 'Las contraseñas no coinciden.',
            
            })
            
        if len(password) < 8:
            return render(request, 'inventario/restablecer.html', {
                'error': 'La contraseña debe tener al menos 8 caracteres.',
            })

        error_pw = validar_password(password)
        if error_pw:
            return render(request, 'inventario/restablecer.html', {'error': error_pw})
        
        empleado.password = make_password(password)
        empleado.save(update_fields=['password'])
        request.session.pop('empleado_recuperar_id', None)
        request.session.pop('recuperacion_verificada', None)
        request.session.pop('correo_recuperacion_error', None)
        return redirect('login')

    return render(request, 'inventario/restablecer.html')
def dashboard(request):
    emp_id = request.session.get('empleado_id')
    if not emp_id:
        return redirect('login')
    emp = Empleados.objects.filter(id_empleado=emp_id).first()
    if emp is None:
        request.session.flush()
        return redirect('login')

    hoy = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
    ventas_hoy = Ventas.objects.filter(fecha_venta__gte=hoy)
    total_hoy = DetalleVenta.objects.filter(id_venta__fecha_venta__gte=hoy).aggregate(
        total=Sum(F('cantidad') * F('precio_venta'), output_field=DecimalField())
    )['total'] or 0

    return render(request, 'inventario/dashboard.html', {
        'nombre': emp.nombre,        'rol': emp.rol,
        'inicial': emp.nombre[:1].upper(),
        'total_productos': Productos.objects.count(),
        'ventas_hoy': ventas_hoy.count(),
        'total_hoy': total_hoy,
        'total_ordenes': OrdenesCompra.objects.count(),
        'alertas': 0,
        'actividad': Ventas.objects.order_by('-fecha_venta')[:5],
    })

def logout_view(request):
    request.session.flush()
    return redirect('login')

def terminos(request):
    return render(request, 'inventario/terminos.html')