from django.db import models
from django.contrib.auth.models import User

class Pyme(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nombre_negocio = models.CharField(max_length=150)
    rut = models.CharField(max_length=12, unique=True)
    comuna = models.CharField(max_length=100)
    rubro = models.CharField(max_length=100)
    telefono_whatsapp = models.CharField(max_length=20, blank=True, null=True)
    enlace_redes = models.URLField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)

    def __str__(self):
        return f"{self.nombre_negocio} ({self.comuna})"


class Diagnostico(models.Model):
    pyme = models.ForeignKey(Pyme, on_delete=models.CASCADE)
    puntaje_total = models.IntegerField(default=0)
    nivel_obtenido = models.CharField(max_length=50, default='Inicial')  # <-- Campo clave para el HTML
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Diagnóstico #{self.id} - {self.pyme.nombre_negocio} ({self.nivel_obtenido})"


class Pregunta(models.Model):
    enunciado = models.TextField()
    categoria = models.CharField(max_length=100)

    def __str__(self):
        return f"[{self.categoria}] {self.enunciado[:50]}..."


class RespuestaDiagnostico(models.Model):
    diagnostico = models.ForeignKey(Diagnostico, on_delete=models.CASCADE, related_name='respuestas')
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    puntaje_opcion = models.IntegerField()
    nivel_obtenido = models.CharField(max_length=50)

    def __str__(self):
        return f"Resp. Diag #{self.diagnostico.id} - P{self.pregunta.id}: {self.puntaje_opcion} pts"


class Producto(models.Model):
    pyme = models.ForeignKey(Pyme, on_delete=models.CASCADE, related_name='productos')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.IntegerField()
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.pyme})"


class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    
    TIPO_USUARIO = [
        ('cliente', 'Usuario / Cliente Regular'),
        ('pyme', 'Dueño de PyMe'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_USUARIO, default='cliente')

    def __str__(self):
        return f"{self.user.username} - {self.get_tipo_display()}"

class Opcion(models.Model):
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE, related_name='opciones')
    texto_opcion = models.CharField(max_length=255) # Ej: "Lo hacemos todo en un cuaderno"
    puntaje = models.IntegerField(default=1)         # El puntaje oculto (ej: 1, 3, 5)

    def __str__(self):
        return f"{self.texto_opcion} (Ptos: {self.puntaje})"

class Publicacion(models.Model):
    pyme = models.ForeignKey(Pyme, on_delete=models.CASCADE, related_name='publicaciones')
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='marketplace/', blank=True, null=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} - {self.pyme.nombre_negocio}"