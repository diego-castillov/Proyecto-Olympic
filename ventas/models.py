from django.db import models

# Create your models here.
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
    
    # Calcula el total sumando los detalles de este pedido
    @property
    def total_pedido(self):
        detalles = self.detallepedido_set.all()
        return sum(detalle.cantidad * detalle.precio_unitario for detalle in detalles)

class DetallePedido(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    id_pedido = models.ForeignKey('Pedido', models.DO_NOTHING, db_column='id_pedido')
    id_producto = models.ForeignKey('inventario.Producto', models.DO_NOTHING, db_column='id_producto')
    id_talla = models.ForeignKey('inventario.Talla', models.DO_NOTHING, db_column='id_talla')

    class Meta:
        managed = False
        db_table = 'detalle_pedido'

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario