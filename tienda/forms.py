from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Pedido, MensajeChat

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        # El usuario solo sube la imagen y las instrucciones
        fields = ['imagen_cliente', 'instrucciones']
        widgets = {
            'instrucciones': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Ej: Quiero que la foto quede centrada...'
            }),
            'imagen_cliente': forms.FileInput(attrs={'class': 'form-control'}),
        }

class MensajeChatForm(forms.ModelForm):
    class Meta:
        model = MensajeChat
        fields = ['contenido']
        widgets = {
            'contenido': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Escribe un mensaje...'
            }),
        }

class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(label="Correo Electrónico", required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)

    # Campo de verificación humana simple
    captcha = forms.IntegerField(
        label="Verificación humana: ¿Cuánto es 4 + 3?",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Escribe el resultado'})
    )

    def clean_captcha(self):
        respuesta = self.cleaned_data.get('captcha')
        if respuesta != 7:
            raise forms.ValidationError("Respuesta incorrecta. Por favor intenta de nuevo.")
        return respuesta

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email