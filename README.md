# 🚀 INFORME TÉCNICO – DESARROLLO, CONTENERIZACIÓN Y DESPLIEGUE DE API EN LA NUBE

## 📖 1. RESUMEN EJECUTIVO
El presente informe describe el diseño, desarrollo, contenerización y despliegue de una API funcional en entorno local y con opción de despliegue en nube, aplicando buenas prácticas de ingeniería de software, control de versiones, pruebas y despliegue continuo.

Se emplearon herramientas clave del ecosistema moderno como GitHub para versionamiento, Docker para contenerización, curl para pruebas de endpoints y despliegue en infraestructura local/cloud (opcional). El proyecto demuestra la implementación de un servicio API robusto, accesible y validado mediante pruebas funcionales, estructurado bajo principios de desarrollo seguro y escalable.

---

## 🌟 2. INTRODUCCIÓN
En la actualidad de la transformación digital, el desarrollo de APIs seguras y escalables constituye un componente crítico en arquitecturas modernas. Este proyecto integra conocimientos de desarrollo backend, DevOps y ciberseguridad mediante la implementación de un servicio API desplegable en la nube.

Se enfatiza el uso de buenas prácticas en:
- Control de versiones
- Contenerización
- Automatización de despliegue
- Validación de servicios
- Seguridad básica en APIs

---

## 🎯 3. OBJETIVOS

### 3.1 Objetivo General
Diseñar, construir, contenerizar y desplegar una API funcional en la nube, aplicando buenas prácticas de desarrollo, pruebas y despliegue seguro.

### 3.2 Objetivos Específicos
- Implementar una API utilizando un framework moderno de Python.
- Gestionar el código mediante control de versiones distribuido con Visual Studio Code y GitHub.
- Contenerizar la aplicación utilizando Docker.
- Validar el funcionamiento mediante pruebas con curl.
- Desplegar el servicio en una plataforma local/cloud (opcional).
- Documentar el proceso y evidenciar su correcto funcionamiento.

---

## 🏗️ 4. ARQUITECTURA DEL SISTEMA
El sistema está compuesto por los siguientes elementos:
- **Backend API**: Desarrollado en Python con **FastAPI**.
- **Base de datos**: PostgreSQL 16.
- **Contenedor Docker**: Encapsula la aplicación y sus dependencias.
- **Orquestación local**: Docker Compose para API + base de datos.
- **Repositorio GitHub**: Almacena el código fuente y el historial de versiones.
- **Infraestructura Cloud**: Servicio de despliegue local/cloud (Cloud Run / Compute Engine, opcional).

![RAMAS](.\img\ramas.jpeg "RAMAS")

**Flujo general:**
> Cliente → API (HTTP/JSON) → Lógica de negocio → PostgreSQL

---

## 💻 5. DESARROLLO DEL API

### 5.1 Tecnologías utilizadas
- **Lenguaje:** Python 3.12
- **Framework:** FastAPI + Uvicorn
- **Base de datos:** PostgreSQL
- **Formato de datos:** JSON

### 5.2 Estructura del repositorio
El repositorio incluye:
- Código fuente del API
- Archivo `README.md` documentado
- `Dockerfile`
- `docker-compose.yml`
- `requirements.txt`

![Estructura del repositorio](.\img\api_structure.jpeg "Estructura del repositorio")

### 5.3 Funcionalidades implementadas
- **Endpoint GET (Inicio/Status)**
	- Permite consultar el estado del API y verificar que el servicio está en ejecución.
	- Ruta: `/` (ejemplo público: `http://127.0.0.1:8080/`)
	- Respuesta esperada: `{"mensaje":"API Banco Simulado funcionando 🚀"}`

- **Endpoint POST (Login)**
	- Permite enviar credenciales para autenticación y obtener token.
	- Ruta: `/login` (ejemplo público: `http://127.0.0.1:8080/login`)

- **Endpoint GET (Saldo)**
	- Consulta el saldo del usuario autenticado.
	- Ruta: `/saldo`

- **Endpoint POST (Transferencia)**
	- Registra transferencias, valida saldo y activa detección de fraude.
	- Ruta: `/transferir`

- **Endpoint POST (Recarga)**
	- Permite recargar saldo del usuario autenticado.
	- Ruta: `/recargar`

- **Endpoint GET (Movimientos)**
	- Retorna historial de movimientos del usuario.
	- Ruta: `/movimientos`

- **Endpoint POST (Usuarios)**
	- Crea nuevos usuarios mediante clave de administrador (`x-admin-key`).
	- Ruta: `/usuarios`

**Validación de datos**
Se implementaron validaciones básicas como:
- Campos obligatorios
- Tipos de datos correctos
- Validaciones de montos (> 0)
- Manejo de errores con códigos HTTP

**Manejo de respuestas**
Todas las respuestas se devuelven en formato JSON estructurado.

![API en Ejecución](.\img\api_funciona.jpeg "API en Ejecución")

---

## 🌿 6. CONTROL DE VERSIONES (GITHUB)
Se utilizó GitHub para:
- Gestión del código fuente
- Control de versiones
- Trabajo con ramas (branches)

**Uso de branches**
Se recomienda implementar nuevas funcionalidades en ramas independientes, por ejemplo:
- `feature/login`
- `feature/transferencias`

Posteriormente:
- Se realiza merge hacia `main`
- Se valida la integración sin conflictos

![API Branches](.\img\branches.jpeg "API Branches")

---

## 🐳 7. CONTENERIZACIÓN CON DOCKER

### 7.1 Dockerfile
Se creó un archivo Dockerfile que permite:
- Definir el entorno de ejecución (Python 3.12 slim)
- Instalar dependencias
- Copiar el código fuente
- Exponer el puerto **interno** 8001 del contenedor
- Ejecutar la aplicación con Uvicorn

![DOCKER](.\img\docker.jpeg "DOCKER")


### 7.2 Construcción de imagen
Se construye la imagen mediante el siguiente comando:

```bash
docker build -t api-banco-simulado .
```

### 7.3 Ejecución del contenedor

```bash
docker run -p 8080:8001 --env-file .env api-banco-simulado
```

![API_DOCKER](.\img\bank_api_loc8001.jpeg "API_DOCKER")

### 7.4 Ejecución con Docker Compose (API + PostgreSQL)

```bash
docker compose up --build
```

Servicio disponible en:
- API: `http://localhost:8080`
- Base de datos: `localhost:5432`

![API_DOCKER1](.\img\bank_api_local8080.jpeg "API_DOCKER1")
---

## 🧪 8. PRUEBAS FUNCIONALES CON CURL

### 8.1 Verificación de estado

```bash
curl -X GET http://127.0.0.1:8080/
```

### 8.2 Login

```bash
curl -X POST http://127.0.0.1:8080/login \
	-H "Content-Type: application/json" \
	-d '{"username":"admin","password":"admin123"}'
```

### 8.3 Consultar saldo con token

```bash
curl -G http://127.0.0.1:8080/saldo \
	--data-urlencode "token=TOKEN_AQUI"
```

### 8.4 Transferir

```bash
curl -X POST "http://127.0.0.1:8080/transferir?token=TOKEN_AQUI" \
	-H "Content-Type: application/json" \
	-d '{"destino":"usuario2","monto":25.5}'
```

### 8.5 Recargar

```bash
curl -X POST "http://127.0.0.1:8080/recargar?token=TOKEN_AQUI" \
	-H "Content-Type: application/json" \
	-d '{"monto":100}'
```

### 8.6 Consultar movimientos

```bash
curl -G http://127.0.0.1:8080/movimientos \
	--data-urlencode "token=TOKEN_AQUI"
```

---

## ☁️ 9. DESPLIEGUE EN LA NUBE (OPCIONAL)
La API puede desplegarse en servicios cloud como:
- Google Cloud Run
- Google Compute Engine
- AWS ECS/Fargate
- Azure Container Apps

Requisitos recomendados para despliegue:
- Variables de entorno seguras (`DB_*`, `ADMIN_API_KEY`, `TELEGRAM_*`)
- Base de datos administrada
- Exposición de puertos y reglas de red
- HTTPS y control de acceso

---

## 📦 10. EJECUCIÓN  CON DOCKER COMPOSE
Para desplegar en local o servidor, se usa una imagen ya publicada en Docker Hub y se levanta todo con un único `docker compose up -d`.

![DOCK_EEXE](.\img\docker_db.jpeg "DOCK_EXE")

### 10.1 Descargar imagen publicada

```bash
docker pull gelobash/api-banco-simulado:v1
```

### 10.2 Crear archivo `.env` (NO versionar)

```env
DB_NAME=usuarios_db
DB_USER=admin
DB_PASSWORD=CAMBIAR_PASSWORD
DB_PORT=5432
ADMIN_API_KEY=CAMBIAR_ADMIN_API_KEY("CREDENCIALES DE ADMIN")
TELEGRAM_BOT_TOKEN=TU_TOKEN
TELEGRAM_CHAT_ID=TU_CHAT_ID
```

### 10.3 Crear archivo docker-compose.yml

```yaml
version: "3.9"

services:
  db:
    image: postgres:16-alpine
    container_name: banco_db
    restart: always
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
      interval: 5s
      timeout: 5s
      retries: 10

  bank_api:
    image: gelobash/api-banco-simulado:v1
    container_name: bank_api
    restart: always
    depends_on:
      db:
        condition: service_healthy
    environment:
      DB_HOST: db
      DB_PORT: ${DB_PORT}
      DB_NAME: ${DB_NAME}
      DB_USER: ${DB_USER}
      DB_PASSWORD: ${DB_PASSWORD}
      ADMIN_API_KEY: ${ADMIN_API_KEY}
      TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN:-}
      TELEGRAM_CHAT_ID: ${TELEGRAM_CHAT_ID:-}
    ports:
      - "8080:8001"

volumes:
  postgres_data:
```

### 10.4 Levantar contenedores

```bash
docker compose --env-file .env up -d
```

### 10.5 Aspectos críticos para evitar fallos (`git pull` y `docker pull`)
- Si haces `git pull`, revisa y actualiza tu archivo `.env` local antes de levantar servicios.
- Si solo haces `docker pull` de la imagen, igual necesitas `.env` con `DB_*`, `ADMIN_API_KEY` y opcionalmente `TELEGRAM_*`.
- Las credenciales deben permanecer fuera del repositorio: `.env` está ignorado en `.gitignore`.
- Las credenciales tampoco se empaquetan en la imagen: `.env` está excluido por `.dockerignore`.
- `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID` vacíos no rompen la API, pero desactivan alertas por Telegram.
- Verifica puertos libres en el host: `8080` (API) y `5432` (PostgreSQL).

---

## 🔐 11. SEGURIDAD BÁSICA IMPLEMENTADA
- Autenticación por token en endpoints protegidos
- Validación de credenciales en login
- Restricción de creación de usuarios mediante clave de administrador
- Validación de montos para prevenir operaciones inválidas
- Alertas por intentos fallidos de login y saldo insuficiente (Telegram)

---

## ✅ 12. CONCLUSIONES
El proyecto cumple con el ciclo técnico completo de una API moderna:
- Diseño e implementación backend con FastAPI
- Integración con base de datos PostgreSQL
- Contenerización con Docker
- Orquestación local con Docker Compose
- Validación de endpoints con curl
- Preparación para despliegue en nube

Como resultado, se obtiene un servicio funcional, estructurado y escalable, alineado con buenas prácticas de ingeniería de software y DevOps.

---

## 📌 13. EJECUCIÓN RÁPIDA

1. Crear archivo `.env` con variables de base de datos y seguridad.
2. Levantar servicios:

```bash
docker compose up --build
```

3. Probar estado:

```bash
curl -X GET http://127.0.0.1:8080/
```
