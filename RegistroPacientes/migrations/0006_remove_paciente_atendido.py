# Generated by Django 5.1.1 on 2025-02-26 19:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('RegistroPacientes', '0005_alter_historialpaciente_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paciente',
            name='atendido',
        ),
    ]
