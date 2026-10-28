from django.urls import path
from . import views

urlpatterns = [
    path('', views.registrar_usuario, name='index'),
    path('pymes/', views.listar_pymes, name='listar_pymes'),
    path('estadisticas/', views.estadisticas_pymes, name='estadisticas_pymes'),
    path('pyme/<int:pyme_id>/diagnostico/', views.realizar_diagnostico, name='realizar_diagnostico'),
    path('registro/', views.registrar_usuario, name='registrar_usuario'),
    path('login/', views.iniciar_sesion, name='login'),
    path('crear-pyme/', views.crear_pyme, name='crear_pyme'), # <-- ¡Agrega esta línea!
    path('pyme/<int:pyme_id>/', views.detalle_pyme, name='detalle_pyme'),
    # CORREGIDO: detalle_pyme.html usa estas dos rutas y no existían (error NoReverseMatch)
    path('pyme/<int:pyme_id>/editar/', views.editar_pyme, name='editar_pyme'),
    path('pyme/<int:pyme_id>/publicar/', views.crear_publicacion, name='crear_publicacion'),
]
