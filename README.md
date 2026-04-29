# PonteGlam Backend

Sistema de gestión de servicios de belleza y agendamiento de citas. Desarrollado con Django REST Framework, PostgreSQL y Firebase.

## Requisitos

- Python >= 3.11
- PostgreSQL >= 16
- Redis (para tareas asíncronas con Celery)

## Instalación

1. **Clonar el repositorio**:
    ```bash
    git clone [url_del_repositorio]
    cd ponteglam_backend
    ```

2. **Crear y activar entorno virtual**:
    ```bash
    python -m venv env
    source env/bin/activate  # macOS/Linux
    .\env\Scripts\activate   # Windows
    ```

3. **Instalar dependencias**:
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

4. **Configuración de Variables de Entorno**:
    Crea un archivo `.env` en la raíz del proyecto basándote en `.env.example`. Asegúrate de configurar:
    - Datos de conexión a PostgreSQL (`POSTGRES_DB`, `POSTGRES_USER`, etc.)
    - Configuración de Redis (`REDIS_URL`)
    - Credenciales de Email (opcional)

5. **Configuración de Firebase (Google Sign-In)**:
    El proyecto requiere una llave de cuenta de servicio de Firebase para la autenticación y notificaciones.
    - Ve a la [Consola de Firebase](https://console.firebase.google.com/).
    - Selecciona tu proyecto -> Configuración del proyecto -> Cuentas de servicio.
    - Haz clic en **Generar nueva clave privada**.
    - Descarga el archivo JSON y guárdalo en la raíz del proyecto con el nombre:
      `ponteglam-8741d-firebase-adminsdk-twbfr-ee152a3d39.json`

6. **Migraciones y Base de Datos**:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

7. **Carga de Configuración Inicial**:
    Este comando limpia los datos actuales y carga la configuración por defecto (categorías, servicios, sedes):
    ```bash
    python manage.py shell < core/scripts/create_default_settings.py
    ```

## Ejecución

### 1. Servidor de Desarrollo
```bash
python manage.py runserver
```

### 2. Celery (Tareas Asíncronas)
En una terminal aparte (con el entorno activado):
```bash
celery -A ponteglam worker --loglevel=info
```

## Mantenimiento y Reset de Base de Datos

Si necesitas resetear la base de datos por completo:

1. **Borrar y recrear BD**:
    ```bash
    sudo su postgres
    psql
    DROP DATABASE dbproyecto;
    CREATE DATABASE dbproyecto;
    \q
    ```

2. **Limpiar archivos de migración**:
    ```bash
    find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
    find . -path "*/migrations/*.pyc" -delete
    ```

3. **Generar de nuevo y cargar datos**:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    python manage.py shell < core/scripts/create_default_settings.py
    ```

## Licencia

Este proyecto está bajo la licencia [MIT](https://opensource.org/licenses/MIT).
