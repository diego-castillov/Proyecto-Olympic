# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

# Se hizo un cambio AQUI!


class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'categoria'


class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    usuario_id = models.IntegerField(unique=True, blank=True, null=True)
    nombre = models.CharField(max_length=75)
    apellido = models.CharField(max_length=75)
    email = models.CharField(max_length=150, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion_envio = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cliente'


class DetallePedido(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    id_pedido = models.ForeignKey('Pedido', models.DO_NOTHING, db_column='id_pedido')
    id_producto = models.ForeignKey('Producto', models.DO_NOTHING, db_column='id_producto')
    id_talla = models.ForeignKey('Talla', models.DO_NOTHING, db_column='id_talla')

    class Meta:
        managed = False
        db_table = 'detalle_pedido'


class Pedido(models.Model):
    id_pedido = models.AutoField(primary_key=True)
    fecha = models.DateTimeField(blank=True, null=True)
    estado_pedido = models.CharField(max_length=50, blank=True, null=True)
    metodo_pago = models.CharField(max_length=50, blank=True, null=True)
    estado_pago = models.CharField(max_length=50, blank=True, null=True)
    fecha_pago = models.DateTimeField(blank=True, null=True)
    comprobante_url = models.CharField(max_length=255, blank=True, null=True)
    id_cliente = models.ForeignKey(Cliente, models.DO_NOTHING, db_column='id_cliente')
    vendedor_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pedido'


class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    id_categoria = models.ForeignKey(Categoria, models.DO_NOTHING, db_column='id_categoria')

    class Meta:
        managed = False
        db_table = 'producto'


class ProductoProveedor(models.Model):
    pk = models.CompositePrimaryKey('id_producto', 'id_proveedor')
    id_producto = models.ForeignKey(Producto, models.DO_NOTHING, db_column='id_producto')
    id_proveedor = models.ForeignKey('Proveedor', models.DO_NOTHING, db_column='id_proveedor')

    class Meta:
        managed = False
        db_table = 'producto_proveedor'


class Proveedor(models.Model):
    id_proveedor = models.AutoField(primary_key=True)
    nombre_empresa = models.CharField(max_length=150)
    telefono = models.CharField(max_length=25, blank=True, null=True)
    email = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'proveedor'


class Stock(models.Model):
    id_stock = models.AutoField(primary_key=True)
    cantidad = models.IntegerField()
    stock_minimo = models.IntegerField()
    id_producto = models.ForeignKey(Producto, models.DO_NOTHING, db_column='id_producto')
    id_talla = models.ForeignKey('Talla', models.DO_NOTHING, db_column='id_talla')

    class Meta:
        managed = False
        db_table = 'stock'


class Talla(models.Model):
    id_talla = models.AutoField(primary_key=True)
    nombre_talla = models.CharField(max_length=10)
    tipo_talla = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'talla'
