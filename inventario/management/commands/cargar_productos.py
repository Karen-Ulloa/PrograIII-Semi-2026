from decimal import Decimal

from django.core.management.base import BaseCommand

from inventario.models import Categorias, Productos

# (categoria, nombre, precio_compra, precio_venta)
PRODUCTOS = [
    # --- Tornillería y fijación ---
    ("Tornillería y fijación", 'Tornillo para madera 1/4" x 2"', "0.04", "0.10"),
    ("Tornillería y fijación", 'Tornillo para madera 1/4" x 3"', "0.06", "0.12"),
    ("Tornillería y fijación", 'Tornillo goloso 10 x 1"', "0.03", "0.08"),
    ("Tornillería y fijación", 'Tornillo de fijación para lámina 14 x 1"', "0.05", "0.10"),
    ("Tornillería y fijación", 'Tornillo para drywall 6 x 1"', "0.02", "0.05"),
    ("Tornillería y fijación", 'Perno hexagonal grado 2 3/8" x 2"', "0.15", "0.35"),
    ("Tornillería y fijación", 'Tuerca hexagonal 1/4"', "0.02", "0.05"),
    ("Tornillería y fijación", 'Tuerca hexagonal 3/8"', "0.04", "0.10"),
    ("Tornillería y fijación", 'Arandela plana 1/4"', "0.02", "0.10"),
    ("Tornillería y fijación", 'Arandela de presión 3/8"', "0.05", "0.13"),
    ("Tornillería y fijación", 'Clavo con cabeza para madera 2" (libra)', "0.75", "1.25"),
    ("Tornillería y fijación", 'Clavo con cabeza para madera 3" (libra)', "0.75", "1.25"),
    ("Tornillería y fijación", 'Clavo para concreto 2" (libra)', "1.10", "1.75"),
    ("Tornillería y fijación", 'Clavo para concreto 3" (libra)', "1.10", "1.75"),
    ("Tornillería y fijación", 'Taquete / Tarugo plástico 1/4"', "0.02", "0.05"),
    ("Tornillería y fijación", 'Taquete / Tarugo plástico 3/8"', "0.04", "0.10"),
    # --- Lijas ---
    ("Lijas", "Lija para agua N° 80", "0.35", "0.75"),
    ("Lijas", "Lija para agua N° 120", "0.35", "0.75"),
    ("Lijas", "Lija para agua N° 220", "0.35", "0.75"),
    ("Lijas", "Lija para agua N° 400", "0.40", "0.80"),
    ("Lijas", "Lija para madera N° 60", "0.30", "1.00"),
    ("Lijas", "Lija para madera N° 100", "0.30", "0.60"),
    # --- Pinturas y accesorios ---
    ("Pinturas y accesorios", "Pintura de aceite Rojo Óxido (Galón)", "12.50", "18.00"),
    ("Pinturas y accesorios", "Pintura de aceite Blanco Hueso (Galón)", "13.00", "19.50"),
    ("Pinturas y accesorios", "Pintura de aceite Negro Mate (Galón)", "12.50", "18.00"),
    ("Pinturas y accesorios", "Pintura látex Blanco (Galón)", "9.50", "14.50"),
    ("Pinturas y accesorios", "Pintura látex Azul Colonial (Galón)", "10.00", "15.50"),
    ("Pinturas y accesorios", "Pintura látex Verde Bosque (Galón)", "10.00", "15.50"),
    ("Pinturas y accesorios", "Anti-corrosivo Gris (Galón)", "11.00", "16.50"),
    ("Pinturas y accesorios", "Thinner corriente (Galón)", "5.50", "8.50"),
    ("Pinturas y accesorios", "Solvente Mineral / Aguarrás (Galón)", "6.00", "9.00"),
    ("Pinturas y accesorios", 'Brocha para pintura 1"', "0.45", "1.00"),
    ("Pinturas y accesorios", 'Brocha para pintura 2"', "0.85", "1.75"),
    ("Pinturas y accesorios", 'Brocha para pintura 3"', "1.25", "2.50"),
    ("Pinturas y accesorios", 'Rodillo para pintura felpa 9"', "1.50", "3.00"),
    # --- Herramientas manuales ---
    ("Herramientas manuales", "Martillo de uña curva 16 oz", "4.25", "7.50"),
    ("Herramientas manuales", 'Alicate universal 7"', "3.50", "6.00"),
    ("Herramientas manuales", 'Tenaza de presión 10"', "5.00", "9.00"),
    ("Herramientas manuales", 'Destornillador plano 1/4" x 4"', "1.20", "2.50"),
    ("Herramientas manuales", 'Destornillador de estrella (Phillips) #2 x 4"', "1.20", "2.50"),
    ("Herramientas manuales", 'Llave ajustable (Cinta/Perica) 8"', "4.00", "7.50"),
    ("Herramientas manuales", "Cinta métrica (Flexómetro) 5 metros / 16 pies", "2.00", "4.00"),
    ("Herramientas manuales", 'Arco de sierra para metal 12"', "3.00", "5.50"),
    # --- Discos y brocas ---
    ("Discos y brocas", "Hoja de sierra para metal 18 dientes", "0.60", "1.25"),
    ("Discos y brocas", 'Disco de corte para metal 4 1/2" x 1/16"', "0.70", "1.35"),
    ("Discos y brocas", 'Disco de corte para concreto 4 1/2"', "2.50", "4.50"),
    ("Discos y brocas", 'Broca para concreto 1/4" x 4"', "0.90", "1.75"),
    ("Discos y brocas", 'Broca para concreto 3/8" x 6"', "1.40", "2.75"),
    ("Discos y brocas", 'Broca para metal HSS 1/8"', "0.50", "1.10"),
    ("Discos y brocas", 'Broca para metal HSS 1/4"', "0.90", "1.80"),
    # --- Eléctrico ---
    ("Eléctrico", "Foco LED 9W luz blanca (Rosca E27)", "0.85", "1.75"),
    ("Eléctrico", "Foco LED 12W luz blanca (Rosca E27)", "1.10", "2.25"),
    ("Eléctrico", "Foco LED 15W luz cálida (Rosca E27)", "1.40", "2.75"),
    ("Eléctrico", "Tomacorriente doble polarizado (Blanco)", "1.10", "2.25"),
    ("Eléctrico", "Interruptor sencillo de pared (Blanco)", "0.90", "1.85"),
    ("Eléctrico", "Cinta aislante negra 18m (3M o similar)", "0.80", "1.60"),
    ("Eléctrico", "Socket / Plafón de porcelana E27", "0.45", "1.00"),
    ("Eléctrico", "Breaker / Cordoncillo 1 polo 20A", "2.80", "5.00"),
    ("Eléctrico", "Cable eléctrico THHN N° 12 (Metro)", "0.45", "0.85"),
    ("Eléctrico", "Cable eléctrico THHN N° 14 (Metro)", "0.32", "0.65"),
    # --- Plomería ---
    ("Plomería", 'Tubo PVC agua potable 1/2" SDR 13.5 (6m)', "2.00", "3.60"),
    ("Plomería", 'Tubo PVC agua potable 3/4" SDR 21 (6m)', "2.80", "4.80"),
    ("Plomería", 'Codo PVC 1/2" a 90° para agua', "0.15", "0.35"),
    ("Plomería", 'Te PVC 1/2" para agua', "0.20", "0.45"),
    ("Plomería", "Pegamento para PVC (Pega PVC) 4 oz", "1.60", "3.00"),
    ("Plomería", 'Cinta de teflón 1/2" x 260"', "0.25", "0.60"),
    ("Plomería", 'Llave de chorro bronce 1/2"', "3.20", "6.00"),
    ("Plomería", "Silicón transparente uso general 280ml", "2.20", "4.00"),
    # --- Construcción ---
    ("Construcción", "Cemento CUSCATLÁNEO / HOLCIM (Bolsa 42.5 kg)", "7.80", "9.25"),
    ("Construcción", 'Varilla de hierro corrugado 3/8" (Grade 40 - 6m)', "2.60", "3.80"),
    ("Construcción", 'Varilla de hierro corrugado 1/2" (Grade 40 - 6m)', "4.60", "6.50"),
    ("Construcción", "Alambre de amarre (Libra)", "0.70", "1.20"),
    # --- Otros ---
    ("Otros", "Candado de hierro 40mm", "2.50", "4.80"),
    ("Otros", "Cuchilla / Exacto universal 18mm", "0.60", "1.25"),
    ("Otros", "Guantes de lona con puntos de PVC (Par)", "0.75", "1.50"),
]


class Command(BaseCommand):
    help = "Carga o actualiza los 75 productos del inventario real."

    def handle(self, *args, **options):
        creados = 0
        actualizados = 0
        for categoria, nombre, compra, venta in PRODUCTOS:
            cat, _ = Categorias.objects.get_or_create(nombre_categoria=categoria)
            producto, nuevo = Productos.objects.get_or_create(
                nombre_producto=nombre,
                defaults={
                    "precio_producto": Decimal(venta),
                    "precio_compra": Decimal(compra),
                    "id_categoria": cat,
                },
            )
            if nuevo:
                creados += 1
            else:
                producto.precio_producto = Decimal(venta)
                producto.precio_compra = Decimal(compra)
                producto.id_categoria = cat
                producto.save()
                actualizados += 1
        self.stdout.write(self.style.SUCCESS(
            f"Listo: {creados} productos creados, {actualizados} actualizados."
        ))