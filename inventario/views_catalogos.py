"""
CRUD de Categorías y Ubicaciones de bodega (archivo nuevo, no modifica views.py).

Permisos (mismos criterios que Productos y Proveedores):
  ver, crear y editar -> Administrador y Encargado
  eliminar            -> solo Administrador (y solo si no hay productos asociados)
"""
from django import forms
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import Categorias, Productos, Ubicaciones
from .views import contexto, gestor, solo_admin


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categorias
        fields = ['nombre_categoria']
        labels = {'nombre_categoria': 'Nombre de la categoría'}
        widgets = {'nombre_categoria': forms.TextInput(attrs={'class': 'form-control'})}

    def clean_nombre_categoria(self):
        nombre = ' '.join(self.cleaned_data['nombre_categoria'].split())
        if len(nombre) < 2:
            raise forms.ValidationError('Escribe el nombre de la categoría.')
        repetido = Categorias.objects.filter(nombre_categoria__iexact=nombre)
        if self.instance.pk:
            repetido = repetido.exclude(pk=self.instance.pk)
        if repetido.exists():
            raise forms.ValidationError('Ya existe una categoría con ese nombre.')
        return nombre


@gestor
def categorias_lista(request):
    q = request.GET.get('q', '').strip()
    qs = Categorias.objects.annotate(n_productos=Count('productos')).order_by('nombre_categoria')
    if q:
        qs = qs.filter(nombre_categoria__icontains=q)
    return render(request, 'inventario/categorias_lista.html', contexto(
        request, 'categorias', categorias=qs, q=q))


@gestor
def categoria_form(request, pk=None):
    categoria = get_object_or_404(Categorias, pk=pk) if pk else None
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría guardada correctamente.')
            return redirect('categorias')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'inventario/categoria_form.html', contexto(
        request, 'categorias', form=form, categoria=categoria))


@solo_admin
def categoria_eliminar(request, pk):
    cat = get_object_or_404(Categorias, pk=pk)
    if request.method == 'POST':
        if Productos.objects.filter(id_categoria=cat).exists():
            messages.error(request, 'No se puede eliminar: hay productos en esta categoría. '
                                    'Cámbialos de categoría primero.')
        else:
            nombre = cat.nombre_categoria
            cat.delete()
            messages.success(request, f'Categoría "{nombre}" eliminada.')
    return redirect('categorias')


class UbicacionForm(forms.ModelForm):
    class Meta:
        model = Ubicaciones
        fields = ['bodega', 'pasillo', 'estante', 'nivel', 'detalle']
        labels = {
            'bodega': 'Bodega', 'pasillo': 'Pasillo', 'estante': 'Estante',
            'nivel': 'Nivel (opcional)', 'detalle': 'Detalle (opcional)',
        }
        widgets = {
            'bodega': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Bodega 1'}),
            'pasillo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Pasillo 5'}),
            'estante': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Estante 3'}),
            'nivel': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Nivel 2'}),
            'detalle': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # El selector de ubicación del formulario de productos solo muestra las que tienen bodega.
        self.fields['bodega'].required = True

    def clean(self):
        datos = super().clean()
        for campo in ('bodega', 'pasillo', 'estante', 'nivel', 'detalle'):
            if datos.get(campo) is not None:
                datos[campo] = ' '.join(datos[campo].split())
        if all(datos.get(c) for c in ('bodega', 'pasillo', 'estante')):
            repetido = Ubicaciones.objects.filter(
                bodega__iexact=datos['bodega'], pasillo__iexact=datos['pasillo'],
                estante__iexact=datos['estante'], nivel__iexact=datos.get('nivel', ''))
            if self.instance.pk:
                repetido = repetido.exclude(pk=self.instance.pk)
            if repetido.exists():
                raise forms.ValidationError('Ya existe una ubicación con esa bodega, pasillo, estante y nivel.')
        return datos


@gestor
def ubicaciones_lista(request):
    q = request.GET.get('q', '').strip()
    qs = Ubicaciones.objects.annotate(n_productos=Count('productos')).order_by(
        'bodega', 'pasillo', 'estante', 'nivel')
    if q:
        qs = qs.filter(Q(bodega__icontains=q) | Q(pasillo__icontains=q) | Q(estante__icontains=q) |
                       Q(nivel__icontains=q) | Q(detalle__icontains=q))
    pagina = Paginator(qs, 50).get_page(request.GET.get('page'))
    return render(request, 'inventario/ubicaciones_lista.html', contexto(
        request, 'ubicaciones', pagina=pagina, q=q))


@gestor
def ubicacion_form(request, pk=None):
    ubicacion = get_object_or_404(Ubicaciones, pk=pk) if pk else None
    if request.method == 'POST':
        form = UbicacionForm(request.POST, instance=ubicacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ubicación guardada correctamente.')
            return redirect('ubicaciones')
    else:
        form = UbicacionForm(instance=ubicacion)
    return render(request, 'inventario/ubicacion_form.html', contexto(
        request, 'ubicaciones', form=form, ubicacion=ubicacion))


@solo_admin
def ubicacion_eliminar(request, pk):
    ub = get_object_or_404(Ubicaciones, pk=pk)
    if request.method == 'POST':
        if Productos.objects.filter(id_ubicacion=ub).exists():
            messages.error(request, 'No se puede eliminar: hay productos asignados a esta ubicación. '
                                    'Cámbialos de ubicación primero.')
        else:
            ub.delete()
            messages.success(request, 'Ubicación eliminada.')
    return redirect('ubicaciones')