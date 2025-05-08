# Desarrollo de una API RESTful para un sistema de gestión de tareas

## Objetivo
En este taller aprenderás a desarrollar una API RESTful utilizando **FastAPI**, **SQLModel** y **Pydantic**. Implementaremos un sistema de gestión de tareas que permita crear, leer, actualizar y eliminar tareas, conectándonos a una base de datos PostgreSQL.

---

## Configuración Inicial del Proyecto

### Crear un Repositorio en GitHub
1. Accede a [GitHub](https://github.com/) y crea un nuevo repositorio para el proyecto.
2. Clona el repositorio en tu máquina local:
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   ```
3. Navega al directorio del proyecto:
   ```bash
   cd <NOMBRE_DEL_REPOSITORIO>
   ```

### Crear un Entorno Virtual
1. Crea un entorno virtual para el proyecto:
   ```bash
   python -m venv venv
   ```
2. Activa el entorno virtual:
   - En Windows:
     ```bash
     venv\Scripts\activate
     ```
   - En macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. Instala las dependencias necesarias:
   ```bash
   pip install fastapi uvicorn sqlmodel psycopg2
   ```

### Generar el Archivo `requirements.txt`
Exporta las dependencias instaladas a un archivo `requirements.txt`:
   ```bash
   pip freeze > requirements.txt
   ```
---

### Crear un Archivo `.gitignore`
Crea un archivo `.gitignore` en la raíz del proyecto. Agrega las siguientes líneas para ignorar archivos y carpetas innecesarios:
   ```
   # Entorno virtual
   venv/

   # Archivos de configuración
   .env

   # Archivos de caché de Python
   __pycache__/
   *.pyc
   *.pyo

   # Archivos de logs
   *.log

   # Archivos del sistema operativo
   .DS_Store
   Thumbs.db
   ```

---

## Estructura de Carpetas

```
app/
├── db/
│   ├── database.py       # Configuración de la base de datos y funciones auxiliares
├── models/
│   ├── user.py           # Modelo User con SQLModel
│   ├── todo_list.py      # Modelo TodoList con SQLModel
│   ├── task.py           # Modelo Task con SQLModel
│   ├── task_status.py    # Modelo TaskStatus con SQLModel
├── crud/
│   ├── user.py           # Operaciones CRUD para User
│   ├── todo_list.py      # Operaciones CRUD para TodoList
│   ├── task.py           # Operaciones CRUD para Task
│   ├── task_status.py    # Operaciones CRUD para TaskStatus
├── routes/
│   ├── user.py           # Endpoints relacionados con User
│   ├── todo_list.py      # Endpoints relacionados con TodoList
│   ├── task.py           # Endpoints relacionados con Task
│   ├── task_status.py    # Endpoints relacionados con TaskStatus
├── main.py               # Punto de entrada principal de la aplicación
├── seeder.py             # Script para poblar la base de datos con datos iniciales
├── .env                  # Variables de entorno
├── .env.example                  # Variables de entorno. Fichero de ejemplo
├── .gitignore                  # Declara los ficheros que no quiero que se suban a github
└── README.md             # Documentación del proyecto
```

---

## Modelo de Datos

### 1. `users`
- **Campos**:
  - `id`: int (PK)
  - `username`: str (único)
  - `email`: str (único)
  - `hashed_password`: str
  - `created_at`: datetime
- **Relación**: Un usuario puede tener muchas listas de tareas.

---

### 2. `todo_lists`
- **Campos**:
  - `id`: int (PK)
  - `title`: str
  - `description`: Optional[str]
  - `owner_id`: int (FK a `users.id`)
  - `created_at`: datetime
- **Relación**: Una lista pertenece a un usuario y puede tener muchas tareas.

---

### 3. `tasks`
- **Campos**:
  - `id`: int (PK)
  - `title`: str
  - `description`: Optional[str]
  - `due_date`: Optional[date]
  - `is_completed`: bool
  - `todo_list_id`: int (FK a `todo_lists.id`)
  - `status_id`: int (FK a `task_status.id`)
  - `created_at`: datetime
- **Relación**: Una tarea pertenece a una lista y tiene un estado.

---

### 4. `task_status`
- **Campos**:
  - `id`: int (PK)
  - `name`: str (`pendiente`, `en progreso`, `completada`, etc.)
  - `color`: Optional[str]
- **Relación**: Un estado puede aplicarse a muchas tareas.

---

## Agenda del Taller

### Configuración del Entorno
- Instalación de dependencias:
  ```bash
  pip install fastapi uvicorn sqlmodel psycopg2
  ```
- Crear la estructura de carpetas descrita anteriormente.

### Creación del Servidor Base con FastAPI
- Configuración inicial del servidor en `main.py`.
- Ejecutar el servidor con `uvicorn` y probar el endpoint base en [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

### Modelado y Persistencia de Datos
- Definición del Modelo de Datos con SQLModel:
  - Crear los archivos `models/user.py`, `models/todo_list.py`, `models/task.py` y `models/task_status.py` con los modelos correspondientes.
- Configuración de la Base de Datos PostgreSQL:
  - Configurar la conexión a PostgreSQL en `db/database.py` y crear la base de datos `task_manager`.
- Operaciones CRUD para las Entidades:
  - Crear los archivos `crud/user.py`, `crud/todo_list.py`, `crud/task.py` y `crud/task_status.py` con las funciones para crear, leer, actualizar y eliminar las entidades.

---

### Seeder para Poblar la Base de Datos

Implementar un seeder para inicializar la base de datos con datos de ejemplo. Esto es útil para pruebas y desarrollo.

Ejecutar el archivo `seeder.py` para poblar la base de datos:
```bash
python seeder.py
```

---

## Implementación de Endpoints

### **Usuarios (`/users`)**

#### **Obtener Usuario(s)**
- **Método HTTP**: `GET`
- **Endpoint**: `/users/`
- **Código de respuesta**: `200 OK`
- **Descripción**: Permite obtener usuarios utilizando parámetros de consulta (`query parameters`). Si no se proporciona ningún parámetro, devuelve todos los usuarios.
  - **Parámetros disponibles**:
    - `id`: Filtra por el ID del usuario.
    - `username`: Filtra por el nombre de usuario.
    - `email`: Filtra por el correo electrónico.
    - `skip`: Número de registros a omitir (paginación).
    - `limit`: Número máximo de registros a devolver (paginación).

- **Ejemplo de solicitud para obtener un usuario por ID**:
  ```http
  GET /users/?id=1
  ```
- **Ejemplo de solicitud para obtener un usuario por username**:
  ```http
  GET /users/?username=johndoe
  ```
- **Ejemplo de solicitud para obtener un usuario por email**:
  ```http
  GET /users/?email=johndoe@example.com
  ```
- **Ejemplo de solicitud para obtener todos los usuarios con paginación**:
  ```http
  GET /users/?skip=10&limit=5
  ```
- **Ejemplo de respuesta para un usuario específico**:
  ```json
  {
    "id": 1,
    "username": "johndoe",
    "email": "johndoe@example.com",
    "created_at": "2023-11-01T10:00:00"
  }
  ```
- **Ejemplo de respuesta para todos los usuarios**:
  ```json
  [
    {
      "id": 1,
      "username": "johndoe",
      "email": "johndoe@example.com",
      "created_at": "2023-11-01T10:00:00"
    },
    {
      "id": 2,
      "username": "janedoe",
      "email": "janedoe@example.com",
      "created_at": "2023-11-02T12:00:00"
    }
  ]
  ```

#### **Crear Usuario**
- **Método HTTP**: `POST`
- **Endpoint**: `/users/`
- **Código de respuesta**: `201 Created`
- **Descripción**: Crea un nuevo usuario en el sistema.
- **Ejemplo de solicitud**:
  ```json
  {
    "username": "johndoe",
    "email": "johndoe@example.com",
    "password": "securepassword"
  }
  ```
- **Ejemplo de respuesta**:
  ```json
  {
    "id": 1,
    "username": "johndoe",
    "email": "johndoe@example.com",
    "created_at": "2023-11-01T10:00:00"
  }
  ```

#### **Actualizar Usuario**
- **Método HTTP**: `PUT`
- **Endpoint**: `/users/{id}`
- **Código de respuesta**: `200 OK`
- **Descripción**: Actualiza los datos de un usuario existente.
- **Ejemplo de solicitud**:
  ```json
  {
    "username": "john_doe_updated",
    "email": "john_doe_updated@example.com"
  }
  ```
- **Ejemplo de respuesta**:
  ```json
  {
    "id": 1,
    "username": "john_doe_updated",
    "email": "john_doe_updated@example.com",
    "created_at": "2023-11-01T10:00:00"
  }
  ```

#### **Eliminar Usuario**
- **Método HTTP**: `DELETE`
- **Endpoint**: `/users/{id}`
- **Código de respuesta**: `204 No Content`
- **Descripción**: Elimina un usuario del sistema.
- **Ejemplo de respuesta**:
  ```json
  {
    "message": "User deleted successfully"
  }
  ```

---

### **Listas de Tareas (`/lists`)**

#### **Crear Lista**
- **Método HTTP**: `POST`
- **Endpoint**: `/lists/`
- **Código de respuesta**: `201 Created`
- **Descripción**: Crea una nueva lista de tareas asociada a un usuario.
- **Ejemplo de solicitud**:
  ```json
  {
    "title": "Trabajo",
    "description": "Tareas relacionadas con el trabajo",
    "owner_username": "johndoe"
  }
  ```
- **Ejemplo de respuesta**:
  ```json
  {
    "id": 1,
    "title": "Trabajo",
    "description": "Tareas relacionadas con el trabajo",
    "owner_username": "johndoe",
    "created_at": "2023-11-01T10:00:00"
  }
  ```

#### **Obtener Listas**
- **Método HTTP**: `GET`
- **Endpoint**: `/lists/`
- **Código de respuesta**: `200 OK`
- **Descripción**: Devuelve listas de tareas utilizando parámetros de consulta (`query parameters`). Si no se proporciona ningún parámetro, devuelve todas las listas.
  - **Parámetros disponibles**:
    - `id`: Filtra por el ID de la lista.
    - `owner_id`: Filtra por el ID del propietario.
    - `username`: Filtra por el nombre de usuario del propietario.
    - `email`: Filtra por el correo electrónico del propietario.
    - `skip`: Número de registros a omitir (paginación).
    - `limit`: Número máximo de registros a devolver (paginación).

- **Ejemplo de solicitud para obtener una lista por ID**:
  ```http
  GET /lists/?id=1
  ```
- **Ejemplo de solicitud para obtener listas por owner_id**:
  ```http
  GET /lists/?owner_id=1
  ```
- **Ejemplo de solicitud para obtener listas por username**:
  ```http
  GET /lists/?username=johndoe
  ```
- **Ejemplo de solicitud para obtener listas por email**:
  ```http
  GET /lists/?email=johndoe@example.com
  ```
- **Ejemplo de solicitud para obtener todas las listas con paginación**:
  ```http
  GET /lists/?skip=10&limit=5
  ```
- **Ejemplo de respuesta para una lista específica**:
  ```json
  {
    "id": 1,
    "title": "Trabajo",
    "description": "Tareas relacionadas con el trabajo",
    "owner_username": "johndoe",
    "created_at": "2023-11-01T10:00:00"
  }
  ```
- **Ejemplo de respuesta para todas las listas**:
  ```json
  [
    {
      "id": 1,
      "title": "Trabajo",
      "description": "Tareas relacionadas con el trabajo",
      "owner_username": "johndoe",
      "created_at": "2023-11-01T10:00:00"
    },
    {
      "id": 2,
      "title": "Personal",
      "description": "Tareas personales",
      "owner_username": "janedoe",
      "created_at": "2023-11-01T11:00:00"
    }
  ]
  ```

#### **Actualizar Lista**
- **Método HTTP**: `PUT`
- **Endpoint**: `/lists/{id}`
- **Código de respuesta**: `200 OK`
- **Ejemplo de solicitud**:
  ```json
  {
    "title": "Trabajo Actualizado",
    "description": "Tareas relacionadas con el trabajo actualizadas"
  }
  ```
- **Ejemplo de respuesta**:
  ```json
  {
    "id": 1,
    "title": "Trabajo Actualizado",
    "description": "Tareas relacionadas con el trabajo actualizadas",
    "owner_username": "janedoe",
    "created_at": "2023-11-01T10:00:00"
  }
  ```

#### **Eliminar Lista**
- **Método HTTP**: `DELETE`
- **Endpoint**: `/lists/{id}`
- **Código de respuesta**: `204 No Content`
- **Ejemplo de respuesta**:
  ```json
  {
    "message": "List deleted successfully"
  }
  ```

---

### **Tareas (`/tasks`)**

#### **Crear Tarea**
- **Método HTTP**: `POST`
- **Endpoint**: `/tasks/`
- **Código de respuesta**: `201 Created`
- **Ejemplo de solicitud**:
  ```json
  {
    "title": "Comprar leche",
    "description": "Ir al supermercado y comprar leche",
    "due_date": "2023-12-01",
    "is_completed": false,
    "todo_list_id": 1,
    "status_id": 1
  }
  ```
- **Ejemplo de respuesta**:
  ```json
  {
    "id": 1,
    "title": "Comprar leche",
    "description": "Ir al supermercado y comprar leche",
    "due_date": "2023-12-01",
    "is_completed": false,
    "todo_list_id": 1,
    "status_id": 1,
    "created_at": "2023-11-01T10:00:00"
  }
  ```

#### **Obtener Tareas**
- **Método HTTP**: `GET`
- **Endpoint**: `/tasks/`
- **Código de respuesta**: `200 OK`
- **Descripción**: Devuelve tareas utilizando parámetros de consulta (`query parameters`). Si no se proporciona ningún parámetro, devuelve todas las tareas.
  - **Parámetros disponibles**:
    - `todo_list_id`: Filtra las tareas pertenecientes a una lista específica.
    - `is_completed`: Filtra las tareas según su estado de finalización (`true` o `false`).
    - `skip`: Número de registros a omitir (paginación).
    - `limit`: Número máximo de registros a devolver (paginación).

- **Ejemplo de solicitud para obtener todas las tareas**:
  ```http
  GET /tasks/
  ```
- **Ejemplo de solicitud para obtener tareas de una lista específica**:
  ```http
  GET /tasks/?todo_list_id=1
  ```
- **Ejemplo de solicitud para obtener tareas completadas**:
  ```http
  GET /tasks/?is_completed=true
  ```
- **Ejemplo de solicitud para obtener tareas con paginación**:
  ```http
  GET /tasks/?skip=10&limit=5
  ```
- **Ejemplo de solicitud para obtener tareas con filtros combinados**:
  ```http
  GET /tasks/?todo_list_id=1&is_completed=true
  ```
- **Ejemplo de respuesta para todas las tareas**:
  ```json
  [
    {
      "id": 1,
      "title": "Comprar leche",
      "description": "Ir al supermercado y comprar leche",
      "due_date": "2023-12-01",
      "is_completed": false,
      "todo_list_id": 1,
      "status_id": 1,
      "created_at": "2023-11-01T10:00:00"
    },
    {
      "id": 2,
      "title": "Estudiar Python",
      "description": "Revisar documentación de FastAPI",
      "due_date": "2023-11-15",
      "is_completed": true,
      "todo_list_id": 2,
      "status_id": 3,
      "created_at": "2023-11-01T11:00:00"
    }
  ]
  ```

#### **Actualizar Tarea**
- **Método HTTP**: `PUT`
- **Endpoint**: `/tasks/{id}`
- **Código de respuesta**: `200 OK`
- **Descripción**: Permite actualizar los datos de una tarea, incluyendo su estado (`status_id`).
- **Ejemplo de solicitud**:
  ```json
  {
    "title": "Comprar leche y pan",
    "description": "Ir al supermercado y comprar leche y pan",
    "is_completed": true,
    "status_id": 2
  }
  ```
- **Ejemplo de respuesta**:
  ```json
  {
    "id": 1,
    "title": "Comprar leche y pan",
    "description": "Ir al supermercado y comprar leche y pan",
    "due_date": "2023-12-01",
    "is_completed": true,
    "todo_list_id": 1,
    "status_id": 2,
    "created_at": "2023-11-01T10:00:00"
  }
  ```

#### **Eliminar Tarea**
- **Método HTTP**: `DELETE`
- **Endpoint**: `/tasks/{id}`
- **Código de respuesta**: `204 No Content`
- **Ejemplo de respuesta**:
  ```json
  {
    "message": "Task deleted successfully"
  }
  ```

---

### **Estados de Tareas (`/status`)**

#### **Crear Estado**
- **Método HTTP**: `POST`
- **Endpoint**: `/status/`
- **Código de respuesta**: `201 Created`
- **Ejemplo de solicitud**:
  ```json
  {
    "name": "Pendiente",
    "color": "red"
  }
  ```
- **Ejemplo de respuesta**:
  ```json
  {
    "id": 1,
    "name": "Pendiente",
    "color": "red"
  }
  ```

#### **Obtener Estados**
- **Método HTTP**: `GET`
- **Endpoint**: `/status/`
- **Código de respuesta**: `200 OK`
- **Ejemplo de respuesta**:
  ```json
  [
    {
      "id": 1,
      "name": "Pendiente",
      "color": "red"
    },
    {
      "id": 2,
      "name": "En progreso",
      "color": "yellow"
    }
  ]
  ```

#### **Actualizar Estado**
- **Método HTTP**: `PUT`
- **Endpoint**: `/status/{id}`
- **Código de respuesta**: `200 OK`
- **Ejemplo de solicitud**:
  ```json
  {
    "name": "Completado",
    "color": "green"
  }
  ```
- **Ejemplo de respuesta**:
  ```json
  {
    "id": 1,
    "name": "Completado",
    "color": "green"
  }
  ```

#### **Eliminar Estado**
- **Método HTTP**: `DELETE`
- **Endpoint**: `/status/{id}`
- **Código de respuesta**: `204 No Content`
- **Ejemplo de respuesta**:
  ```json
  {
    "message": "Status deleted successfully"
  }
  ```

---

### Sistema de Logs
Implementar un sistema de logs para registrar eventos importantes en la aplicación, como solicitudes, errores y operaciones críticas. Esto ayuda a monitorear y depurar el sistema.

- **Requisitos**:
  - Configurar un archivo de logs para almacenar los registros.
  - Registrar eventos como:
    - Solicitudes entrantes.
    - Respuestas enviadas.
    - Errores y excepciones.
    - Operaciones CRUD realizadas.
    - **Registro de cada petición a la API en la terminal**: Mostrar información como método HTTP, endpoint, código de respuesta y tiempo de ejecución.

**Configuración de logs**:
- Configurar un archivo `logging.conf` o usar la biblioteca `logging` de Python para registrar eventos en un archivo o consola.
- Usar middleware de FastAPI para capturar y registrar cada solicitud automáticamente.

---

## Recursos Adicionales
- [Documentación oficial de FastAPI](https://fastapi.tiangolo.com/)
- [Documentación oficial de SQLModel](https://sqlmodel.tiangolo.com/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [PostgreSQL](https://www.postgresql.org/)
- [Logging en Python](https://docs.python.org/3/library/logging.html)

---

## Conclusión
Al finalizar este taller, habrás aprendido a:
1. Configurar un entorno de desarrollo para FastAPI.
2. Conectar una API RESTful a una base de datos PostgreSQL.
3. Modelar datos con SQLModel y Pydantic.
4. Implementar una API RESTful completa con operaciones CRUD.
5. Organizar un proyecto con una estructura de carpetas que siga buenas prácticas.
6. Relacionar entidades en una base de datos relacional.
7. Implementar un sistema de logs para monitorear y depurar la aplicación, incluyendo el registro de cada petición a la API en la terminal.
