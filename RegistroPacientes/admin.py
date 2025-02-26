from django.contrib import admin
from .models import *

# Registrando los modelos en el admin
admin.site.register(Paciente)
admin.site.register(Cita)
admin.site.register(HistorialPaciente)
admin.site.register(Perfil)