"""
Lectura y validación de archivos de importación de productos (archivo nuevo).
No usa Django ni la base de datos: solo lee .xlsx/.csv y valida filas.
"""
import csv
import io
import logging
import re
import unicodedata
from decimal import Decimal, InvalidOperation

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill

logger = logging.getLogger(__name__)

MAX_BYTES = 5 * 1024 * 1024
MAX_FILAS = 2000
CODIGO_VALIDO = re.compile(r'[A-Za-z0-9._\-]{3,50}')

ENCABEZADOS = ['nombre_producto', 'categoria', 'precio_compra', 'precio_venta', 'stock',
               'stock_minimo', 'codigo_barras', 'bodega', 'pasillo', 'estante', 'nivel']
OBLIGATORIAS = ('nombre_producto', 'categoria', 'precio_venta')

ALIAS = {
    'nombre_producto': ('nombre_producto', 'nombre', 'producto', 'nombre_del_producto'),
    'categoria': ('categoria', 'categorias'),
    'precio_compra': ('precio_compra', 'costo', 'precio_de_compra'),
    'precio_venta': ('precio_venta', 'precio', 'precio_de_venta', 'precio_producto'),
    'stock': ('stock', 'existencia', 'existencias', 'cantidad'),
    'stock_minimo': ('stock_minimo', 'minimo', 'stock_min'),
    'codigo_barras': ('codigo_barras', 'codigo', 'codigo_de_barras', 'codigo_qr'),
    'bodega': ('bodega',),
    'pasillo': ('pasillo',),
    'estante': ('estante',),
    'nivel': ('nivel',),
}
_ALIAS_A_CLAVE = {a: clave for clave, lista in ALIAS.items() for a in lista}

# nombre, categoría, compra, venta, stock, mínimo, código, bodega, pasillo, estante, nivel
EJEMPLOS = [
    ['Cemento gris 42.5 kg', 'Construcción', 8.50, 10.75, 60, 20, 'CEM-0001', 'Bodega 1', 'Pasillo 1', 'Estante 1', 'Nivel 1'],
    ['Clavo de acero 2 pulgadas (libra)', 'Ferretería', 0.70, 1.10, 120, 30, '', 'Bodega 1', 'Pasillo 2', 'Estante 1', 'Nivel 2'],
    ['Tubo PVC 1/2 pulgada x 6 m', 'Plomería', 2.20, 3.50, 45, 15, '', 'Bodega 1', 'Pasillo 3', 'Estante 2', 'Nivel 1'],
    ['Pintura látex blanca (galón)', 'Pintura', 14.00, 19.90, 18, 6, 'PIN-0001', 'Bodega 2', 'Pasillo 1', 'Estante 1', 'Nivel 2'],
    ['Martillo de uña 16 oz', 'Herramientas', 5.00, 8.25, 12, 4, '', 'Bodega 2', 'Pasillo 2', 'Estante 3', 'Nivel 1'],
    ['Machete 22 pulgadas', 'Herramientas', 4.50, 7.50, 25, 8, '', 'Bodega 2', 'Pasillo 2', 'Estante 3', 'Nivel 2'],
    ['Alambre de amarre (libra)', 'Construcción', 0.80, 1.25, 90, 25, '', 'Bodega 1', 'Pasillo 1', 'Estante 2', 'Nivel 1'],
    ['Fertilizante 15-15-15 (quintal)', 'Agroquímicos', 28.00, 36.00, 30, 10, 'FER-0001', 'Bodega 3', 'Pasillo 1', 'Estante 1', 'Nivel 1'],
    ['Manguera 1/2 pulgada (metro)', 'Riego', 0.60, 1.00, 200, 50, '', 'Bodega 3', 'Pasillo 2', 'Estante 1', 'Nivel 1'],
    ['Candado de seguridad 40 mm', 'Ferretería', 3.00, 5.25, 20, 6, '', 'Bodega 2', 'Pasillo 1', 'Estante 3', 'Nivel 1'],
]

INSTRUCCIONES = [
    'CÓMO USAR ESTA PLANTILLA',
    '',
    '1. Borra las filas de ejemplo de la hoja "Productos" y escribe tus productos (una fila por producto).',
    '2. No cambies ni borres la fila de encabezados (la primera fila).',
    '3. Columnas obligatorias: nombre_producto, categoria y precio_venta.',
    '4. Columnas opcionales: precio_compra, stock, stock_minimo, codigo_barras, bodega, pasillo, estante, nivel.',
    '5. Si pones ubicación, escribe bodega, pasillo y estante juntos (el nivel es opcional).',
    '6. Si la categoría o la ubicación no existen, el sistema las crea.',
    '7. Esta plantilla es solo para productos NUEVOS: si un producto ya existe (mismo nombre o mismo',
    '   código de barras) se marca como error y no se modifica. Para cambiar precios o datos de',
    '   productos existentes usa la pestaña "Actualizar productos".',
    '8. Los precios van en dólares, sin el símbolo $ (ejemplo: 10.75).',
    '9. Guarda como .xlsx (o como .csv) y súbelo en la pestaña "Productos nuevos".',
    '',
    'Límites: máximo 2000 filas y 5 MB por archivo.',
]


class ErrorArchivo(ValueError):
    """Problema con el archivo completo (no con una fila)."""


def _norm(texto):
    t = unicodedata.normalize('NFD', str(texto or '').strip().lower())
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    t = re.sub(r'[^a-z0-9]+', '_', t).strip('_')
    return re.sub(r'_usd$', '', t)


def _filas_xlsx(contenido):
    try:
        libro = load_workbook(io.BytesIO(contenido), read_only=True, data_only=True)
    except Exception:
        logger.exception('No se pudo abrir el archivo xlsx.')
        raise ErrorArchivo('No se pudo leer el archivo. Verifica que sea un .xlsx válido '
                           '(no un .xls antiguo) y que no esté dañado.')
    try:
        hoja = libro.worksheets[0]
        return [list(f) for f in hoja.iter_rows(values_only=True)]
    except Exception:
        logger.exception('No se pudo leer la hoja del xlsx.')
        raise ErrorArchivo('No se pudo leer la primera hoja del archivo.')
    finally:
        libro.close()


def _filas_csv(contenido):
    try:
        texto = contenido.decode('utf-8-sig')
    except UnicodeDecodeError:
        texto = contenido.decode('latin-1')
    primera = texto.splitlines()[0] if texto.strip() else ''
    delimitador = ';' if primera.count(';') > primera.count(',') else ','
    return [list(f) for f in csv.reader(io.StringIO(texto), delimiter=delimitador)]


def leer_archivo(nombre_archivo, contenido, tipo='nuevos'):
    """Devuelve [(numero_de_fila_en_el_archivo, {clave: valor_crudo}), ...]."""
    if len(contenido) > MAX_BYTES:
        raise ErrorArchivo('El archivo pesa demasiado (máximo 5 MB).')
    nombre = nombre_archivo.lower()
    if nombre.endswith('.xlsx'):
        filas = _filas_xlsx(contenido)
    elif nombre.endswith('.csv'):
        filas = _filas_csv(contenido)
    else:
        raise ErrorArchivo('Formato no permitido. Sube un archivo .xlsx o .csv.')

    if not filas or not any(c not in (None, '') for c in filas[0]):
        raise ErrorArchivo('El archivo está vacío o la primera fila no tiene encabezados.')

    columnas = {}
    for indice, celda in enumerate(filas[0]):
        clave = _ALIAS_A_CLAVE.get(_norm(celda))
        if clave is None:
            continue  # columnas desconocidas se ignoran
        if clave in columnas:
            raise ErrorArchivo(f'La columna "{clave}" aparece repetida en los encabezados.')
        columnas[clave] = indice
    if tipo == 'actualizar':
        if 'nombre_producto' not in columnas and 'codigo_barras' not in columnas:
            raise ErrorArchivo('Para actualizar necesito al menos una de estas columnas para identificar '
                               'cada producto: nombre_producto o codigo_barras. Descarga tus productos '
                               'actuales para ver los encabezados correctos.')
    else:
        faltan = [c for c in OBLIGATORIAS if c not in columnas]
        if faltan:
            raise ErrorArchivo('Faltan columnas obligatorias: ' + ', '.join(faltan) +
                               '. Descarga la plantilla para ver los encabezados correctos.')

    resultado = []
    for numero, fila in enumerate(filas[1:], start=2):
        valores = {clave: (fila[i] if i < len(fila) else None) for clave, i in columnas.items()}
        if all(v in (None, '') or str(v).strip() == '' for v in valores.values()):
            continue  # fila totalmente vacía
        resultado.append((numero, valores))
    if not resultado:
        raise ErrorArchivo('El archivo no tiene filas con datos debajo de los encabezados.')
    if len(resultado) > MAX_FILAS:
        raise ErrorArchivo(f'El archivo tiene más de {MAX_FILAS} filas. Divídelo en varios archivos.')
    return resultado


def _texto(valor):
    if valor is None:
        return ''
    if isinstance(valor, float) and valor.is_integer():
        valor = int(valor)
    return ' '.join(str(valor).split())


def _a_decimal(valor):
    if isinstance(valor, bool):
        raise ValueError
    if isinstance(valor, (int, float, Decimal)):
        crudo = str(valor)
    else:
        crudo = _texto(valor).replace('$', '').replace(' ', '')
        if ',' in crudo and '.' in crudo:
            crudo = crudo.replace(',', '')
        else:
            crudo = crudo.replace(',', '.')
    try:
        d = Decimal(crudo)
    except InvalidOperation:
        raise ValueError
    if not d.is_finite() or d < 0 or d > Decimal('99999999.99'):
        raise ValueError
    return d.quantize(Decimal('0.01'))


def _a_entero(valor):
    d = _a_decimal(valor)
    if d != d.to_integral_value() or d > 9999999:
        raise ValueError
    return int(d)


def validar_fila(valores, tipo='nuevos'):
    """
    Devuelve (datos, errores). Si hay errores, datos es None.
      tipo 'nuevos'     : nombre, categoría y precio de venta son obligatorios.
      tipo 'actualizar' : basta el nombre o el código de barras para identificar el producto;
                          todo lo demás es opcional (vacío = no cambiar).
    """
    nuevo = tipo != 'actualizar'
    errores = []
    datos = {}

    nombre = _texto(valores.get('nombre_producto'))
    codigo = _texto(valores.get('codigo_barras'))
    if nuevo and not nombre:
        errores.append('Falta el nombre del producto.')
    if not nuevo and not nombre and not codigo:
        errores.append('Falta el nombre o el código de barras para identificar el producto.')
    if len(nombre) > 150:
        errores.append('El nombre pasa de 150 caracteres.')
    datos['nombre'] = nombre

    categoria = _texto(valores.get('categoria'))
    if nuevo and not categoria:
        errores.append('Falta la categoría.')
    elif len(categoria) > 100:
        errores.append('La categoría pasa de 100 caracteres.')
    datos['categoria'] = categoria

    def numero(clave, convertir, etiqueta, obligatorio=False):
        crudo = valores.get(clave)
        if _texto(crudo) == '':
            if obligatorio:
                errores.append(f'Falta {etiqueta}.')
            return None
        try:
            return convertir(crudo)
        except ValueError:
            errores.append(f'{etiqueta.capitalize()} no es válido ("{_texto(crudo)}").')
            return None

    datos['precio_venta'] = numero('precio_venta', _a_decimal, 'el precio de venta', obligatorio=nuevo)
    datos['precio_compra'] = numero('precio_compra', _a_decimal, 'el precio de compra')
    datos['stock'] = numero('stock', _a_entero, 'el stock')
    datos['stock_minimo'] = numero('stock_minimo', _a_entero, 'el stock mínimo')

    if codigo and not CODIGO_VALIDO.fullmatch(codigo):
        errores.append('El código de barras solo puede tener letras, números, punto, guion o '
                       'guion bajo (de 3 a 50 caracteres).')
    datos['codigo'] = codigo or None

    bodega, pasillo = _texto(valores.get('bodega')), _texto(valores.get('pasillo'))
    estante, nivel = _texto(valores.get('estante')), _texto(valores.get('nivel'))
    datos['ubicacion'] = None
    if bodega or pasillo or estante or nivel:
        if not (bodega and pasillo and estante):
            errores.append('Para la ubicación escribe bodega, pasillo y estante juntos.')
        elif len(bodega) > 50 or len(pasillo) > 120 or len(estante) > 120 or len(nivel) > 30:
            errores.append('Algún dato de la ubicación es demasiado largo.')
        else:
            datos['ubicacion'] = (bodega, pasillo, estante, nivel)

    return (None, errores) if errores else (datos, [])


INSTRUCCIONES_ACTUALIZAR = [
    'CÓMO ACTUALIZAR PRODUCTOS CON ESTE ARCHIVO',
    '',
    '1. Este archivo trae tus productos tal como están hoy en el sistema.',
    '2. Cambia solo lo que necesites (por ejemplo precio_venta) y deja el resto igual.',
    '3. Cada producto se identifica por su codigo_barras o, si no tiene, por su nombre_producto.',
    '   Si cambias el nombre de un producto que no tiene código, el sistema no lo encontrará.',
    '4. Una celda vacía significa "no cambiar ese dato".',
    '5. No agregues productos nuevos aquí: para eso usa la pestaña "Productos nuevos".',
    '6. El stock solo se modifica si eliges "Reemplazar" o "Sumar" en la pantalla al importar.',
    '   Descarga este archivo justo antes de editarlo: las ventas posteriores no se reflejan en él.',
    '7. Guarda como .xlsx y súbelo en la pestaña "Actualizar productos".',
    '',
    'Límites: máximo 2000 filas y 5 MB por archivo.',
]


def _armar_libro(filas, instrucciones):
    libro = Workbook()
    hoja = libro.active
    hoja.title = 'Productos'
    hoja.append(ENCABEZADOS)
    for fila in filas:
        hoja.append(fila)

    relleno = PatternFill('solid', fgColor='5A1016')
    for celda in hoja[1]:
        celda.font = Font(bold=True, color='FFFFFF')
        celda.fill = relleno
        celda.alignment = Alignment(horizontal='center')
    for letra, ancho in zip('ABCDEFGHIJK', (38, 16, 14, 14, 9, 13, 16, 12, 12, 12, 10)):
        hoja.column_dimensions[letra].width = ancho
    for fila in hoja.iter_rows(min_row=2, min_col=3, max_col=4):
        for celda in fila:
            celda.number_format = '0.00'
    for fila in hoja.iter_rows(min_row=2, min_col=7, max_col=7):
        for celda in fila:
            celda.number_format = '@'  # los códigos se guardan como texto
    hoja.freeze_panes = 'A2'

    ayuda = libro.create_sheet('Instrucciones')
    for linea in instrucciones:
        ayuda.append([linea])
    ayuda['A1'].font = Font(bold=True, size=13)
    ayuda.column_dimensions['A'].width = 100

    salida = io.BytesIO()
    libro.save(salida)
    return salida.getvalue()


def generar_plantilla():
    """Plantilla con ejemplos para cargar productos nuevos."""
    return _armar_libro(EJEMPLOS, INSTRUCCIONES)


def generar_exportacion(filas):
    """Archivo con los productos actuales, listo para editar y volver a subir."""
    return _armar_libro(filas, INSTRUCCIONES_ACTUALIZAR)