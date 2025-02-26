from django.urls import path
from . import views
from .views import *

urlpatterns = [
    # Otras rutas
    path("", views.inicio, name="inicio"), 
    path("registro-paciente/", views.registro_paciente, name="registro_paciente"),
    path("listado-de-pacientes/", views.listado_de_pacientes, name="listado_de_pacientes"),
    path('eliminar-paciente/id/<int:pk>/', EliminarPaciente.as_view(), name='eliminar_paciente'),
    path('acceso/', views.acceso, name='acceso'),
    path('agendar_cita/', views.agendar_cita, name='agendar_cita'),
    path('reserva_exitosa/', views.reserva_exitosa, name='reserva_exitosa'),
    path('acerca_de/', views.acerca_de, name='acerca_de'),
    
    # Primero, busca por nombre y redirige a la edición con pk
    path("editar-paciente/<str:nombre>/", buscar_paciente_por_nombre, name="buscar_paciente"),
    
    # Luego, actualiza el paciente a través de pk
    path("editar-paciente/id/<int:pk>/", EditarPaciente.as_view(), name="editar_paciente"),
    
    ## URLs para el login, logout y registro bajo el prefijo 'accounts'
    #
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),
    path('registro_usuario/', views.registro_usuario, name='registro_usuario'),
    
    # EDITAR PERFIL
    path('perfil/', perfil, name='perfil'),
    path('perfil/editar/', editar_perfil, name='editar_perfil'),
    
    
]