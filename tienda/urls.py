from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Página Nosotros
    path('nosotros/', views.nosotros, name='nosotros'),

    # Registro de usuarios
    path('registro/', views.registro, name='registro'),

    # Activación de cuenta por email
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    # RUTAS PARA LOGIN Y LOGOUT (Añade estas si no están)
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

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

    path('galeria/<str:tipo_producto>/', views.galeria_ejemplos, name='galeria_ejemplos'),
]