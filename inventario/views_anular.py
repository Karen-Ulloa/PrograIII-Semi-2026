"""Vista web para anular una venta (archivo nuevo, no modifica views.py)."""
from django.contrib import messages
from django.shortcuts import redirect

from .anulaciones import AnulacionInvalida, VentaNoExiste, anular_venta
from .views import login_requerido


@login_requerido
def venta_anular(request, pk):
    if request.method == 'POST':
        try:
            anular_venta(pk, request.empleado, request.POST.get('motivo', ''),
                         request.POST.get('codigo', ''))
        except VentaNoExiste:
            messages.error(request, 'Esa venta no existe.')
            return redirect('ventas')
        except AnulacionInvalida as problema:
            messages.error(request, str(problema))
        else:
            messages.success(request, f'Venta #{pk} anulada. Las cantidades volvieron al stock.')
    return redirect('venta_detalle', pk=pk)