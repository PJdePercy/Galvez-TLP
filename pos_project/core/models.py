from django.db import models
from post_project.choices import EstadoEntidades,EstadoOrden
import uuid
from django.contrib.auth import get_user_model
Usuario = get_user_model()


class GrupoArticulo(models.Model):
    grupo_id = models.UUIDField(primary_key=True)
    codigo_grupo = models.CharField(max_length=5, null=False)
    nombre_grupo = models.CharField(max_length=150, null=False)
    estado = models.IntegerField(choices=EstadoEntidades, default = EstadoEntidades.ACTIVO)
    
    def _str_(self):
        return self.nombre_grupo
    
    class Meta:
        db_table = ("grupos_articulos")
        ordering = ["codigo_grupo"]

class LineaArticulo(models.Model):
    linea_id = models.UUIDField(primary_key=True)
    codigo_linea = models.CharField(max_length=10, null=False)
    grupo = models.ForeignKey(GrupoArticulo, on_delete=models.RESTRICT, null=False, related_name='grupo_linea')
    nombre_linea = models.CharField(max_length=150, null=False)
    estado = models.IntegerField(choices=EstadoEntidades, default = EstadoEntidades.ACTIVO)
    
    class Meta:
        db_table = ("lineas_articulos")
        ordering = ["codigo_linea"]
        
class CanalCliente(models.Model):
    canal_id = models.CharField(max_length=3, primary_key=True)
    nombre_canal = models.CharField(max_length=100, null=False)

    class Meta:
        db_table = 'canal_cliente'
        ordering = ['nombre_canal']

class Cliente(models.Model):
    cliente_id = models.UUIDField(primary_key=True)
    tipo_identificacion = models.CharField(max_length=1)
    nro_identificacion = models.CharField(max_length=11)
    nombres = models.CharField(max_length=150)
    direccion = models.CharField(max_length=150)
    correo_electronico = models.CharField(max_length=255)
    nro_movil = models.CharField(max_length=15)
    estado = models.IntegerField()
    canal = models.ForeignKey(CanalCliente, on_delete=models.RESTRICT, db_column='canal_id')

    class Meta:
        db_table = 'clientes'
        ordering = ['nro_identificacion']
        
class Articulo(models.Model):
    articulo_id = models.UUIDField(primary_key=True)
    codigo_articulo = models.CharField(max_length=25)
    codigo_barras = models.CharField(max_length=25)
    descripcion = models.CharField(max_length=150)
    presentacion = models.CharField(max_length=100)
    grupo = models.ForeignKey(GrupoArticulo, on_delete=models.RESTRICT, db_column='grupo_id')
    linea = models.ForeignKey(LineaArticulo, on_delete=models.RESTRICT, db_column='linea_id')
    estado = models.IntegerField()
    stock = models.DecimalField(max_digits=12, decimal_places=2)
    imagen = models.CharField(max_length=255)

    class Meta:
        db_table = 'articulos'
        ordering = ['codigo_articulo']

class Pedido(models.Model):
    pedido_id = models.UUIDField(primary_key=True)
    nro_pedido = models.IntegerField()
    fecha_pedido = models.DateTimeField()
    cliente = models.ForeignKey(Cliente, on_delete=models.RESTRICT, db_column='cliente_id')
    importe = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.IntegerField()

    class Meta:
        db_table = 'pedidos'
        ordering = ['nro_pedido']

class ItemPedido(models.Model):
    item_id = models.UUIDField(primary_key=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, db_column='pedido_id', related_name='items')
    nro_item = models.IntegerField()
    articulo = models.ForeignKey(Articulo, on_delete=models.RESTRICT, db_column='articulo_id')
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    total_item = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.IntegerField()

    class Meta:
        db_table = 'items_pedido'
        ordering = ['nro_item']

class ListaPrecios(models.Model):
    articulo = models.OneToOneField(Articulo, on_delete=models.CASCADE, db_column='articulo_id', primary_key=True)
    precio_1 = models.DecimalField(max_digits=12, decimal_places=2)
    precio_2 = models.DecimalField(max_digits=12, decimal_places=2)
    precio_3 = models.DecimalField(max_digits=12, decimal_places=2)
    precio_4 = models.DecimalField(max_digits=12, decimal_places=2)
    precio_compra = models.DecimalField(max_digits=12, decimal_places=2)
    precio_costo = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = 'lista_precios'


##############################CARRITO DE COMPRA
class Vendedor(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=8, unique=True)
    def _str_(self):
        return f"{self.nombre} {self.apellido}"
    
class OrdenCompraCliente(models.Model):
    pedido_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nro_pedido = models.BigIntegerField(unique=True, null=False, auto_created=True)
    fecha_pedido = models.DateField(auto_now_add=True, null=False)
    cliente = models.ForeignKey('Cliente', on_delete=models.RESTRICT,null=False)
    vendedor = models.ForeignKey('Vendedor', on_delete=models.RESTRICT,null=False)
    importe = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.IntegerField(choices=EstadoOrden,default=EstadoOrden.PENDIENTE)
    notas = models.TextField(blank=True, null=True)
    creado_por = models.ForeignKey(Usuario, on_delete=models.RESTRICT, null=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=False)
    
    def actualizar_total(self):
        """Actualiza el total de la orden basado en los items"""
        total = sum(item.total_item for item in self.items_orden_compra.all())
        self.importe = total
        self.save()
    def _str_(self):
        return f"Orden #{self.nro_pedido} - {self.cliente}"
    class Meta:
        db_table = "ordenes_compra_cliente"
        ordering = ["-fecha_creacion"]


from django.db import models
import uuid

class ItemOrdenCompraCliente(models.Model):
    item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pedido = models.ForeignKey(OrdenCompraCliente, on_delete=models.CASCADE, null=False, related_name='items_orden_compra')
    nro_item = models.PositiveIntegerField(default=1, null=False)
    articulo = models.ForeignKey('Articulo', on_delete=models.RESTRICT, null=False, related_name='articulo_item_orden_compra')
    cantidad = models.PositiveIntegerField(null=False, default=1)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
    total_item = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
    estado = models.IntegerField(choices=EstadoEntidades, default=EstadoEntidades.ACTIVO)
    creado_por = models.ForeignKey(Usuario, on_delete=models.RESTRICT, null=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=False)

    def save(self, *args, **kwargs):
        # Calcular el total del ítem
        self.total_item = self.cantidad * self.precio_unitario

        if self.precio_unitario == 0:
            try:
                lista_precio = self.articulo.listaprecio
                self.precio_unitario = lista_precio.precio_1
                self.total_item = self.cantidad * self.precio_unitario
            except:
                pass

        super().save(*args, **kwargs)

        self.pedido.actualizar_total()

    def _str_(self):
        return f"{self.cantidad} x {self.articulo.descripcion}"

    class Meta:
        db_table = "items_ordenes_compra_cliente"