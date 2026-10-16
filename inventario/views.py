import hmac
import logging
import re
import secrets
import time
from functools import wraps
from io import BytesIO
from uuid import uuid4
from smtplib import SMTPException

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.db.models import DecimalField, F, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from PIL import Image, ImageOps, UnidentifiedImageError
from requests.exceptions import RequestException
from twilio.base.exceptions import TwilioException
from twilio.rest import Client

from .models import (
    Categorias, Configuracion, DetalleCompra, DetalleVenta, Empleados,
    OrdenesCompra, ProductoProveedo, Productos, Proveedores,
    RegistrosMerma, Ubicaciones, Ventas,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------
# UTILIDADES
# ---------------------------------------------------------------
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


# ---------------------------------------------------------------
# PERMISOS Y CONFIGURACIÓN
# ---------------------------------------------------------------
def login_requerido(vista):
    """Exige sesión iniciada. Deja al empleado en request.empleado."""
    @wraps(vista)
    def envoltura(request, *args, **kwargs):
        emp = Empleados.objects.filter(id_empleado=request.session.get('empleado_id')).first()
        if emp is None or not emp.activo:
            request.session.flush()
            return redirect('login')
        request.empleado = emp
        return vista(request, *args, **kwargs)
    return envoltura


ROLES = ('Administrador', 'Encargado', 'Empleado')


def roles_permitidos(*roles):
    """Exige sesión iniciada y que el rol esté en la lista."""
    def decorador(vista):
        @login_requerido
        @wraps(vista)
        def envoltura(request, *args, **kwargs):
            if request.empleado.rol not in roles:
                return render(request, 'inventario/sin_permiso.html', status=403)
            return vista(request, *args, **kwargs)
        return envoltura
    return decorador


solo_admin = roles_permitidos('Administrador')
gestor = roles_permitidos('Administrador', 'Encargado')


def obtener_config(clave):
    fila = Configuracion.objects.filter(pk=clave).first()
    return fila.valor if fila else None


def guardar_config(clave, valor):
    Configuracion.objects.update_or_create(clave=clave, defaults={'valor': valor})


def codigo_admin_correcto(codigo):
    hash_guardado = obtener_config('codigo_admin_hash')
    return bool(hash_guardado) and check_password(codigo, hash_guardado)


def contexto(request, activo='', **extra):
    """Datos comunes para todas las pantallas con menú."""
    emp = request.empleado
    datos = {
        'nombre': emp.nombre,
        'rol': emp.rol,
        'es_admin': emp.rol == 'Administrador',
        'es_gestor': emp.rol in ('Administrador', 'Encargado'),
        'inicial': emp.nombre[:1].upper(),
        'foto_url': emp.foto.url if emp.foto else '',
        'activo': activo,
        'alertas': 0,
    }
    datos.update(extra)
    return datos


# ---------------------------------------------------------------
# PÁGINAS PÚBLICAS, REGISTRO Y LOGIN
# ---------------------------------------------------------------
def inicio(request):
    return render(request, 'inventario/inicio.html')


def terminos(request):
    return render(request, 'inventario/terminos.html')


def registro(request):
    # Si aún no existe ningún administrador, la primera cuenta es la del dueño.
    primer_uso = not Empleados.objects.filter(rol='Administrador').exists()

    if request.method == 'POST':
        datos = request.POST.copy()
        for campo in ('password', 'password2', 'codigo_admin', 'codigo_admin2'):
            datos[campo] = ''

        def volver(error, limpiar=None):
            if limpiar:
                datos[limpiar] = ''
            return render(request, 'inventario/registro.html', {
                'error': error, 'datos': datos, 'primer_uso': primer_uso})

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

        codigo = ''
        if primer_uso:
            codigo = request.POST.get('codigo_admin', '')
            if len(codigo) < 8:
                return volver('El código secreto debe tener al menos 8 caracteres.')
            if codigo != request.POST.get('codigo_admin2', ''):
                return volver('Los códigos secretos no coinciden.')
            rol = 'Administrador'
        else:
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

        if primer_uso and Empleados.objects.filter(rol='Administrador').exists():
            return volver('Ya existe un administrador. Recarga la página para registrarte como empleado.')

        Empleados.objects.create(
            nombre=nombre, apellido=apellido,
            direccion=request.POST.get('direccion'), correo=correo,
            telefono=request.POST.get('telefono'), usuario=usuario_final,
            password=make_password(password),
            rol=rol,
        )
        if primer_uso:
            guardar_config('codigo_admin_hash', make_password(codigo))
        return redirect('login')

    return render(request, 'inventario/registro.html', {'datos': {}, 'primer_uso': primer_uso})


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
            if not emp.activo:
                return render(request, 'inventario/login.html', {
                    'error': 'Tu cuenta está desactivada. Habla con el administrador.'})
            request.session['empleado_id'] = emp.id_empleado
            return redirect('dashboard')
        except ValueError:
            return render(request, 'inventario/login.html', {'error': 'Usuario o contraseña incorrectos'})
    return render(request, 'inventario/login.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')


# ---------------------------------------------------------------
# RECUPERAR CONTRASEÑA
# ---------------------------------------------------------------
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

        # SMS opcional: solo si Twilio está configurado
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
        for clave in ('codigo_recuperacion', 'empleado_recuperar_id',
                      'codigo_recuperacion_expira', 'correo_recuperacion_error'):
            request.session.pop(clave, None)
        return render(request, 'inventario/recuperar.html', {
            'error': 'El código venció. Solicita uno nuevo.',
            'active_tab': 'correo',
        })

    if request.method == 'POST':
        codigo_ingresado = request.POST.get('codigo', '').strip()
        if hmac.compare_digest(codigo_ingresado, codigo_sesion):
            for clave in ('codigo_recuperacion', 'codigo_recuperacion_expira',
                          'intentos_codigo_recuperacion', 'correo_recuperacion_error'):
                request.session.pop(clave, None)
            request.session['recuperacion_verificada'] = True
            return redirect('restablecer')

        intentos = request.session.get('intentos_codigo_recuperacion', 0) + 1
        request.session['intentos_codigo_recuperacion'] = intentos
        if intentos >= 5:
            for clave in ('codigo_recuperacion', 'empleado_recuperar_id',
                          'codigo_recuperacion_expira', 'intentos_codigo_recuperacion',
                          'correo_recuperacion_error'):
                request.session.pop(clave, None)
            return render(request, 'inventario/recuperar.html', {
                'error': 'Se agotaron los intentos. Solicita un código nuevo.',
                'active_tab': 'correo',
            })
        return render(request, 'inventario/verificar.html', {
            'error': 'El código ingresado no es válido.',
        })

    return render(request, 'inventario/verificar.html')


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


# ---------------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------------
@login_requerido
def dashboard(request):
    hoy = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
    ventas_hoy = Ventas.objects.filter(fecha_venta__gte=hoy)
    total_hoy = DetalleVenta.objects.filter(id_venta__fecha_venta__gte=hoy).aggregate(
        total=Sum(F('cantidad') * F('precio_venta'), output_field=DecimalField())
    )['total'] or 0

    return render(request, 'inventario/dashboard.html', contexto(
        request, 'inicio',
        total_productos=Productos.objects.count(),
        ventas_hoy=ventas_hoy.count(),
        total_hoy=total_hoy,
        total_ordenes=OrdenesCompra.objects.count(),
        alertas=0,
        actividad=Ventas.objects.order_by('-fecha_venta')[:5],
    ))


# ---------------------------------------------------------------
# PRODUCTOS
# ---------------------------------------------------------------
class ProductoForm(forms.ModelForm):
    pasillo = forms.CharField(
        required=False, max_length=50, label='Pasillo',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 2'}))
    estante = forms.CharField(
        required=False, max_length=50, label='Estante',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: B'}))

    class Meta:
        model = Productos
        fields = ['nombre_producto', 'id_categoria', 'precio_compra',
                  'precio_producto', 'stock', 'stock_minimo']
        labels = {
            'nombre_producto': 'Nombre y medida del producto',
            'id_categoria': 'Categoría',
            'precio_compra': 'Precio de compra (USD)',
            'precio_producto': 'Precio de venta (USD)',
            'stock': 'Stock actual',
            'stock_minimo': 'Stock mínimo (para alertas)',
        }
        widgets = {
            'nombre_producto': forms.TextInput(attrs={'class': 'form-control'}),
            'id_categoria': forms.Select(attrs={'class': 'form-select'}),
            'precio_compra': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'precio_producto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cat = self.fields['id_categoria']
        cat.queryset = Categorias.objects.order_by('nombre_categoria')
        cat.label_from_instance = lambda c: c.nombre_categoria
        cat.empty_label = 'Selecciona una categoría'
        cat.required = True

    def clean_nombre_producto(self):
        nombre = self.cleaned_data['nombre_producto'].strip()
        repetido = Productos.objects.filter(nombre_producto__iexact=nombre)
        if self.instance.pk:
            repetido = repetido.exclude(pk=self.instance.pk)
        if repetido.exists():
            raise forms.ValidationError('Ya existe un producto con ese nombre.')
        return nombre

    def clean(self):
        datos = super().clean()
        for campo in ('precio_compra', 'precio_producto', 'stock', 'stock_minimo'):
            valor = datos.get(campo)
            if valor is not None and valor < 0:
                self.add_error(campo, 'No puede ser negativo.')
        if bool(datos.get('pasillo')) != bool(datos.get('estante')):
            self.add_error('estante', 'Escribe pasillo y estante, o deja los dos vacíos.')
        return datos


@login_requerido
def productos_lista(request):
    return render(request, 'inventario/productos_lista.html', contexto(
        request, 'productos',
        categorias=Categorias.objects.order_by('nombre_categoria'),
    ))


@login_requerido
def api_productos(request):
    q = request.GET.get('q', '').strip()
    cat = request.GET.get('categoria', '')
    es_gestor = request.empleado.rol in ('Administrador', 'Encargado')

    qs = Productos.objects.select_related('id_categoria', 'id_ubicacion').order_by('nombre_producto')
    if q:
        qs = qs.filter(Q(nombre_producto__icontains=q) |
                       Q(id_categoria__nombre_categoria__icontains=q))
    if cat.isdigit():
        qs = qs.filter(id_categoria_id=int(cat))

    total = qs.count()
    items = []
    for p in qs[:100]:
        item = {
            'id': p.id_producto,
            'nombre': p.nombre_producto,
            'categoria': p.id_categoria.nombre_categoria if p.id_categoria else '—',
            'ubicacion': (f'Pasillo {p.id_ubicacion.pasillo} · Estante {p.id_ubicacion.estante}'
                          if p.id_ubicacion else '—'),
            'stock': p.stock,
            'stock_minimo': p.stock_minimo,
            'precio_venta': float(p.precio_producto),
        }
        if es_gestor:
            item['precio_compra'] = float(p.precio_compra)
        items.append(item)

    return JsonResponse({'productos': items, 'total': total})


@gestor
def producto_form(request, pk=None):
    producto = get_object_or_404(Productos, pk=pk) if pk else None

    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            p = form.save(commit=False)
            pasillo = form.cleaned_data['pasillo']
            estante = form.cleaned_data['estante']
            if pasillo and estante:
                p.id_ubicacion = (Ubicaciones.objects.filter(pasillo=pasillo, estante=estante).first()
                                  or Ubicaciones.objects.create(pasillo=pasillo, estante=estante))
            else:
                p.id_ubicacion = None
            p.save()
            messages.success(request, 'Producto guardado correctamente.')
            return redirect('productos')
    else:
        inicial = {}
        if producto and producto.id_ubicacion:
            inicial = {'pasillo': producto.id_ubicacion.pasillo,
                       'estante': producto.id_ubicacion.estante}
        form = ProductoForm(instance=producto, initial=inicial)

    return render(request, 'inventario/producto_form.html', contexto(
        request, 'productos', form=form, producto=producto))


@solo_admin
def producto_eliminar(request, pk):
    p = get_object_or_404(Productos, pk=pk)
    if request.method == 'POST':
        if (DetalleVenta.objects.filter(id_producto=p).exists()
                or DetalleCompra.objects.filter(id_producto=p).exists()
                or RegistrosMerma.objects.filter(id_producto=p).exists()):
            messages.error(request, 'No se puede eliminar: el producto tiene ventas, compras o mermas registradas. '
                                    'Puedes dejar su stock en 0.')
        else:
            nombre = p.nombre_producto
            p.delete()
            messages.success(request, f'Producto "{nombre}" eliminado.')
    return redirect('productos')


# ---------------------------------------------------------------
# EMPLEADOS (solo administrador)
# ---------------------------------------------------------------
class EmpleadoForm(forms.ModelForm):
    rol = forms.ChoiceField(
        choices=[('Empleado', 'Empleado'), ('Encargado', 'Encargado'), ('Administrador', 'Administrador')],
        label='Rol', widget=forms.Select(attrs={'class': 'form-select'}))
    codigo_admin = forms.CharField(
        required=False, label='Código de autorización (solo para asignar el rol Administrador)',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    password1 = forms.CharField(
        required=False, label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}))
    password2 = forms.CharField(
        required=False, label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}))

    field_order = ['nombre', 'apellido', 'correo', 'telefono', 'direccion',
                   'usuario', 'rol', 'codigo_admin', 'password1', 'password2', 'activo']

    class Meta:
        model = Empleados
        fields = ['nombre', 'apellido', 'correo', 'telefono', 'direccion',
                  'usuario', 'rol', 'activo']
        labels = {'nombre': 'Nombre', 'apellido': 'Apellido', 'correo': 'Correo',
                  'telefono': 'Teléfono', 'direccion': 'Dirección', 'usuario': 'Usuario'}
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0000-0000'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'usuario': forms.TextInput(attrs={'class': 'form-control', 'autocapitalize': 'none'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, actual=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.actual = actual

    def clean_correo(self):
        correo = self.cleaned_data['correo'].strip().lower()
        validate_email(correo)
        repetido = Empleados.objects.filter(correo__iexact=correo)
        if self.instance.pk:
            repetido = repetido.exclude(pk=self.instance.pk)
        if repetido.exists():
            raise forms.ValidationError('Ese correo ya está registrado.')
        return correo

    def clean_usuario(self):
        usuario = self.cleaned_data['usuario'].strip()
        if self.instance.pk and usuario == self.instance.usuario:
            return usuario
        usuario = usuario.lower()
        if not re.fullmatch(r'[a-z0-9._]{3,30}', usuario):
            raise forms.ValidationError('Solo letras, números, punto y guion bajo (mínimo 3).')
        repetido = Empleados.objects.filter(usuario=usuario)
        if self.instance.pk:
            repetido = repetido.exclude(pk=self.instance.pk)
        if repetido.exists():
            raise forms.ValidationError('Ese usuario ya está en uso.')
        return usuario

    def clean_telefono(self):
        telefono = self.cleaned_data['telefono'].strip()
        if len(re.sub(r'\D', '', telefono)) != 8:
            raise forms.ValidationError('El teléfono debe tener 8 dígitos.')
        return telefono

    def clean(self):
        datos = super().clean()
        p1 = datos.get('password1', '')
        p2 = datos.get('password2', '')
        creando = not self.instance.pk

        if creando and not p1:
            self.add_error('password1', 'La contraseña es obligatoria.')
        elif p1 or p2:
            if p1 != p2:
                self.add_error('password2', 'Las contraseñas no coinciden.')
            else:
                error = validar_password(p1)
                if error:
                    self.add_error('password1', error)

        if self.instance.pk and self.actual and self.instance.pk == self.actual.pk:
            if datos.get('rol') != 'Administrador':
                self.add_error('rol', 'No puedes quitarte el rol de administrador a ti misma.')
            if not datos.get('activo'):
                self.add_error('activo', 'No puedes desactivar tu propia cuenta.')

        # Para dar el rol Administrador a alguien nuevo se pide el código secreto.
        if datos.get('rol') == 'Administrador' and (creando or self.instance.rol != 'Administrador'):
            if not obtener_config('codigo_admin_hash'):
                self.add_error('codigo_admin', 'Primero configura el código admin en el menú "Código admin".')
            elif not codigo_admin_correcto(datos.get('codigo_admin', '')):
                self.add_error('codigo_admin', 'El código de autorización no es correcto.')
        return datos

    def save(self, commit=True):
        emp = super().save(commit=False)
        p1 = self.cleaned_data.get('password1')
        if p1:
            emp.password = make_password(p1)
        if commit:
            emp.save()
        return emp


@solo_admin
def empleados_lista(request):
    q = request.GET.get('q', '').strip()
    qs = Empleados.objects.order_by('nombre', 'apellido')
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(apellido__icontains=q) |
                       Q(usuario__icontains=q) | Q(correo__icontains=q))
    return render(request, 'inventario/empleados_lista.html', contexto(
        request, 'empleados', empleados=qs, q=q, yo=request.empleado.id_empleado))


@solo_admin
def empleado_form(request, pk=None):
    empleado = get_object_or_404(Empleados, pk=pk) if pk else None
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, instance=empleado, actual=request.empleado)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empleado guardado correctamente.')
            return redirect('empleados')
    else:
        form = EmpleadoForm(instance=empleado, actual=request.empleado)
    return render(request, 'inventario/empleado_form.html', contexto(
        request, 'empleados', form=form, empleado=empleado))


@solo_admin
def empleado_estado(request, pk):
    emp = get_object_or_404(Empleados, pk=pk)
    if request.method == 'POST':
        if emp.pk == request.empleado.pk:
            messages.error(request, 'No puedes desactivar tu propia cuenta.')
        else:
            emp.activo = not emp.activo
            emp.save(update_fields=['activo'])
            messages.success(request, f'{emp.nombre} ahora está {"activo" if emp.activo else "inactivo"}.')
    return redirect('empleados')


@solo_admin
def empleado_eliminar(request, pk):
    emp = get_object_or_404(Empleados, pk=pk)
    if request.method == 'POST':
        if emp.pk == request.empleado.pk:
            messages.error(request, 'No puedes eliminar tu propia cuenta.')
        elif Ventas.objects.filter(id_empleado=emp).exists():
            messages.error(request, 'No se puede eliminar: tiene ventas registradas. Mejor desactívalo.')
        else:
            nombre = emp.nombre
            if emp.foto:
                emp.foto.delete(save=False)
            emp.delete()
            messages.success(request, f'Empleado "{nombre}" eliminado.')
    return redirect('empleados')


# ---------------------------------------------------------------
# CÓDIGO SECRETO DE ADMINISTRADOR
# ---------------------------------------------------------------
@solo_admin
def codigo_admin(request):
    existe = bool(obtener_config('codigo_admin_hash'))
    if request.method == 'POST':
        clave = request.POST.get('clave', '')
        nuevo = request.POST.get('nuevo', '')
        nuevo2 = request.POST.get('nuevo2', '')
        if not check_password(clave, request.empleado.password):
            messages.error(request, 'La contraseña de tu cuenta no es correcta.')
        elif len(nuevo) < 8:
            messages.error(request, 'El código debe tener al menos 8 caracteres.')
        elif nuevo != nuevo2:
            messages.error(request, 'Los códigos no coinciden.')
        else:
            guardar_config('codigo_admin_hash', make_password(nuevo))
            messages.success(request, 'El código de autorización se guardó correctamente.')
            return redirect('codigo_admin')
    return render(request, 'inventario/codigo_admin.html', contexto(
        request, 'codigo', existe=existe))


# ---------------------------------------------------------------
# PERFIL (cada persona maneja su propia cuenta)
# ---------------------------------------------------------------
class PerfilForm(forms.ModelForm):
    class Meta:
        model = Empleados
        fields = ['nombre', 'apellido', 'correo', 'telefono', 'direccion']
        labels = {'nombre': 'Nombre', 'apellido': 'Apellido', 'correo': 'Correo',
                  'telefono': 'Teléfono', 'direccion': 'Dirección'}
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0000-0000'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_correo(self):
        correo = self.cleaned_data['correo'].strip().lower()
        validate_email(correo)
        if Empleados.objects.filter(correo__iexact=correo).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Ese correo ya está registrado.')
        return correo

    def clean_telefono(self):
        telefono = self.cleaned_data['telefono'].strip()
        if len(re.sub(r'\D', '', telefono)) != 8:
            raise forms.ValidationError('El teléfono debe tener 8 dígitos.')
        return telefono


MAX_FOTO = 8 * 1024 * 1024  # 8 MB (las fotos de celular suelen pesar entre 2 y 6 MB)


def procesar_foto(archivo):
    """Valida que sea una imagen real, la endereza, la recorta cuadrada y la
    guarda como JPEG de 480x480. Al recodificarla se eliminan los metadatos
    (ubicación GPS, modelo del teléfono, etc.)."""
    if archivo.size > MAX_FOTO:
        raise ValueError('La foto pesa demasiado (máximo 8 MB).')
    try:
        img = Image.open(archivo)
        formato = img.format
        img.verify()
        archivo.seek(0)
        img = Image.open(archivo)
        img.load()
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        raise ValueError('El archivo no es una imagen válida. Usa una foto JPG, PNG o WEBP.')
    if formato not in ('JPEG', 'PNG', 'WEBP'):
        raise ValueError('Formato no permitido. Usa una foto JPG, PNG o WEBP.')

    img = ImageOps.exif_transpose(img)
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGBA')
        fondo = Image.new('RGB', img.size, (255, 255, 255))
        fondo.paste(img, mask=img.split()[-1])
        img = fondo
    else:
        img = img.convert('RGB')
    img = ImageOps.fit(img, (480, 480), Image.LANCZOS)

    salida = BytesIO()
    img.save(salida, format='JPEG', quality=85)
    return ContentFile(salida.getvalue(), name=f'{uuid4().hex}.jpg')


@login_requerido
def perfil(request):
    emp = request.empleado
    form = PerfilForm(instance=emp)
    abrir = ''

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'datos':
            form = PerfilForm(request.POST, instance=emp)
            if form.is_valid():
                form.save()
                messages.success(request, 'Tus datos se guardaron correctamente.')
                return redirect('perfil')
            abrir = 'editar'

        elif accion == 'foto':
            archivo = request.FILES.get('foto')
            if not archivo:
                messages.error(request, 'No se seleccionó ninguna foto.')
            else:
                try:
                    contenido = procesar_foto(archivo)
                except ValueError as error:
                    messages.error(request, str(error))
                else:
                    if emp.foto:
                        emp.foto.delete(save=False)
                    emp.foto.save(contenido.name, contenido, save=True)
                    messages.success(request, 'Tu foto de perfil se actualizó.')
            return redirect('perfil')

        elif accion == 'quitar_foto':
            if emp.foto:
                emp.foto.delete(save=True)
                messages.success(request, 'Se quitó tu foto de perfil.')
            return redirect('perfil')

        elif accion == 'password':
            actual = request.POST.get('actual', '')
            p1 = request.POST.get('password1', '')
            p2 = request.POST.get('password2', '')
            if not check_password(actual, emp.password):
                messages.error(request, 'La contraseña actual no es correcta.')
            elif p1 != p2:
                messages.error(request, 'Las contraseñas nuevas no coinciden.')
            else:
                error_pw = validar_password(p1)
                if error_pw:
                    messages.error(request, error_pw)
                else:
                    emp.password = make_password(p1)
                    emp.save(update_fields=['password'])
                    messages.success(request, 'Tu contraseña se cambió correctamente.')
            return redirect('perfil')

        elif accion == 'eliminar':
            clave = request.POST.get('clave', '')
            if not check_password(clave, emp.password):
                messages.error(request, 'La contraseña no es correcta. Tu cuenta no se eliminó.')
            elif (emp.rol == 'Administrador'
                  and not Empleados.objects.filter(rol='Administrador', activo=True)
                                           .exclude(pk=emp.pk).exists()):
                messages.error(request, 'Eres la única administradora activa. Crea o asigna a otro administrador '
                                        'antes de eliminar tu cuenta.')
            elif Ventas.objects.filter(id_empleado=emp).exists():
                messages.error(request, 'No puedes eliminar tu cuenta porque tiene ventas registradas. '
                                        'Pide a otro administrador que la desactive.')
            else:
                if emp.foto:
                    emp.foto.delete(save=False)
                emp.delete()
                request.session.flush()
                return redirect('login')
            return redirect('perfil')

    return render(request, 'inventario/perfil.html', contexto(
        request, 'perfil', form=form, empleado=emp, abrir=abrir))


# ---------------------------------------------------------------
# PROVEEDORES (administrador y encargado; solo el administrador elimina)
# ---------------------------------------------------------------
class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedores
        fields = ['nombre_proveedor', 'contacto_proveedor']
        labels = {
            'nombre_proveedor': 'Nombre del proveedor',
            'contacto_proveedor': 'Contacto (teléfono o correo)',
        }
        widgets = {
            'nombre_proveedor': forms.TextInput(attrs={'class': 'form-control'}),
            'contacto_proveedor': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_nombre_proveedor(self):
        nombre = self.cleaned_data['nombre_proveedor'].strip()
        repetido = Proveedores.objects.filter(nombre_proveedor__iexact=nombre)
        if self.instance.pk:
            repetido = repetido.exclude(pk=self.instance.pk)
        if repetido.exists():
            raise forms.ValidationError('Ya existe un proveedor con ese nombre.')
        return nombre

    def clean_contacto_proveedor(self):
        return self.cleaned_data['contacto_proveedor'].strip()


@gestor
def proveedores_lista(request):
    q = request.GET.get('q', '').strip()
    qs = Proveedores.objects.order_by('nombre_proveedor')
    if q:
        qs = qs.filter(Q(nombre_proveedor__icontains=q) | Q(contacto_proveedor__icontains=q))
    return render(request, 'inventario/proveedores_lista.html', contexto(
        request, 'proveedores', proveedores=qs, q=q))


@gestor
def proveedor_form(request, pk=None):
    proveedor = get_object_or_404(Proveedores, pk=pk) if pk else None
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor guardado correctamente.')
            return redirect('proveedores')
    else:
        form = ProveedorForm(instance=proveedor)
    return render(request, 'inventario/proveedor_form.html', contexto(
        request, 'proveedores', form=form, proveedor=proveedor))


@solo_admin
def proveedor_eliminar(request, pk):
    prov = get_object_or_404(Proveedores, pk=pk)
    if request.method == 'POST':
        if (OrdenesCompra.objects.filter(id_proveedor=prov).exists()
                or ProductoProveedo.objects.filter(id_proveedor=prov).exists()):
            messages.error(request, 'No se puede eliminar: el proveedor tiene órdenes de compra '
                                    'o productos asociados.')
        else:
            nombre = prov.nombre_proveedor
            prov.delete()
            messages.success(request, f'Proveedor "{nombre}" eliminado.')
    return redirect('proveedores')