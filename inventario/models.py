from django.db import models

class Categorias(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre_categoria = models.CharField(max_length=100)
    class Meta:
        db_table = 'categorias'

class Ubicaciones(models.Model):
    id_ubicacion = models.AutoField(primary_key=True)
    pasillo = models.CharField(max_length=50)
    estante = models.CharField(max_length=50)
    class Meta:
        db_table = 'ubicaciones'

class MotivosMerma(models.Model):
    id_motivo = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100)
    class Meta:
        db_table = 'motivos_merma'

class Proveedores(models.Model):
    id_proveedor = models.AutoField(primary_key=True)
    nombre_proveedor = models.CharField(max_length=150)
    contacto_proveedor = models.CharField(max_length=100)
    class Meta:
        db_table = 'proveedores'

class Clientes(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20)
    class Meta:
        db_table = 'clientes'

class Empleados(models.Model):
    id_empleado = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    correo = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20)
    usuario = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    class Meta:
        db_table = 'empleados'

class MetodosPago(models.Model):
    id_metodo_pago = models.AutoField(primary_key=True)
    nombre_metodo = models.CharField(max_length=50)
    class Meta:
        db_table = 'metodos_pago'

class Productos(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre_producto = models.CharField(max_length=150)
    precio_producto = models.DecimalField(max_digits=10, decimal_places=2)
    id_categoria = models.ForeignKey(Categorias, on_delete=models.SET_NULL, null=True, db_column='id_categoria')
    id_ubicacion = models.ForeignKey(Ubicaciones, on_delete=models.SET_NULL, null=True, db_column='id_ubicacion')
    imagen = models.CharField(max_length=255, null=True, blank=True)
    class Meta:
        db_table = 'productos'

class RegistrosMerma(models.Model):
    id_merma = models.AutoField(primary_key=True)
    id_producto = models.ForeignKey(Productos, on_delete=models.CASCADE, db_column='id_producto')
    id_motivo = models.ForeignKey(MotivosMerma, on_delete=models.CASCADE, db_column='id_motivo')
    cantidad = models.IntegerField()
    fecha_merma = models.DateTimeField()
    class Meta:
        db_table = 'registos_merma'

class ProductoProveedo(models.Model):
    id_producto = models.ForeignKey(Productos, on_delete=models.CASCADE, db_column='id_producto')
    id_proveedor = models.ForeignKey(Proveedores, on_delete=models.CASCADE, db_column='id_proveedor')
    class Meta:
        db_table = 'producto_proveedo'
        unique_together = (('id_producto', 'id_proveedor'),)

class OrdenesCompra(models.Model):
    id_compra = models.AutoField(primary_key=True)
    id_proveedor = models.ForeignKey(Proveedores, on_delete=models.CASCADE, db_column='id_proveedor')
    fecha_compra = models.DateTimeField()
    class Meta:
        db_table = 'ordenes_compra'

class Ventas(models.Model):
    id_venta = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Clientes, on_delete=models.SET_NULL, null=True, db_column='id_cliente')
    id_empleado = models.ForeignKey(Empleados, on_delete=models.SET_NULL, null=True, db_column='id_empleado')
    id_metodo_pago = models.ForeignKey(MetodosPago, on_delete=models.SET_NULL, null=True, db_column='id_metodo_pago')
    fecha_venta = models.DateTimeField()
    class Meta:
        db_table = 'ventas'

class DetalleCompra(models.Model):
    id_detalle_compra = models.AutoField(primary_key=True)
    id_compra = models.ForeignKey(OrdenesCompra, on_delete=models.CASCADE, db_column='id_compra')
    id_producto = models.ForeignKey(Productos, on_delete=models.CASCADE, db_column='id_producto')
    cantidad = models.IntegerField()
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        db_table = 'detalle_compra'

class DetalleVenta(models.Model):
    id_detalle_venta = models.AutoField(primary_key=True)
    id_venta = models.ForeignKey(Ventas, on_delete=models.CASCADE, db_column='id_venta')
    id_producto = models.ForeignKey(Productos, on_delete=models.CASCADE, db_column='id_producto')
    cantidad = models.IntegerField()
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        db_table = 'detalle_venta'
