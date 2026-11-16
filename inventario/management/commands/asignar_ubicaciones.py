from django.core.management.base import BaseCommand

from inventario.models import Productos, Ubicaciones

# (producto, bodega, pasillo o zona, estante / módulo / patio, nivel)
# Asignación según el documento de bodegas. Los discos de corte, las brocas y el breaker no
# aparecen en el documento, así que se ubicaron junto a los productos más parecidos
# (corte, taquetes, tornillos para metal y cajas eléctricas). El dueño puede cambiarlos
# desde Editar producto.
ASIGNACION = [
    ('Tornillo para madera 1/4" x 2"', 'Bodega 1', 'Pasillo 1', 'Estante 2', 'Nivel 1'),
    ('Tornillo para madera 1/4" x 3"', 'Bodega 1', 'Pasillo 1', 'Estante 2', 'Nivel 2'),
    ('Tornillo goloso 10 x 1"', 'Bodega 1', 'Pasillo 1', 'Estante 2', 'Nivel 3'),
    ('Tornillo de fijación para lámina 14 x 1"', 'Bodega 1', 'Pasillo 1', 'Estante 3', 'Nivel 1'),
    ('Tornillo para drywall 6 x 1"', 'Bodega 1', 'Pasillo 1', 'Estante 5', 'Nivel 3'),
    ('Perno hexagonal grado 2 3/8" x 2"', 'Bodega 1', 'Pasillo 1', 'Estante 3', 'Nivel 2'),
    ('Tuerca hexagonal 1/4"', 'Bodega 1', 'Pasillo 1', 'Estante 3', 'Nivel 2'),
    ('Tuerca hexagonal 3/8"', 'Bodega 1', 'Pasillo 1', 'Estante 3', 'Nivel 2'),
    ('Arandela plana 1/4"', 'Bodega 1', 'Pasillo 1', 'Estante 4', 'Nivel 4'),
    ('Arandela de presión 3/8"', 'Bodega 1', 'Pasillo 1', 'Estante 4', 'Nivel 4'),
    ('Clavo con cabeza para madera 2" (libra)', 'Bodega 1', 'Pasillo 1', 'Estante 1', 'Nivel 1'),
    ('Clavo con cabeza para madera 3" (libra)', 'Bodega 1', 'Pasillo 1', 'Estante 1', 'Nivel 1'),
    ('Clavo para concreto 2" (libra)', 'Bodega 1', 'Pasillo 1', 'Estante 1', 'Nivel 3'),
    ('Clavo para concreto 3" (libra)', 'Bodega 1', 'Pasillo 1', 'Estante 1', 'Nivel 3'),
    ('Taquete / Tarugo plástico 1/4"', 'Bodega 1', 'Pasillo 1', 'Estante 4', 'Nivel 2'),
    ('Taquete / Tarugo plástico 3/8"', 'Bodega 1', 'Pasillo 1', 'Estante 4', 'Nivel 2'),
    ('Lija para agua N° 80', 'Bodega 1', 'Pasillo 5', 'Estante 4', 'Nivel 2'),
    ('Lija para agua N° 120', 'Bodega 1', 'Pasillo 5', 'Estante 4', 'Nivel 2'),
    ('Lija para agua N° 220', 'Bodega 1', 'Pasillo 5', 'Estante 4', 'Nivel 2'),
    ('Lija para agua N° 400', 'Bodega 1', 'Pasillo 5', 'Estante 4', 'Nivel 2'),
    ('Lija para madera N° 60', 'Bodega 1', 'Pasillo 5', 'Estante 4', 'Nivel 1'),
    ('Lija para madera N° 100', 'Bodega 1', 'Pasillo 5', 'Estante 4', 'Nivel 1'),
    ('Pintura de aceite Rojo Óxido (Galón)', 'Bodega 1', 'Pasillo 5', 'Estante 1', 'Nivel 1'),
    ('Pintura de aceite Blanco Hueso (Galón)', 'Bodega 1', 'Pasillo 5', 'Estante 1', 'Nivel 1'),
    ('Pintura de aceite Negro Mate (Galón)', 'Bodega 1', 'Pasillo 5', 'Estante 1', 'Nivel 1'),
    ('Pintura látex Blanco (Galón)', 'Bodega 1', 'Pasillo 5', 'Estante 1', 'Nivel 3'),
    ('Pintura látex Azul Colonial (Galón)', 'Bodega 1', 'Pasillo 5', 'Estante 1', 'Nivel 3'),
    ('Pintura látex Verde Bosque (Galón)', 'Bodega 1', 'Pasillo 5', 'Estante 1', 'Nivel 3'),
    ('Anti-corrosivo Gris (Galón)', 'Bodega 1', 'Pasillo 5', 'Estante 1', 'Nivel 1'),
    ('Thinner corriente (Galón)', 'Bodega 1', 'Pasillo 5', 'Estante 4', 'Nivel 4'),
    ('Solvente Mineral / Aguarrás (Galón)', 'Bodega 1', 'Pasillo 5', 'Estante 4', 'Nivel 4'),
    ('Brocha para pintura 1"', 'Bodega 1', 'Pasillo 5', 'Estante 3', 'Nivel 1'),
    ('Brocha para pintura 2"', 'Bodega 1', 'Pasillo 5', 'Estante 3', 'Nivel 1'),
    ('Brocha para pintura 3"', 'Bodega 1', 'Pasillo 5', 'Estante 3', 'Nivel 1'),
    ('Rodillo para pintura felpa 9"', 'Bodega 1', 'Pasillo 5', 'Estante 3', 'Nivel 2'),
    ('Martillo de uña curva 16 oz', 'Bodega 1', 'Pasillo 2', 'Estante 1', 'Nivel 1'),
    ('Alicate universal 7"', 'Bodega 1', 'Pasillo 2', 'Estante 3', 'Nivel 1'),
    ('Tenaza de presión 10"', 'Bodega 1', 'Pasillo 2', 'Estante 3', 'Nivel 2'),
    ('Destornillador plano 1/4" x 4"', 'Bodega 1', 'Pasillo 2', 'Estante 2', 'Nivel 1'),
    ('Destornillador de estrella (Phillips) #2 x 4"', 'Bodega 1', 'Pasillo 2', 'Estante 2', 'Nivel 2'),
    ('Llave ajustable (Cinta/Perica) 8"', 'Bodega 1', 'Pasillo 2', 'Estante 3', 'Nivel 4'),
    ('Cinta métrica (Flexómetro) 5 metros / 16 pies', 'Bodega 1', 'Pasillo 2', 'Estante 4', 'Nivel 1'),
    ('Arco de sierra para metal 12"', 'Bodega 1', 'Pasillo 2', 'Estante 4', 'Nivel 3'),
    ('Hoja de sierra para metal 18 dientes', 'Bodega 1', 'Pasillo 2', 'Estante 4', 'Nivel 3'),
    ('Foco LED 9W luz blanca (Rosca E27)', 'Bodega 1', 'Pasillo 4', 'Estante 4', 'Nivel 1'),
    ('Foco LED 12W luz blanca (Rosca E27)', 'Bodega 1', 'Pasillo 4', 'Estante 4', 'Nivel 1'),
    ('Foco LED 15W luz cálida (Rosca E27)', 'Bodega 1', 'Pasillo 4', 'Estante 4', 'Nivel 2'),
    ('Tomacorriente doble polarizado (Blanco)', 'Bodega 1', 'Pasillo 4', 'Estante 2', 'Nivel 2'),
    ('Interruptor sencillo de pared (Blanco)', 'Bodega 1', 'Pasillo 4', 'Estante 2', 'Nivel 1'),
    ('Cinta aislante negra 18m (3M o similar)', 'Bodega 1', 'Pasillo 4', 'Estante 3', 'Nivel 1'),
    ('Socket / Plafón de porcelana E27', 'Bodega 1', 'Pasillo 4', 'Estante 4', 'Nivel 3'),
    ('Cable eléctrico THHN N° 12 (Metro)', 'Bodega 1', 'Pasillo 4', 'Estante 1', 'Nivel 1'),
    ('Cable eléctrico THHN N° 14 (Metro)', 'Bodega 1', 'Pasillo 4', 'Estante 1', 'Nivel 2'),
    ('Tubo PVC agua potable 1/2" SDR 13.5 (6m)', 'Bodega 1', 'Pasillo 3', 'Estante 1', 'Nivel 1'),
    ('Tubo PVC agua potable 3/4" SDR 21 (6m)', 'Bodega 1', 'Pasillo 3', 'Estante 1', 'Nivel 1'),
    ('Codo PVC 1/2" a 90° para agua', 'Bodega 1', 'Pasillo 3', 'Estante 2', 'Nivel 1'),
    ('Te PVC 1/2" para agua', 'Bodega 1', 'Pasillo 3', 'Estante 2', 'Nivel 3'),
    ('Pegamento para PVC (Pega PVC) 4 oz', 'Bodega 1', 'Pasillo 3', 'Estante 4', 'Nivel 3'),
    ('Cinta de teflón 1/2" x 260"', 'Bodega 1', 'Pasillo 3', 'Estante 4', 'Nivel 4'),
    ('Llave de chorro bronce 1/2"', 'Bodega 1', 'Pasillo 3', 'Estante 4', 'Nivel 1'),
    ('Silicón transparente uso general 280ml', 'Bodega 1', 'Pasillo 5', 'Estante 2', 'Nivel 3'),
    ('Cemento CUSCATLÁNEO / HOLCIM (Bolsa 42.5 kg)', 'Bodega 2', 'Zona 2', 'Módulo 1', 'Nivel 1'),
    ('Varilla de hierro corrugado 3/8" (Grade 40 - 6m)', 'Bodega 2', 'Zona 4', 'Patio 1', 'Nivel 1'),
    ('Varilla de hierro corrugado 1/2" (Grade 40 - 6m)', 'Bodega 2', 'Zona 4', 'Patio 1', 'Nivel 1'),
    ('Alambre de amarre (Libra)', 'Bodega 2', 'Zona 4', 'Patio 1', 'Nivel 4'),
    ('Candado de hierro 40mm', 'Bodega 1', 'Pasillo 6', 'Estante 2', 'Nivel 1'),
    ('Cuchilla / Exacto universal 18mm', 'Bodega 1', 'Pasillo 2', 'Estante 4', 'Nivel 2'),
    ('Guantes de lona con puntos de PVC (Par)', 'Bodega 1', 'Pasillo 6', 'Estante 1', 'Nivel 1'),
    ('Disco de corte para metal 4 1/2" x 1/16"', 'Bodega 1', 'Pasillo 2', 'Estante 4', 'Nivel 3'),
    ('Disco de corte para concreto 4 1/2"', 'Bodega 1', 'Pasillo 2', 'Estante 4', 'Nivel 3'),
    ('Broca para concreto 1/4" x 4"', 'Bodega 1', 'Pasillo 1', 'Estante 4', 'Nivel 2'),
    ('Broca para concreto 3/8" x 6"', 'Bodega 1', 'Pasillo 1', 'Estante 4', 'Nivel 2'),
    ('Broca para metal HSS 1/8"', 'Bodega 1', 'Pasillo 1', 'Estante 3', 'Nivel 1'),
    ('Broca para metal HSS 1/4"', 'Bodega 1', 'Pasillo 1', 'Estante 3', 'Nivel 1'),
    ('Breaker / Cordoncillo 1 polo 20A', 'Bodega 1', 'Pasillo 4', 'Estante 2', 'Nivel 4'),
]


class Command(BaseCommand):
    help = "Asigna la ubicación (bodega, pasillo, estante y nivel) a los productos del catálogo."

    def add_arguments(self, parser):
        parser.add_argument('--sobrescribir', action='store_true',
                            help='Cambia también la ubicación de productos que ya tienen una')

    def handle(self, *args, **options):
        if not Ubicaciones.objects.exclude(bodega='').exists():
            self.stdout.write(self.style.ERROR(
                "No hay ubicaciones. Primero ejecuta: python manage.py cargar_ubicaciones"))
            return

        asignados = omitidos = faltan = 0
        for nombre, bodega, area, seccion, nivel in ASIGNACION:
            producto = Productos.objects.filter(nombre_producto=nombre).first()
            if producto is None:
                faltan += 1
                continue
            if producto.id_ubicacion_id and not options['sobrescribir']:
                omitidos += 1
                continue
            ubicacion = Ubicaciones.objects.filter(
                bodega=bodega, pasillo__startswith=area + ' ·',
                estante__startswith=seccion + ' ·', nivel=nivel).first()
            if ubicacion is None:
                faltan += 1
                continue
            producto.id_ubicacion = ubicacion
            producto.save(update_fields=['id_ubicacion'])
            asignados += 1

        self.stdout.write(self.style.SUCCESS(
            f"Listo: {asignados} productos con ubicación, {omitidos} ya tenían una, "
            f"{faltan} no se encontraron."))
        sin_ubicacion = Productos.objects.filter(id_ubicacion__isnull=True).order_by('nombre_producto')
        if sin_ubicacion.exists():
            self.stdout.write("Productos sin ubicación (hay que definirla):")
            for p in sin_ubicacion:
                self.stdout.write(f"  - {p.nombre_producto}")