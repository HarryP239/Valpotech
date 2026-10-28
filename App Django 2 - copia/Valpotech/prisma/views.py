from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'prisma/index.html')

from django.shortcuts import render, redirect, get_object_or_404
from .models import Pyme, Pregunta, Opcion, Diagnostico, Publicacion # CORREGIDO: faltaba importar Publicacion

# CORREGIDO: aquí había una primera versión duplicada de realizar_diagnostico.
# Python solo usaba la segunda, así que se dejó una sola (más abajo), ya corregida.


def resultado_diagnostico(request, diagnostico_id):
    # Vista simple para mostrar los resultados al usuario
    diagnostico = get_object_or_404(Diagnostico, id=diagnostico_id)
    respuestas = diagnostico.respuestas.all() # Usamos el related_name que definimos en models.py
    
    context = {
        'diagnostico': diagnostico,
        'respuestas': respuestas
    }
    return render(request, 'prisma/resultado_diagnostico.html', context)

    from django.shortcuts import render
from .models import Pyme

def listar_pymes(request):
    # Obtenemos todos los objetos Pyme por defecto
    pymes = Pyme.objects.all()

    # Capturamos los parámetros enviados por método GET desde el formulario
    comuna_seleccionada = request.GET.get('comuna', '')
    rubro_seleccionado = request.GET.get('rubro', '')

    # Aplicamos filtros con el ORM de Django si el usuario seleccionó un valor
    if comuna_seleccionada:
        pymes = pymes.filter(comuna__icontains=comuna_seleccionada)
    
    if rubro_seleccionado:
        pymes = pymes.filter(rubro__icontains=rubro_seleccionado)

    # Obtenemos listas de opciones únicas para llenar los selectores del HTML dinámicamente
    comunas_disponibles = Pyme.objects.values_list('comuna', flat=True).distinct().order_by('comuna')
    rubros_disponibles = Pyme.objects.values_list('rubro', flat=True).distinct().order_by('rubro')

    context = {
        'pymes': pymes,
        'comunas_disponibles': comunas_disponibles,
        'rubros_disponibles': rubros_disponibles,
        'comuna_seleccionada': comuna_seleccionada,
        'rubro_seleccionado': rubro_seleccionado,
    }
    
    return render(request, 'prisma/listar_pymes.html', context)

from django.shortcuts import render
from django.db.models import Avg, Count
from .models import Pyme, Diagnostico

def estadisticas_pymes(request):
    # CORREGIDO: antes mostraba estadisticas.html, que es la pantalla del RESULTADO del
    # diagnóstico (salía vacía). Las métricas regionales están en dashboard.html,
    # así que se usa esa plantilla con los datos que necesita.
    por_comuna = Diagnostico.objects.values('pyme__comuna').annotate(
        promedio_puntaje=Avg('puntaje_total'),
        total=Count('id'),
    ).order_by('pyme__comuna')

    niveles = Diagnostico.objects.values('nivel_obtenido').annotate(
        total=Count('id')
    ).order_by('nivel_obtenido')

    context = {
        'total_pymes': Pyme.objects.count(),
        'total_diagnosticos': Diagnostico.objects.count(),
        'por_comuna': por_comuna,
        'niveles': niveles,
    }

    return render(request, 'prisma/dashboard.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from .models import Pyme, Pregunta, Diagnostico

def realizar_diagnostico(request, pyme_id):
    pyme = get_object_or_404(Pyme, id=pyme_id)
    preguntas = Pregunta.objects.all()

    if request.method == 'POST':
        puntaje_total = 0

        # El formulario envía el ID de la opción elegida; se suma el puntaje real
        # de esa opción (5, 3 o 1), no el ID.
        for pregunta in preguntas:
            opcion_id = request.POST.get(f'pregunta_{pregunta.id}')
            if opcion_id:
                try:
                    opcion = Opcion.objects.get(id=opcion_id, pregunta=pregunta)
                    puntaje_total += opcion.puntaje
                except (Opcion.DoesNotExist, ValueError):
                    pass

        if puntaje_total <= 23:
            nivel = 'Inicial'
        elif puntaje_total <= 37:
            nivel = 'Intermedio'
        else:
            nivel = 'Avanzado'

        # CORREGIDO: antes usaba get_or_create, que se caía si la PyMe tenía más de un
        # diagnóstico, y guardaba en campos que no existen (puntaje / nivel), por lo que
        # el diagnóstico quedaba siempre en 0 puntos.
        # Ahora cada PyMe guarda un solo diagnóstico: se borra el anterior y se guarda el nuevo
        # en los campos reales del modelo (puntaje_total / nivel_obtenido).
        Diagnostico.objects.filter(pyme=pyme).delete()
        Diagnostico.objects.create(
            pyme=pyme,
            puntaje_total=puntaje_total,
            nivel_obtenido=nivel,
        )

        return render(request, 'prisma/estadisticas.html', {
            'pyme': pyme,
            'puntaje_total': puntaje_total,
            'nivel': nivel
        })

    return render(request, 'prisma/realizar_diagnostico.html', {
        'pyme': pyme, 
        'preguntas': preguntas
    })


from django.shortcuts import render, redirect, get_object_or_404
from .models import Pyme
from .forms import ProductoForm

def agregar_producto(request, pyme_id):
    pyme = get_object_or_404(Pyme, id=pyme_id)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.pyme = pyme  # Asociamos el producto a esta PyMe
            producto.save()
            return redirect('detalle_pyme', pyme_id=pyme.id) # O a la vista principal
    else:
        form = ProductoForm()

    context = {
        'pyme': pyme,
        'form': form,
    }
    return render(request, 'prisma/agregar_producto.html', context)

from django.contrib.auth.models import User
from django.contrib.auth import login
from .models import Perfil

def registrar_usuario(request):
    if request.method == 'POST':
        nombre_usuario = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        tipo_rol = request.POST.get('tipo_rol') # 'cliente' o 'pyme'

        if not User.objects.filter(username=nombre_usuario).exists():
            user = User.objects.create_user(username=nombre_usuario, email=email, password=password)
            Perfil.objects.create(user=user, tipo=tipo_rol)
            login(request, user)

            # 👇 AQUÍ ESTÁ EL CAMBIO CLAVE 👇
            if tipo_rol == 'pyme':
                return redirect('crear_pyme')  # Si es PyMe, va a crear su negocio
            else:
                return redirect('listar_pymes')  # Si es cliente normal, va al directorio
                
        else:
            error = "El nombre de usuario ya está en uso."
            return render(request, 'prisma/registro.html', {'error': error})

    return render(request, 'prisma/registro.html')

from .forms import PymeForm
from .models import Pyme
from django.contrib.auth.decorators import login_required

from .forms import PymeForm
from .models import Pyme
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Pyme

@login_required
def crear_pyme(request):
    # Verificamos si el usuario ya tiene una PyMe creada
    pyme_existente = Pyme.objects.filter(usuario=request.user).first()
    if pyme_existente:
        # Si ya tiene una, lo mandamos directo a su detalle/perfil en lugar de crear otra
        return redirect('detalle_pyme', pyme_id=pyme_existente.id)

    if request.method == 'POST':
        nombre_negocio = request.POST.get('nombre_negocio')
        rut = request.POST.get('rut')
        comuna = request.POST.get('comuna')
        rubro = request.POST.get('rubro')
        descripcion = request.POST.get('descripcion')
        logo = request.FILES.get('logo')

        # CORREGIDO: si el RUT ya existe la página se caía con IntegrityError
        if Pyme.objects.filter(rut=rut).exists():
            return render(request, 'prisma/crear_pyme.html', {
                'error': 'Ya existe una PyMe registrada con ese RUT.'
            })

        # Creamos la PyMe asociada al usuario actual
        pyme = Pyme.objects.create(
            usuario=request.user,
            nombre_negocio=nombre_negocio,
            rut=rut,
            comuna=comuna,
            rubro=rubro,
            descripcion=descripcion,
            logo=logo
        )
        # CORREGIDO: después de registrar la PyMe se va directo al diagnóstico
        # (antes iba al directorio y no había forma de llegar al cuestionario)
        return redirect('realizar_diagnostico', pyme_id=pyme.id)

    return render(request, 'prisma/crear_pyme.html')

from django.contrib.auth import authenticate

def iniciar_sesion(request):
    if request.method == 'POST':
        nombre_usuario = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=nombre_usuario, password=password)
        
        if user is not None:
            login(request, user)
            
            # Verificamos si es una PyMe
            if hasattr(user, 'perfil') and user.perfil.tipo == 'pyme':
                # Buscamos si ya tiene su PyMe creada
                pyme = Pyme.objects.filter(usuario=user).first()
                if not pyme:
                    return redirect('crear_pyme') # Si no la tiene, va al formulario de su negocio
                else:
                    # Si ya tiene su PyMe, revisamos si ya hizo su diagnóstico
                    diagnostico = Diagnostico.objects.filter(pyme=pyme).first()
                    if not diagnostico:
                        return redirect('realizar_diagnostico', pyme_id=pyme.id) # Va al cuestionario
                    else:
                        return redirect('listar_pymes') # Si ya hizo todo, va al directorio general
            else:
                # Si es un cliente regular, va directo al directorio
                return redirect('listar_pymes')
        else:
            error = "Nombre de usuario o contraseña incorrectos."
            return render(request, 'prisma/login.html', {'error': error})

    return render(request, 'prisma/login.html')

from django.shortcuts import render, redirect, get_object_or_404
from .models import Pyme

def editar_pyme(request, pyme_id):
    pyme = get_object_or_404(Pyme, id=pyme_id)
    if request.method == 'POST':
        # CORREGIDO: si el RUT nuevo ya pertenece a otra PyMe la página se caía con IntegrityError
        nuevo_rut = request.POST.get('rut', pyme.rut)
        if Pyme.objects.filter(rut=nuevo_rut).exclude(id=pyme.id).exists():
            return render(request, 'prisma/editar_pyme.html', {
                'pyme': pyme,
                'error': 'Ese RUT ya pertenece a otra PyMe.'
            })

        pyme.nombre_negocio = request.POST.get('nombre_negocio', pyme.nombre_negocio)
        pyme.rut = nuevo_rut # <-- Guardamos el RUT actualizado
        pyme.descripcion = request.POST.get('descripcion', pyme.descripcion)
        if 'logo' in request.FILES:
            pyme.logo = request.FILES['logo']
        pyme.save()
        return redirect('detalle_pyme', pyme_id=pyme.id)
        
    return render(request, 'prisma/editar_pyme.html', {'pyme': pyme})

from django.shortcuts import render, get_object_or_404
from .models import Pyme, Diagnostico

def detalle_pyme(request, pyme_id):
    pyme = get_object_or_404(Pyme, id=pyme_id)
    # CORREGIDO: se toma el diagnóstico más reciente (antes tomaba el más antiguo)
    diagnostico = Diagnostico.objects.filter(pyme=pyme).order_by('-id').first()
    # CORREGIDO: la plantilla muestra 'publicaciones' pero la vista nunca las enviaba
    publicaciones = pyme.publicaciones.all().order_by('-fecha_publicacion')

    return render(request, 'prisma/detalle_pyme.html', {
        'pyme': pyme,
        'diagnostico': diagnostico,
        'publicaciones': publicaciones,
    })

@login_required
def crear_publicacion(request, pyme_id):
    pyme = get_object_or_404(Pyme, id=pyme_id)
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        imagen = request.FILES.get('imagen')
        
        # Guarda la publicación asociada a esta PyMe
        Publicacion.objects.create(
            pyme=pyme,
            titulo=titulo,
            descripcion=descripcion,
            precio=precio,
            imagen=imagen
        )
        return redirect('detalle_pyme', pyme_id=pyme.id)
        
    return render(request, 'prisma/crear_publicacion.html', {'pyme': pyme})