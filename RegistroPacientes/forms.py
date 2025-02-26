from django import forms
from RegistroPacientes.models import *
from django.contrib.auth.models import User
from django.utils.timezone import localdate
import datetime
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError


class PacienteForm(forms.ModelForm):
    cita = forms.ModelChoiceField(
        queryset=Cita.objects.filter(fecha__gte=localdate()).distinct(),  # Filtrar citas agendadas en el futuro
        label="Seleccione una cita agendada",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        to_field_name="id"  # El valor será el ID de la cita seleccionada
    )

    class Meta:
        model = Paciente
        fields = ['nombre', 'edad', 'direccion', 'telefono', 'email', 'diagnostico', 'receta', 'observaciones']

    def __init__(self, *args, **kwargs):
        paciente = kwargs.get('instance')
        super().__init__(*args, **kwargs)

        # Si ya se pasa una instancia de paciente (es decir, si estamos editando)
        if paciente:
            # Pre-fijamos los campos del paciente con los datos de la cita seleccionada
            self.fields['cita'].initial = paciente.citas.first()  # Seleccionar la primera cita asociada al paciente
            self.fields['nombre'].initial = paciente.nombre
            self.fields['edad'].initial = paciente.edad
            self.fields['direccion'].initial = paciente.direccion
            self.fields['telefono'].initial = paciente.telefono
            self.fields['email'].initial = paciente.email

        # Reordenar los campos para que 'cita' aparezca al principio
        self.fields = {'cita': self.fields['cita'], **self.fields}

    def clean_cita(self):
        cita = self.cleaned_data.get('cita')

        # Si la cita está asociada a un paciente existente, verificamos si hay un paciente ya registrado
        if cita:
            paciente_asociado = cita.paciente
            if paciente_asociado:
                self.instance = paciente_asociado  # Asignamos el paciente desde la cita
                # Marcar la cita como atendida
                cita.atendido = True  # Cambiar el estado de 'atendido' a True
                cita.save()

        return cita



        
class CitaForm(forms.Form):
    paciente = forms.CharField(label='Nombre del paciente', max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Ejemplo: Juan Pérez'}))
    fecha = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Fecha de la cita"
    )
    
    hora_cita = forms.ChoiceField(
        choices=[(f"{hora:02d}:00", f"{hora:02d}:00") for hora in range(8, 20)] + 
                [(f"{hora:02d}:30", f"{hora:02d}:30") for hora in range(8, 19)],
        label="Hora de la cita",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')

        if isinstance(fecha, datetime.datetime):
            fecha = fecha.date()

        fecha_actual = localdate()  # Obtiene la fecha actual considerando la zona horaria

        if fecha < fecha_actual:
            raise forms.ValidationError("No puedes seleccionar una fecha pasada.")

        if fecha.weekday() == 6:
            raise forms.ValidationError("Solo se permiten citas de lunes a sábado.")

        return fecha

    def clean_hora_cita(self):
        hora_cita = self.cleaned_data.get('hora_cita')
        fecha = self.cleaned_data.get('fecha')

        # Si la fecha seleccionada es hoy, verificamos la hora
        if fecha == localdate():
            hora_actual = datetime.datetime.now().strftime('%H:%M')  # Hora actual formateada como 'HH:MM'
            
            if hora_cita < hora_actual:
                raise forms.ValidationError("No puedes seleccionar una hora pasada para hoy.")
        
        return hora_cita
    


class Buscar_PacienteForm(forms.Form):
    nombre = forms.CharField(label='Nombre', max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Ejemplo: Juan Pérez'}))
    
    
####REGISTRO

class RegistroUsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    # Sobrescribimos el método save para hacer hash de la contraseña antes de guardar al usuario
    def save(self, commit=True):
        user = super().save(commit=False)  # Obtener el usuario sin guardar aún
        user.set_password(self.cleaned_data['password'])  # Hash de la contraseña
        if commit:
            user.save()  # Guardar el usuario con la contraseña hasheada
        return user
    

#########  EDITAR PERFIL

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['avatar','biografia','fecha_nacimiento','especialidad']
        widgets = {
            'fecha_nacimiento' : forms.DateInput(attrs={'type':'date'})
        }
        

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name','last_name','email']
        
        
class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Contraseña actual",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )