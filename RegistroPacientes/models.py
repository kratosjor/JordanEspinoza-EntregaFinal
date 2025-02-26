from django.db import models
from django.utils.timezone import localdate
from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.templatetags.static import static



class Paciente(models.Model):
    nombre = models.CharField(max_length=50)
    edad = models.IntegerField()
    direccion = models.CharField(max_length=100)
    telefono = models.CharField(max_length=10)
    email = models.EmailField(null=True, blank=True)
    
    
    # Campos de atención (diagnóstico, receta, observaciones)
    diagnostico = models.TextField()
    receta = models.TextField()
    observaciones = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(default=now)  # Registro de fecha
    
    def __str__(self):
        return self.nombre




class Cita(models.Model):
    HORAS_DISPONIBLES = [
        (f"{hora:02d}:00", f"{hora:02d}:00") for hora in range(8, 20)
    ] + [(f"{hora:02d}:30", f"{hora:02d}:30") for hora in range(8, 19)]

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="citas")
    fecha = models.DateField()
    hora_cita = models.CharField(max_length=5, choices=HORAS_DISPONIBLES)
    atendido = models.BooleanField(default=False)  # Nuevo campo para indicar si el paciente fue atendido

    def __str__(self):
        # Formato: Nombre del paciente - Fecha - Hora (Atendido o No Atendido)
        estado = "Atendido" if self.atendido else "No Atendido"
        return f"{self.paciente.nombre} - {self.fecha.strftime('%Y-%m-%d')} - {self.hora_cita} ({estado})"

    def clean(self):
        """
        Validación: No permitir fechas pasadas ni domingos.
        También verifica si ya existe una cita en la misma fecha y hora.
        """
        if self.fecha < localdate():
            raise ValidationError("No puedes agendar una cita en una fecha pasada.")

        if self.fecha.weekday() == 6:  # 6 es domingo
            raise ValidationError("No puedes agendar citas los domingos.")
        
        # Verificar si ya existe una cita para la misma fecha y hora
        if Cita.objects.filter(fecha=self.fecha, hora_cita=self.hora_cita).exists():
            raise ValidationError("Ya hay una cita agendada en esa fecha y hora.")

        super().clean()

class HistorialPaciente(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='historiales')
    diagnostico = models.TextField()
    receta = models.TextField()
    observaciones = models.TextField(null=True, blank=True)
    fecha_registro = models.DateTimeField(default=now)
    
    # Opcional: campo para marcar si la atención está completa
    atendido = models.BooleanField(default=True)

    def __str__(self):
        return f"Historial de {self.paciente.nombre} - {self.fecha_registro.strftime('%d/%m/%Y')}"
    
    class Meta:
        ordering = ['-fecha_registro']  # Ordenar por la fecha más reciente primero




##### CREAR Y EDITAR PERFIL


class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars', null=True, blank=True)
    biografia = models.TextField(max_length=500, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    especialidad = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return f"Perfil de {self.usuario.username}"
    
    @property
    def avatar_url(self):
        # Si no hay avatar, usar una imagen predeterminada en static
        if not self.avatar:
            return static('assets/img/default_avatar.png')
        return self.avatar.url
    
    