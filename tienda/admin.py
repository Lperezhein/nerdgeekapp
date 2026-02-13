from django.contrib import admin
from .models import Producto, Pedido, MensajeChat, Ejemplo

# 1. Registramos Pedido y MensajeChat de forma simple
admin.site.register(Pedido)
admin.site.register(MensajeChat)

# 2. Configuración para que las fotos de ejemplo aparezcan dentro del Producto
class EjemploInline(admin.StackedInline):
    model = Ejemplo
    extra = 3

# 3. Registro de Producto con sus Inlines
# USAMOS EL DECORADOR SOLO AQUÍ. No debe haber ningún 'admin.site.register(Producto)' arriba.
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    inlines = [EjemploInline]
    list_display = ('nombre', 'precio_base', 'categoria')

# 4. Registro de Ejemplo por separado (Opcional, pero útil)
@admin.register(Ejemplo)
class EjemploAdmin(admin.ModelAdmin):
    list_display = ('producto', 'imagen')
    list_filter = ('producto',)