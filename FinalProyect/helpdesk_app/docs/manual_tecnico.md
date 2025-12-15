# Manual Técnico - Sistema Help Desk

## Índice
1. [Descripción de la Arquitectura](#descripción-de-la-arquitectura)
2. [Modelo de Base de Datos](#modelo-de-base-de-datos)
3. [Instrucciones de Instalación](#instrucciones-de-instalación)
4. [Configuración](#configuración)
5. [Descripción de Rutas (Endpoints)](#descripción-de-rutas-endpoints)
6. [Seguridad](#seguridad)
7. [Mejoras Implementadas](#mejoras-implementadas)
8. [Tecnologías Utilizadas](#tecnologías-utilizadas)

---

## Descripción de la Arquitectura

El sistema Help Desk utiliza una arquitectura de tres capas:

```
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE PRESENTACIÓN                     │
│              (HTML + Bootstrap 5 + jQuery)                  │
│                                                             │
│  • Templates Jinja2                                         │
│  • Bootstrap 5.3 para diseño responsivo                     │
│  • jQuery 3.7 para interacciones AJAX                       │
│  • Bootstrap Icons para iconografía                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE APLICACIÓN                       │
│                    (Flask - Python)                         │
│                                                             │
│  • Rutas y controladores                                    │
│  • Autenticación y autorización                             │
│  • Lógica de negocio                                        │
│  • API endpoints (JSON)                                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE DATOS                            │
│                      (MariaDB)                              │
│                                                             │
│  • Tablas: users, tickets, ticket_comments                  │
│  • Conexiones via PyMySQL                                   │
│  • Consultas parametrizadas (prevención SQL Injection)      │
└─────────────────────────────────────────────────────────────┘
```

---

## Modelo de Base de Datos

### Diagrama Entidad-Relación

![ER Diagram](er_diagram.png)

### Tabla: users

| Campo         | Tipo         | Descripción                        |
|---------------|--------------|-------------------------------------|
| id            | INT (PK)     | Identificador único                 |
| name          | VARCHAR(100) | Nombre del usuario                  |
| email         | VARCHAR(150) | Email único del usuario             |
| password_hash | VARCHAR(255) | Contraseña hasheada (Werkzeug)      |
| role          | ENUM         | Rol: ADMIN, AGENT, USER             |
| created_at    | DATETIME     | Fecha de creación                   |

### Tabla: tickets

| Campo       | Tipo         | Descripción                         |
|-------------|--------------|--------------------------------------|
| id          | INT (PK)     | Identificador único                  |
| title       | VARCHAR(200) | Título del ticket                    |
| description | TEXT         | Descripción detallada                |
| status      | ENUM         | Estado: OPEN, IN_PROGRESS, RESOLVED  |
| priority    | ENUM         | Prioridad: LOW, MEDIUM, HIGH         |
| created_at  | DATETIME     | Fecha de creación                    |
| updated_at  | DATETIME     | Fecha de última actualización        |
| created_by  | INT (FK)     | Usuario que creó el ticket           |
| assigned_to | INT (FK)     | Agente asignado (nullable)           |

### Tabla: ticket_comments

| Campo      | Tipo     | Descripción                |
|------------|----------|----------------------------|
| id         | INT (PK) | Identificador único        |
| ticket_id  | INT (FK) | Ticket relacionado         |
| user_id    | INT (FK) | Usuario que comentó        |
| comment    | TEXT     | Contenido del comentario   |
| created_at | DATETIME | Fecha de creación          |

---

## Instrucciones de Instalación

### Requisitos Previos

- Python 3.8+
- MariaDB 10.x o MySQL 8.x
- Git
- Navegador web moderno

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/TU_USUARIO/helpdesk-agosto-2025.git
cd helpdesk-agosto-2025/helpdesk_app
```

### Paso 2: Crear Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Crear Base de Datos

Ejecutar en MariaDB/MySQL:

```sql
CREATE DATABASE helpdesk_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER 'helpdesk_user'@'localhost' IDENTIFIED BY 'helpdesk_password';
GRANT ALL PRIVILEGES ON helpdesk_db.* TO 'helpdesk_user'@'localhost';
FLUSH PRIVILEGES;

USE helpdesk_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('ADMIN', 'AGENT', 'USER') NOT NULL DEFAULT 'USER',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    status ENUM('OPEN', 'IN_PROGRESS', 'RESOLVED') NOT NULL DEFAULT 'OPEN',
    priority ENUM('LOW', 'MEDIUM', 'HIGH') NOT NULL DEFAULT 'MEDIUM',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT NOT NULL,
    assigned_to INT NULL,
    CONSTRAINT fk_tickets_created_by FOREIGN KEY (created_by) REFERENCES users(id),
    CONSTRAINT fk_tickets_assigned_to FOREIGN KEY (assigned_to) REFERENCES users(id)
);

CREATE TABLE ticket_comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL,
    user_id INT NOT NULL,
    comment TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_comments_ticket FOREIGN KEY (ticket_id) REFERENCES tickets(id),
    CONSTRAINT fk_comments_user FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Paso 5: Crear Usuario Administrador

Generar hash de contraseña:

```python
from werkzeug.security import generate_password_hash
print(generate_password_hash("admin123"))
```

Insertar admin en la base de datos:

```sql
INSERT INTO users (name, email, password_hash, role)
VALUES ('Admin', 'admin@example.com', 'HASH_GENERADO_AQUI', 'ADMIN');
```

### Paso 6: Configurar Variables de Entorno

Crear archivo `.env`:

```env
SECRET_KEY=tu_clave_secreta_larga_y_segura
DB_HOST=localhost
DB_USER=helpdesk_user
DB_PASSWORD=helpdesk_password
DB_NAME=helpdesk_db
```

### Paso 7: Ejecutar la Aplicación

```bash
python app.py
```

La aplicación estará disponible en: `http://localhost:5000`

---

## Configuración

### Archivo config.py

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-this")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "helpdesk_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "helpdesk_password")
    DB_NAME = os.getenv("DB_NAME", "helpdesk_db")
```

### Variables de Entorno (.env)

| Variable    | Descripción                        | Valor por defecto    |
|-------------|------------------------------------|-----------------------|
| SECRET_KEY  | Clave secreta para sesiones Flask  | dev-secret-key        |
| DB_HOST     | Host de la base de datos           | localhost             |
| DB_USER     | Usuario de la base de datos        | helpdesk_user         |
| DB_PASSWORD | Contraseña de la base de datos     | helpdesk_password     |
| DB_NAME     | Nombre de la base de datos         | helpdesk_db           |

---

## Descripción de Rutas (Endpoints)

### Rutas Públicas

| Método | Ruta       | Descripción           |
|--------|------------|-----------------------|
| GET    | /          | Redirección inicial   |
| GET    | /login     | Página de login       |
| POST   | /login     | Procesar login        |
| GET    | /register  | Página de registro    |
| POST   | /register  | Procesar registro     |

### Rutas Protegidas (requieren login)

| Método | Ruta                            | Descripción                  | Roles         |
|--------|---------------------------------|------------------------------|---------------|
| GET    | /dashboard                      | Panel principal              | Todos         |
| GET    | /logout                         | Cerrar sesión                | Todos         |
| GET    | /tickets                        | Lista de tickets             | Todos         |
| GET    | /tickets/new                    | Formulario nuevo ticket      | Todos         |
| POST   | /tickets/new                    | Crear ticket                 | Todos         |
| GET    | /tickets/<id>                   | Detalle del ticket           | Todos*        |
| POST   | /tickets/<id>/update            | Actualizar ticket            | ADMIN, AGENT  |
| POST   | /tickets/<id>/update-ajax       | Actualizar ticket (AJAX)     | ADMIN, AGENT  |
| POST   | /tickets/<id>/comments          | Agregar comentario           | Todos         |
| POST   | /tickets/<id>/comments-ajax     | Agregar comentario (AJAX)    | Todos         |
| GET    | /users                          | Lista de usuarios            | ADMIN         |
| POST   | /users/<id>/role                | Cambiar rol                  | ADMIN         |
| POST   | /users/<id>/delete              | Eliminar usuario             | ADMIN         |
| GET    | /api/stats                      | Estadísticas (JSON)          | Todos         |

*Los usuarios USER solo pueden ver sus propios tickets.

---

## Seguridad

### Medidas Implementadas

1. **Contraseñas Hasheadas**
   - Uso de `generate_password_hash()` y `check_password_hash()` de Werkzeug
   - Algoritmo: scrypt (por defecto en Werkzeug 3.x)

2. **Prevención de SQL Injection**
   - Consultas parametrizadas con `cursor.execute("... %s", (value,))`
   - Nunca se concatenan strings en queries SQL

3. **Control de Acceso por Rol**
   - Decorador `@login_required` para rutas protegidas
   - Decorador `@role_required("ADMIN", "AGENT")` para rutas específicas

4. **Sesiones Seguras**
   - `SECRET_KEY` robusta configurada en producción
   - No se almacena información sensible en la sesión

5. **Manejo de Errores**
   - Páginas de error personalizadas (404, 500)
   - `debug=False` recomendado en producción

---

## Mejoras Implementadas

### 1. Dashboard con Estadísticas

Se implementó un dashboard completo que muestra:
- Total de tickets y usuarios
- Tickets por estado (OPEN, IN_PROGRESS, RESOLVED)
- Tickets por prioridad (LOW, MEDIUM, HIGH)
- Lista de tickets recientes

**Consulta SQL utilizada:**
```sql
SELECT status, COUNT(*) as count 
FROM tickets 
GROUP BY status;
```

### 2. Filtros y Búsqueda de Tickets

- Búsqueda por título y descripción
- Filtros por estado y prioridad
- Paginación implícita en resultados

### 3. AJAX con jQuery

- Actualización de tickets sin recargar página
- Agregar comentarios dinámicamente
- Mensajes de feedback instantáneos

### 4. Diseño Responsivo

- Bootstrap 5.3 para diseño adaptable
- Mobile-first approach
- Iconografía con Bootstrap Icons

---

## Tecnologías Utilizadas

| Componente     | Tecnología      | Versión  |
|----------------|-----------------|----------|
| Backend        | Flask           | 3.x      |
| Base de Datos  | MariaDB/MySQL   | 10.x/8.x |
| Conector DB    | PyMySQL         | 1.x      |
| Frontend CSS   | Bootstrap       | 5.3.3    |
| Frontend JS    | jQuery          | 3.7.1    |
| Iconos         | Bootstrap Icons | 1.11.3   |
| Env Variables  | python-dotenv   | 1.x      |
| Security       | Werkzeug        | 3.x      |

---

## Repositorio GitHub

**URL del Proyecto**: https://github.com/TU_USUARIO/helpdesk-agosto-2025

---

## Estructura del Proyecto

```
helpdesk_app/
├── app.py              # Aplicación principal Flask
├── config.py           # Configuración
├── requirements.txt    # Dependencias Python
├── .env                # Variables de entorno
├── .env.example        # Plantilla de variables
├── templates/          # Plantillas HTML (Jinja2)
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── tickets_list.html
│   ├── ticket_new.html
│   ├── ticket_detail.html
│   ├── users_list.html
│   └── error.html
├── static/             # Archivos estáticos
│   ├── css/
│   │   └── custom.css
│   └── js/
│       └── main.js
└── docs/               # Documentación
    ├── manual_usuario.md
    ├── manual_tecnico.md
    ├── er_diagram.png
    └── screenshots/
        ├── login.png
        ├── dashboard.png
        ├── tickets_list.png
        ├── ticket_detail.png
        └── users_list.png
```

---

*Help Desk System - COMP 2053 Final Project - 2025*
