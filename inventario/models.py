from django.db import models

# Create your models here.
class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        managed = True
        db_table = 'categoria'

class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    id_categoria = models.ForeignKey(Categoria, models.DO_NOTHING, db_column='id_categoria')

    class Meta:
        managed = True
        db_table = 'producto'

class Proveedor(models.Model):
    id_proveedor = models.AutoField(primary_key=True)
    nombre_empresa = models.CharField(max_length=150)
    telefono = models.CharField(max_length=25, blank=True, null=True)
    email = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'proveedor'
    
class Talla(models.Model):
    id_talla = models.AutoField(primary_key=True)
    nombre_talla = models.CharField(max_length=10)
    tipo_talla = models.CharField(max_length=50)

    class Meta:
        managed = True
        db_table = 'talla'
    
class Stock(models.Model):
    id_stock = models.AutoField(primary_key=True)
    cantidad = models.IntegerField()
    stock_minimo = models.IntegerField(default=5)
    id_producto = models.ForeignKey(Producto, models.DO_NOTHING, db_column='id_producto')
    id_talla = models.ForeignKey('Talla', models.DO_NOTHING, db_column='id_talla')

    class Meta:
        managed = True
        db_table = 'stock'

class ProductoProveedor(models.Model):
    pk = models.CompositePrimaryKey('id_producto', 'id_proveedor')
    id_producto = models.ForeignKey(Producto, models.DO_NOTHING, db_column='id_producto')
    id_proveedor = models.ForeignKey('Proveedor', models.DO_NOTHING, db_column='id_proveedor')

    class Meta:
        managed = True
        db_table = 'producto_proveedor'