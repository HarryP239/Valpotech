# Valpotech - Proyecto IWG400 (Grupo 13)
Sistema web desarrollado para potenciar la transformación digital de PyMEs en la Región de Valparaíso, integrando autodiagnóstico digital, directorio comercial y panel de métricas territoriales.

# Requisitos del Sistema
* Python: Versión 3.x compatible.
* Django: Versión 5.2.8 (Django>=5.2.8,<6.0).

# Instalación y Configuración Local
1. Clonar el repositorio:
git clone https://github.com/HarryP239/Valpotech
cd Valpotech

3. Instalar dependencias del proyecto:
pip install -r requirements.txt

5. Aplicar migraciones de la base de datos:
python manage.py migrate

# Ejecución de la Aplicación
Para levantar el servidor de desarrollo local en Django, ejecuta:
python manage.py runserver

Una vez desplegado el servidor, abre tu navegador e ingresa al link que sale al ejecutar runserver:

# Datos para Pruebas
El proyecto ya incluye la base de datos preconfigurada (db.sqlite3) con registros y tablas listos para probar la funcionalidad corazón (autodiagnóstico digital y directorio de PyMEs) de forma inmediata tras iniciar el servidor.
