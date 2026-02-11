from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    # Página Nosotros
    path('nosotros/', views.nosotros, name='nosotros'),

    # Registro de usuarios
    path('registro/', views.registro, name='registro'),

    # Activación de cuenta por email
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    # Ruta para iniciar el pedido de un producto específico (ej: /producto/5/comprar/)
    path('producto/<int:pk>/comprar/', views.CrearPedidoView.as_view(), name='crear_pedido'),
    
    # Lista de pedidos
    path('mis-pedidos/', views.MisPedidosListView.as_view(), name='mis_pedidos'),
    
    # El detalle donde vive el chat
    path('pedido/<int:pk>/', views.DetallePedidoView.as_view(), name='detalle_pedido'),
    
    # Ruta oculta para procesar el envío de mensajes
    path('pedido/<int:pk>/enviar/', views.enviar_mensaje, name='enviar_mensaje'),

    # Ruta para cambiar el estado (Solo Admin)
    path('pedido/<int:pk>/cambiar-estado/<str:nuevo_estado>/', views.cambiar_estado_pedido, name='cambiar_estado'),
]