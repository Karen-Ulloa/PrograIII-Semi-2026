from django.shortcuts import render, redirect
from.models import Empleados
from django.core.mail import send_mail
import random
import re

def inicio(request): return render(request, 'inventario/inicio.html')

def registro(request):
    if request.method == 'POST':
        if request.POST.get('password')!= request.POST.get('password2'):
            return render(request, 'inventario/registro.html', {'error':'Contraseñas no coinciden'})

        correo = request.POST.get('correo','').strip().lower()
        # Generar usuario base desde correo: juan.perez@gmail.com -> juan.perez
        usuario_base = correo.split('@')[0].lower()
        usuario_base = re.sub(r'[^a-z0-9._-]', '', usuario_base)

        usuario_final = usuario_base
        contador = 1
        while Empleados.objects.filter(usuario=usuario_final).exists():
            usuario_final = f"{usuario_base}{contador}"
            contador += 1

        Empleados.objects.create(
            nombre=request.POST.get('nombre'),
            apellido=request.POST.get('apellido'),
            direccion=request.POST.get('direccion'),
            correo=correo,
            telefono=request.POST.get('telefono'),
            usuario=usuario_final,
            password=request.POST.get('password')
        )
        return redirect('login')
    return render(request, 'inventario/registro.html')

def login_view(request):
    if request.method == 'POST':
        try:
            emp = Empleados.objects.get(usuario=request.POST.get('usuario'), password=request.POST.get('password'))
            request.session['empleado_id']=emp.id_empleado
            return redirect('dashboard')
        except:
            return render(request, 'inventario/login.html', {'error':'Usuario o contraseña incorrectos'})
    return render(request, 'inventario/login.html')

def recuperar(request):
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        if tipo == 'correo':
            correo = request.POST.get('correo')
            try:
                emp = Empleados.objects.get(correo=correo)
                codigo = str(random.randint(100000, 999999))
                request.session['codigo_recuperacion'] = codigo
                request.session['empleado_recuperar'] = emp.id_empleado
                send_mail(
                    'CampesinoStock - Código de recuperación',
                    f'Tu código para cambiar contraseña es: {codigo}',
                    'campesinostock@gmail.com',
                    [correo],
                    fail_silently=False,
                )
                return render(request, 'inventario/recuperar.html', {'mensaje': f'Código enviado a {correo}. Código de prueba: {codigo}'})
            except:
                return render(request, 'inventario/recuperar.html', {'error':'Correo no encontrado'})
        else:
            telefono = request.POST.get('telefono')
            try:
                emp = Empleados.objects.get(telefono=telefono)
                codigo = str(random.randint(100000, 999999))
                request.session['codigo_recuperacion'] = codigo
                request.session['empleado_recuperar'] = emp.id_empleado
                return render(request, 'inventario/recuperar.html', {'mensaje': f'Para prueba, tu código es: {codigo}. En producción se enviaría por SMS a {telefono}'})
            except:
                return render(request, 'inventario/recuperar.html', {'error':'Teléfono no encontrado'})
    return render(request, 'inventario/recuperar.html')

def dashboard(request): return render(request, 'inventario/dashboard.html')
def terminos(request): return render(request, 'inventario/terminos.html')