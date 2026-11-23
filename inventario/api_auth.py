"""
Autenticación y permisos de la API REST (archivo nuevo, no modifica nada existente).

El sistema no usa django.contrib.auth: la sesión guarda 'empleado_id' y
'sesion_version'. Aquí se reutiliza esa misma sesión para la API, con las
mismas reglas que login_requerido de views.py.
"""
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import BasePermission

from .models import Empleados

ADMIN = 'Administrador'
ENCARGADO = 'Encargado'
EMPLEADO = 'Empleado'

TODOS = (ADMIN, ENCARGADO, EMPLEADO)
GESTORES = (ADMIN, ENCARGADO)
SOLO_ADMIN = (ADMIN,)


class EmpleadoUsuario:
    """Envoltura mínima para que DRF trate a un Empleado como usuario autenticado."""
    is_authenticated = True
    is_anonymous = False

    def __init__(self, empleado):
        self.empleado = empleado
        self.pk = self.id = empleado.pk
        self.rol = empleado.rol

    def __str__(self):
        return self.empleado.usuario


class EmpleadoSessionAuthentication(SessionAuthentication):
    """Lee la sesión del sistema. En POST/PUT/PATCH/DELETE exige el token CSRF."""

    def authenticate(self, request):
        sesion = request._request.session
        empleado_id = sesion.get('empleado_id')
        if not empleado_id:
            return None
        emp = Empleados.objects.filter(id_empleado=empleado_id).first()
        if (emp is None or not emp.activo
                or sesion.get('sesion_version') != emp.sesion_version):
            return None
        self.enforce_csrf(request)
        return (EmpleadoUsuario(emp), None)

    def authenticate_header(self, request):
        return 'Session'  # hace que "sin sesión" responda 401 en vez de 403


class PorRol(BasePermission):
    """
    Cada vista declara:
      roles_por_accion = {'list': TODOS, 'create': GESTORES, ...}
      roles_default    = roles para cualquier acción no listada (por defecto, solo admin)
    """
    message = 'Tu rol no tiene permiso para esta acción.'

    def has_permission(self, request, view):
        user = request.user
        if not getattr(user, 'is_authenticated', False):
            return False
        accion = getattr(view, 'action', None)
        por_accion = getattr(view, 'roles_por_accion', {})
        roles = por_accion.get(accion, getattr(view, 'roles_default', SOLO_ADMIN))
        return user.rol in roles