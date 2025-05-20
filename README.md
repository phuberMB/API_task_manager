# API Task Manager

## Descripción

API RESTful para la gestión de tareas, listas y usuarios, con autenticación JWT, control de roles, recuperación de contraseña y revocación de tokens con Redis.

---

## Características principales

- **Autenticación JWT** con expiración configurable por rol.
- **Gestión de roles**: `admin`, `user`, `viewer`.
- **Protección de endpoints** según permisos.
- **CRUD** para usuarios, listas, tareas y estados.
- **Recuperación y restablecimiento de contraseña** con token temporal.
- **Revocación de tokens** (logout) usando Redis.
- **Logs** y buenas prácticas de seguridad.
- **Dockerización** y orquestación con Docker Compose.
- **Base de datos PostgreSQL** y **Redis** para revocación eficiente de tokens.

---

## Instalación

1. Clona el repositorio y entra en la carpeta del proyecto.
2. Crea y activa un entorno virtual (opcional para desarrollo local):
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Crea un archivo `.env` en la raíz con:
   ```
   SECRET_KEY=tu_clave_secreta
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/task_manager
   REDIS_URL=redis://localhost:6379/0
   ```

---

## Ejecución local

```bash
uvicorn main:app --reload
```

Accede a la documentación interactiva en [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Despliegue con Docker

1. **Construye y levanta los servicios (API, PostgreSQL y Redis):**

   ```bash
   docker-compose up --build
   ```

2. La API estará disponible en [http://localhost:8000/docs](http://localhost:8000/docs)

3. Para poblar la base de datos con datos de ejemplo, ejecuta el seeder:
   ```bash
   docker-compose exec api python seeder.py
   ```

---

## Endpoints principales

### Autenticación

- **POST** `/api/auth/register`  
  Registra un usuario (`username`, `email`, `password`, `role` opcional: `user` o `viewer`).

- **POST** `/api/auth/login`  
  Login y obtención de tokens (`username`, `password`).  
  Expiración:  
    - admin: 60 min  
    - user: 30 min  
    - viewer: 15 min

- **POST** `/api/auth/refresh`  
  Renueva el access token usando un refresh token.

- **POST** `/api/auth/logout`  
  Revoca el token de acceso (almacenado en Redis hasta su expiración).

- **POST** `/api/auth/forgot-password`  
  Solicita recuperación de contraseña (envía token temporal).

- **POST** `/api/auth/reset-password`  
  Restablece la contraseña usando el token recibido.

---

### Usuarios (`/users`)

- **admin**: CRUD completo sobre cualquier usuario.
- **user/viewer**: CRUD solo sobre su propio usuario.

---

### Listas de tareas (`/lists`)

- **admin**: CRUD completo sobre cualquier lista.
- **user**: CRUD sobre sus propias listas.
- **viewer**: solo GET de cualquier lista.

---

### Tareas (`/tasks`)

- **admin**: CRUD completo sobre cualquier tarea.
- **user**: CRUD sobre tareas de sus listas.
- **viewer**: solo GET de cualquier tarea.

---

### Estados de tareas (`/status`)

- **admin**: CRUD completo.
- **user**: solo GET.
- **viewer**: sin acceso.

---

## Seguridad

- **Clave secreta** protegida en `.env`.
- **Expiración de tokens** según rol.
- **Revocación de tokens** eficiente usando Redis.
- **Validación de roles** en cada endpoint.
- **Recomendado**: usar HTTPS en producción.

---

## Pruebas rápidas

Puedes probar los endpoints con `curl`, `httpie` o desde `/docs`.

Ejemplo registro:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register -H "Content-Type: application/json" -d "{\"username\":\"testuser\",\"email\":\"testuser@example.com\",\"password\":\"testpass\",\"role\":\"user\"}"
```

---

## Licencia

MIT