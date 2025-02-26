from django.apps import AppConfig



class RegistroPacientesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'RegistroPacientes'

    def ready(self):
        import RegistroPacientes.signals  # Asegura que las señales se carguen