# Help Desk System

Sistema de Soporte / Help Desk desarrollado como proyecto final para COMP 2053.

![Help Desk]

## 📋 Descripción

Aplicación web full stack para gestión de tickets de soporte técnico. Permite a los usuarios crear tickets, hacer seguimiento de solicitudes y comunicarse con el equipo de soporte.

## 🚀 Tecnologías Utilizadas

- **Backend**: Flask (Python)
- **Base de Datos**: MariaDB/MySQL
- **Frontend**: HTML, Bootstrap 5, jQuery
- **Iconos**: Bootstrap Icons
- **Seguridad**: Werkzeug (hash de contraseñas)

## ✨ Características

- ✅ Autenticación de usuarios (login/registro)
- ✅ Tres roles: Admin, Agent, User
- ✅ CRUD completo de tickets
- ✅ Sistema de comentarios
- ✅ Dashboard con estadísticas
- ✅ Filtros y búsqueda de tickets
- ✅ Diseño responsivo
- ✅ Interacciones AJAX con jQuery
- ✅ Administración de usuarios (solo Admin)

## 📦 Instalación Rápida

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/helpdesk-agosto-2025.git
cd helpdesk-agosto-2025/helpdesk_app
```

### 2. Crear entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos

Crear la base de datos en MariaDB/MySQL:

```sql
CREATE DATABASE helpdesk_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'helpdesk_user'@'localhost' IDENTIFIED BY 'helpdesk_password';
GRANT ALL PRIVILEGES ON helpdesk_db.* TO 'helpdesk_user'@'localhost';
```

Ejecutar el script SQL completo disponible en `docs/manual_tecnico.md`.

### 5. Configurar variables de entorno

Crear archivo `.env`:

```env
SECRET_KEY=tu_clave_secreta_aqui
DB_HOST=localhost
DB_USER=helpdesk_user
DB_PASSWORD=helpdesk_password
DB_NAME=helpdesk_db
```

### 6. Crear usuario administrador

```python
# Generar hash
from werkzeug.security import generate_password_hash
print(generate_password_hash("admin123"))
```

```sql
INSERT INTO users (name, email, password_hash, role)
VALUES ('Admin', 'admin@example.com', 'HASH_AQUI', 'ADMIN');
```

### 7. Ejecutar la aplicación

```bash
python app.py
```

Acceder a: `http://localhost:5000`

## 📱 Capturas de Pantalla

| Login | New User | Dashboard | 
|-------|----------|-----------|
| ![Login]<img width="1918" height="906" alt="login " src="https://github.com/user-attachments/assets/d515bd18-8d89-4ed3-a45b-ca82e5f6e3e4" />
| ![New User]<img width="1919" height="854" alt="new-user" src="https://github.com/user-attachments/assets/9beb50d0-299e-497f-bde9-111ddb70c5ca" />
| ![Dashboard](<img width="1916" height="912" alt="dashboard" src="https://github.com/user-attachments/assets/b270e7b9-cca2-4a7b-8e88-bef85e31aed1" />

| Tickets | Detalle |
|---------|---------|
| ![New Tickets](<img width="1916" height="911" alt="New-ticket" src="https://github.com/user-attachments/assets/91f9af8e-eade-41bd-9c94-2eaa897c5a3e" />
| ![Ticket Detail](<img width="1919" height="909" alt="ticket" src="https://github.com/user-attachments/assets/7bcda1ac-11f5-4ad8-921b-0d89fd82c2fb" />

## 🔐 Roles y Permisos

| Permiso | Admin | Agent | User |
|---------|-------|-------|------|
| Ver todos los tickets | ✅ | ❌ | ❌ |
| Crear tickets | ✅ | ✅ | ✅ |
| Actualizar tickets | ✅ | ✅ | ❌ |
| Gestionar usuarios | ✅ | ❌ | ❌ |

## 📁 Estructura del Proyecto

```
helpdesk_app/
├── app.py              # Aplicación Flask
├── config.py           # Configuración
├── requirements.txt    # Dependencias
├── .env                # Variables de entorno
├── templates/          # Plantillas HTML
├── static/             # CSS y JS
└── docs/               # Documentación
```

## 📖 Documentación

- [Manual de Usuario](docs/manual_usuario.md)
- [Manual Técnico](docs/manual_tecnico.md)

