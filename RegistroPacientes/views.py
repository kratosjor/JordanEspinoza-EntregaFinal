from django.shortcuts import render, redirect, get_object_or_404
from RegistroPacientes.forms import *
from RegistroPacientes.models import *
from django.views.generic.edit import UpdateView
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistroUsuarioForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import localdate
import datetime
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


###################

#HAY QUE REVISAR EL ASUNTO DE DUPLICIDAS DE HORAS

####################

def inicio(request):
    return render(request, 'RegistroPacientes/inicio.html')


def agendar_cita(request):
    if request.method == 'POST':
        formulario = CitaForm(request.POST)
        if formulario.is_valid():
            nombre_paciente = formulario.cleaned_data.get('paciente')
            fecha = formulario.cleaned_data.get('fecha')
            hora_cita = formulario.cleaned_data.get('hora_cita')

            # Verificar si el paciente ya fue atendido
            paciente = Paciente.objects.filter(nombre=nombre_paciente).first()
            if paciente:
                # Verificar si el paciente ya tiene una cita atendida
                if Cita.objects.filter(paciente=paciente, atendido=True).exists():
                    formulario.add_error('paciente', 'Este paciente ya fue atendido y no puede agendar una nueva cita.')
                    return render(request, 'RegistroPacientes/agendar_cita.html', {'formulario': formulario})

            # Verificar si ya existe una cita agendada en esa fecha y hora
            if Cita.objects.filter(fecha=fecha, hora_cita=hora_cita).exists():
                formulario.add_error('hora_cita', 'Ya existe una cita agendada para esta fecha y hora.')
                return render(request, 'RegistroPacientes/agendar_cita.html', {'formulario': formulario})

            # Crear o actualizar paciente
            if not paciente:
                paciente = Paciente.objects.create(
                    nombre=nombre_paciente,
                    edad=request.POST.get('edad', 30),
                    direccion=request.POST.get('direccion', 'Dirección no proporcionada'),
                    telefono=request.POST.get('telefono', '0000000000'),
                    email=request.POST.get('email', ''),
                )

            # Crear la cita
            cita = Cita.objects.create(
                paciente=paciente,
                fecha=fecha,
                hora_cita=hora_cita,
            )

            # Calcular el día de la semana basado en la fecha
            dia_cita = fecha.weekday() + 1
            cita.dia_cita = dia_cita
            cita.save()

            # Redirigir a la página de "reserva exitosa"
            return redirect('reserva_exitosa')

    else:
        formulario = CitaForm()

    return render(request, 'RegistroPacientes/agendar_cita.html', {'formulario': formulario})




def reserva_exitosa(request):
    cita = Cita.objects.latest('id')
    return render(request, 'RegistroPacientes/reserva_exitosa.html',{'cita':cita})
    
            

@login_required
def registro_paciente(request, paciente_id=None):
    paciente = None
    if paciente_id:
        paciente = Paciente.objects.get(id=paciente_id)

    if request.method == 'POST':
        formulario = PacienteForm(request.POST, instance=paciente)
        if formulario.is_valid():
            paciente = formulario.save()  # Guarda el paciente en la tabla Paciente

            # Si la cita está asociada a este paciente, actualiza el estado de 'atendido'
            cita = formulario.cleaned_data.get('cita')
            if cita:
                cita.atendido = True
                cita.save()

            # Crear un historial del paciente si es necesario
            if paciente_id:
                historial = HistorialPaciente.objects.create(
                    paciente=paciente,
                    diagnostico=request.POST.get('diagnostico', ''),
                    receta=request.POST.get('receta', ''),
                    observaciones=request.POST.get('observaciones', ''),
                )
            return redirect('listado_de_pacientes')

    else:
        formulario = PacienteForm(instance=paciente)

    return render(request, 'RegistroPacientes/registro_paciente.html', {'formulario': formulario})





@login_required
def listado_de_pacientes(request):
    pacientes = Paciente.objects.all()
    formulario = Buscar_PacienteForm(request.GET)
    
    if formulario.is_valid():
        nombre_a_buscar = formulario.cleaned_data.get('nombre')
        if nombre_a_buscar:
            pacientes = Paciente.objects.filter(nombre__icontains=nombre_a_buscar)
            
    return render(request, 'RegistroPacientes/listado_de_pacientes.html', {'pacientes': pacientes, "formulario":formulario})
           
    
####    CBV
class EditarPaciente(UpdateView):
    model = Paciente
    template_name = "RegistroPacientes/editar_paciente.html"
    fields = '__all__'
    success_url = reverse_lazy("listado_de_pacientes")
    


def buscar_paciente_por_nombre(request, nombre):
    paciente = get_object_or_404(Paciente, nombre=nombre)
    return redirect(reverse("editar_paciente", args=[paciente.pk]))



class EliminarPaciente(DeleteView):
    model = Paciente
    template_name = "RegistroPacientes/eliminar_paciente.html"
    success_url = reverse_lazy("listado_de_pacientes")
    
    
########### VISTA ACCESO APLICACION


def acceso(request):
    return render(request, "RegistroPacientes/acceso.html")


###REGISTRO

#login

def login_usuario(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)
            
            # Redirigir al URL original o al home si no existe el parámetro 'next'
            next_url = request.GET.get('next', 'inicio')  # 'home' es un nombre de URL predeterminado
            return redirect(next_url)
        else:
            # Si el formulario no es válido, mostramos un mensaje de error
            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = AuthenticationForm()

    # Si el formulario es un GET, solo renderizamos el formulario vacío
    return render(request, 'RegistroPacientes/login.html', {'form': form})





#Vista Registro
def registro_usuario(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('inicio')
    
    else:
        form = RegistroUsuarioForm()
        
    return render(request, "RegistroPacientes/registro_usuario.html", {'form':form})


#logout
def logout_usuario(request):
    logout(request)
    return redirect('acceso')



###### EDITAR PERFIL


@login_required
def perfil(request):
    perfil = Perfil.objects.get_or_create(usuario=request.user)[0]
    return render(request, 'RegistroPacientes/perfil.html',{'perfil':perfil})


@login_required
def editar_perfil(request):
    perfil = request.user.perfil  # Asegurar que obtenemos el perfil correcto

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        perfil_form = PerfilForm(request.POST, request.FILES, instance=perfil)
        password_form = CustomPasswordChangeForm(request.user, request.POST)  # Formulario de contraseña

        if user_form.is_valid() and perfil_form.is_valid():
            user_form.save()
            perfil_form.save()
            messages.success(request, "Perfil actualizado correctamente.")

        # Verificamos si el usuario quiere cambiar su contraseña
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Mantiene la sesión activa
            messages.success(request, "Tu contraseña ha sido cambiada correctamente.")
            return redirect('perfil')
        else:
            messages.error(request, "La contraseña actual es incorrecta.")

    else:
        user_form = UserForm(instance=request.user)
        perfil_form = PerfilForm(instance=perfil)
        password_form = CustomPasswordChangeForm(request.user)

    return render(request, 'RegistroPacientes/editar_perfil.html', {
        'user_form': user_form,
        'perfil_form': perfil_form,
        'password_form': password_form,
    })
    
    
def acerca_de(request):
    return render(request, 'RegistroPacientes/acerca_de.html')