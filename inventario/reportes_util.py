"""
Utilidades de los reportes (archivo nuevo). No usa Django ni la base de datos:
solo da formato a las tablas para la pantalla y las exporta a Excel.

Un "reporte" es un diccionario:
  {'titulo', 'subtitulo', 'nota',
   'resumen':   [(etiqueta, valor, tipo), ...],
   'secciones': [{'titulo', 'columnas': [(nombre, tipo), ...],
                  'filas': [tuplas], 'totales': tupla o None, 'limite': int o None}, ...]}
Tipos de columna: 'texto', 'num' (entero) y 'dinero'.
"""
import io

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

XLSX = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
FORMATO_EXCEL = {'dinero': '"$"#,##0.00', 'num': '#,##0'}


def fmt(valor, tipo):
    """Texto para mostrar en pantalla."""
    if valor is None:
        return '—'
    if valor == '':
        return ''
    if tipo == 'dinero':
        return f'${valor:,.2f}'
    if tipo == 'num':
        return f'{valor:,}'
    return str(valor)


def vista_resumen(resumen):
    return [{'etiqueta': etiqueta, 'valor': fmt(valor, tipo)} for etiqueta, valor, tipo in resumen]


def vista_seccion(seccion):
    """Prepara una sección para la plantilla (celdas ya formateadas)."""
    columnas = seccion['columnas']

    def celdas(fila):
        return [{'texto': fmt(v, tipo), 'derecha': tipo in ('num', 'dinero'),
                 'etiqueta': nombre, 'primera': i == 0}
                for i, (v, (nombre, tipo)) in enumerate(zip(fila, columnas))]

    limite = seccion.get('limite')
    filas = seccion['filas'][:limite] if limite else seccion['filas']
    return {
        'titulo': seccion['titulo'],
        'encabezados': [{'nombre': n, 'derecha': t in ('num', 'dinero')} for n, t in columnas],
        'filas': [celdas(f) for f in filas],
        'totales': celdas(seccion['totales']) if seccion.get('totales') else None,
        'ocultas': len(seccion['filas']) - len(filas),
        'vacio': not seccion['filas'],
    }


def construir_excel(reporte, generado):
    """Devuelve los bytes de un .xlsx con todo el reporte (sin límite de filas)."""
    libro = Workbook()
    hoja = libro.active
    hoja.title = 'Reporte'
    relleno = PatternFill('solid', fgColor='5A1016')
    anchos = {}

    def escribir(fila, tipos=None, negrita=False):
        hoja.append(list(fila))
        r = hoja.max_row
        for c, valor in enumerate(fila, start=1):
            celda = hoja.cell(row=r, column=c)
            if negrita:
                celda.font = Font(bold=True)
            if (tipos and tipos[c - 1] in FORMATO_EXCEL
                    and valor is not None and not isinstance(valor, str)):
                celda.number_format = FORMATO_EXCEL[tipos[c - 1]]
                celda.alignment = Alignment(horizontal='right')
            anchos[c] = max(anchos.get(c, 0), len(str(valor)) if valor is not None else 0)
        return r

    hoja.append([reporte['titulo']])
    hoja['A1'].font = Font(bold=True, size=14)
    hoja.append([reporte['subtitulo']])
    hoja.append(['Generado: ' + generado])
    hoja.append([])

    for etiqueta, valor, tipo in reporte.get('resumen', []):
        r = escribir((etiqueta, valor), tipos=('texto', tipo))
        hoja.cell(row=r, column=1).font = Font(bold=True)
    hoja.append([])

    for seccion in reporte['secciones']:
        hoja.append([seccion['titulo']])
        hoja.cell(row=hoja.max_row, column=1).font = Font(bold=True, size=12)
        tipos = [t for _, t in seccion['columnas']]
        r = escribir([n for n, _ in seccion['columnas']])
        for c in range(1, len(tipos) + 1):
            celda = hoja.cell(row=r, column=c)
            celda.font = Font(bold=True, color='FFFFFF')
            celda.fill = relleno
            celda.alignment = Alignment(horizontal='center')
        for fila in seccion['filas']:
            escribir(fila, tipos=tipos)
        if seccion.get('totales'):
            escribir(seccion['totales'], tipos=tipos, negrita=True)
        if not seccion['filas']:
            hoja.append(['(sin datos en este período)'])
        hoja.append([])

    if reporte.get('nota'):
        hoja.append([reporte['nota']])
        hoja.cell(row=hoja.max_row, column=1).font = Font(italic=True)

    for c, ancho in anchos.items():
        hoja.column_dimensions[hoja.cell(row=1, column=c).column_letter].width = min(max(ancho + 2, 12), 45)

    salida = io.BytesIO()
    libro.save(salida)
    return salida.getvalue()