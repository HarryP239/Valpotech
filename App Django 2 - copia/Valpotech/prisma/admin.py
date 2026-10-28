from django.contrib import admin
from .models import Pyme, Diagnostico, Pregunta, RespuestaDiagnostico, Opcion, Perfil, Publicacion, Producto

# Registramos nuestros modelos para que aparezcan en el panel de administración
admin.site.register(Pyme)
admin.site.register(Diagnostico)
admin.site.register(Pregunta)
admin.site.register(RespuestaDiagnostico)
# CORREGIDO: faltaban estos modelos (sin Opcion no se pueden editar las respuestas del cuestionario)
admin.site.register(Opcion)
admin.site.register(Perfil)
admin.site.register(Publicacion)
admin.site.register(Producto)
