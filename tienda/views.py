from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse
from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
import urllib.request
import urllib.parse

from .models import Producto, Pedido, MensajeChat
from .forms import PedidoForm, MensajeChatForm, RegistroUsuarioForm

def home(request):
    productos = Producto.objects.all()
    return render(request, 'tienda/home.html', {'productos': productos})

def nosotros(request):
    return render(request, 'tienda/nosotros.html')

# --- VISTA DE REGISTRO ---
def registro(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Desactivar cuenta hasta verificar
            user.save()
            
            # Lógica de envío de correo
            current_site = get_current_site(request)
            mail_subject = 'Activa tu cuenta en Nerdgeek'
            message = render_to_string('registration/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            try:
                email.send()
            except Exception as e:
                user.delete()  # Revertimos el registro si falla el correo
                return HttpResponse(f'<h3>Error al enviar el correo.</h3><p>No se pudo establecer conexión con el servidor de correo. Por favor verifica la configuración. <br>Error: {e}</p>')
            
            return HttpResponse('<h3>Registro casi completo.</h3><p>Por favor confirma tu correo electrónico para activar tu cuenta.</p>')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'registration/registro.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('home')
    else:
        return HttpResponse('El link de activación es inválido o ha expirado.')

# --- VISTA 1: CREAR EL PEDIDO (Checkout) ---
class CrearPedidoView(LoginRequiredMixin, CreateView):
    model = Pedido
    form_class = PedidoForm
    template_name = 'pedidos/crear_pedido.html'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # Obtenemos el producto desde la URL antes de procesar nada
        self.producto = get_object_or_404(Producto, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['producto'] = self.producto
        return context

    def form_valid(self, form):
        # Asignamos automáticamente el usuario y el producto
        form.instance.usuario = self.request.user
        form.instance.producto = self.producto
        form.instance.estado = 'pendiente' # Estado inicial
        return super().form_valid(form)

    def get_success_url(self):
        # ¡Aquí está la magia! Al terminar, llevamos al usuario directo al chat
        return reverse('detalle_pedido', args=[self.object.id])


# --- VISTA 2: LISTA DE PEDIDOS DEL USUARIO ---
class MisPedidosListView(LoginRequiredMixin, ListView):
    model = Pedido
    template_name = 'pedidos/mis_pedidos.html'
    context_object_name = 'pedidos'

    def get_queryset(self):
        # Solo mostramos los pedidos del usuario actual
        if self.request.user.is_superuser:
            return Pedido.objects.all().order_by('-fecha_creacion')
        return Pedido.objects.filter(usuario=self.request.user).order_by('-fecha_creacion')


# --- VISTA 3: DETALLE DEL PEDIDO + CHAT ---
class DetallePedidoView(LoginRequiredMixin, DetailView):
    model = Pedido
    template_name = 'pedidos/detalle_pedido.html'
    context_object_name = 'pedido'

    def get_queryset(self):
        # Seguridad: Que nadie vea pedidos ajenos
        if self.request.user.is_superuser:
            return Pedido.objects.all()
        return Pedido.objects.filter(usuario=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Cargamos el historial de mensajes
        context['mensajes'] = self.object.mensajes.all().order_by('timestamp')
        # Añadimos el formulario para enviar nuevos mensajes
        context['form_chat'] = MensajeChatForm()
        return context


# --- VISTA 4: PROCESAR MENSAJE (AJAX o POST normal) ---
def enviar_mensaje(request, pk):
    """
    Esta vista recibe el mensaje del formulario en el detalle del pedido.
    """
    if request.user.is_superuser:
        pedido = get_object_or_404(Pedido, pk=pk)
    else:
        pedido = get_object_or_404(Pedido, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        form = MensajeChatForm(request.POST)
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.pedido = pedido
            mensaje.emisor = request.user
            mensaje.save()
            
            # --- NOTIFICACIÓN WHATSAPP AL ADMIN ---
            # Si escribe el cliente (no es superuser), avisar al dueño de la tienda
            if not request.user.is_superuser:
                try:
                    # Configura aquí tus datos de CallMeBot (https://www.callmebot.com/)
                    telefono = "56990559234" # Ej: 5215555555555 (Tu número con código de país, sin el +)
                    apikey = "TU_API_KEY_RECIBIDA" # La clave que te dio el bot
                    texto = f"NerdGeek: Nuevo mensaje de {mensaje.emisor.username} en Pedido #{pedido.id}"
                    url = f"https://api.callmebot.com/whatsapp.php?phone={telefono}&text={urllib.parse.quote(texto)}&apikey={apikey}"
                    urllib.request.urlopen(url, timeout=5) # ¡Línea descomentada para que funcione!
                except Exception as e:
                    print(f"Error enviando notificación WhatsApp: {e}")
            
            # Si usamos AJAX (JavaScript) respondemos JSON para no recargar
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'ok',
                    'contenido': mensaje.contenido,
                    'emisor': mensaje.emisor.username,
                    'timestamp': mensaje.timestamp.strftime('%H:%M')
                })
            
            # Si no es AJAX, recargamos la página
            return redirect('detalle_pedido', pk=pk)
            
    return redirect('detalle_pedido', pk=pk)

def cambiar_estado_pedido(request, pk, nuevo_estado):
    """
    Permite al administrador cambiar el estado del pedido manualmente.
    """
    if not request.user.is_superuser:
        return redirect('home')
    
    pedido = get_object_or_404(Pedido, pk=pk)
    if nuevo_estado in dict(Pedido.ESTADO_CHOICES):
        pedido.estado = nuevo_estado
        pedido.save()
        
        # 1. Dejar registro automático en el chat (para que quede en el historial)
        MensajeChat.objects.create(
            pedido=pedido,
            emisor=request.user,
            contenido=f"*** ACTUALIZACIÓN DE SISTEMA: El pedido pasó a estado {pedido.get_estado_display().upper()} ***"
        )

        # 2. Enviar correo electrónico al cliente
        asunto = f"NerdGeek: Actualización de Pedido #{pedido.id}"
        mensaje = f"Hola {pedido.usuario.username},\n\nTu pedido ha cambiado de estado a: {pedido.get_estado_display()}.\n\nIngresa aquí para ver los detalles o chatear con nosotros:\n{request.build_absolute_uri(reverse('detalle_pedido', args=[pk]))}"
        
        try:
            email = EmailMessage(asunto, mensaje, to=[pedido.usuario.email])
            email.send()
        except Exception as e:
            print(f"Error enviando notificación de correo: {e}")
    
    return redirect('detalle_pedido', pk=pk)
