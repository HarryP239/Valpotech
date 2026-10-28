from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('prisma.urls')),  # Esto conecta tu app 'prisma'
]

# CORREGIDO: sin esto los logos e imágenes subidas no se ven (error 404)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
