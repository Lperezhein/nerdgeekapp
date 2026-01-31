from django.db import models
from django.contrib.auth.models import User

class Producto(models.Model):
    TIPO_CHOICES = [
        ('sublimacion', 'Sublimación'),
        ('transfer', 'Transfer'),
        ('fotografia', 'Fotografía/Enmarcado'),
    ]
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=20, choices=TIPO_CHOICES)
    # La imagen de muestra del producto
    imagen_referencia = models.ImageField(upload_to='productos/')

    def __str__(self):
        return self.nombre

class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('diseno', 'En Diseño/Conversación'),
        ('impresion', 'En Impresión'),
        ('listo', 'Listo para Entrega'),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    # La foto que sube el cliente para estampar
    imagen_cliente = models.ImageField(upload_to='pedidos/%Y/%m/%d/')
    instrucciones = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username}"

class MensajeChat(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='mensajes')
    emisor = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"Mensaje de {self.emisor} en Pedido #{self.pedido.id}"

