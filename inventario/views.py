from django.shortcuts import render, redirect
from .models import Empleados

def inicio(request):
    return render(request, 'inventario/inicio.html')

def registro(request):
    if request.method == 'POST':
        pass1 = request.POST.get('password')
        pass2 = request.POST.get('password2')

        if pass1 != pass2:
            return render(request, 'inventario/registro.html', {'error': 'Las contraseñas no coinciden'})

        Empleados.objects.create(
            nombre=request.POST.get('nombre'),
            apellido=request.POST.get('apellido'),
            direccion=request.POST.get('direccion'),
            correo=request.POST.get('correo'),
            telefono=request.POST.get('telefono'),
            usuario=request.POST.get('usuario'),
            password=pass1
        )
        return redirect('login')
    return render(request, 'inventario/registro.html')

def login_view(request):
    return render(request, 'inventario/login.html')

def recuperar(request):
    return render(request, 'inventario/recuperar.html')

def terminos(request):
    return render(request, 'inventario/terminos.html')