# OpenSky Aviation API - Docker Setup

Esta es una API FastAPI que proporciona endpoints para consultar información de aeronaves usando la API de OpenSky Network.

## 📋 Requisitos Previos

- Docker instalado (versión 20.10 o superior)
- Docker Compose instalado (versión 2.0 o superior)

> [!IMPORTANT]
> Este proyecto utiliza la librería **opensky-api local** (del directorio `opensky-api/python`) en lugar de la versión de PyPI. Esto garantiza compatibilidad con el código fuente específico que estás usando.

## 🚀 Inicio Rápido

### 1. Construir y ejecutar con Docker Compose

```bash
# Construir la imagen y levantar el contenedor
docker-compose up --build

# O en modo detached (segundo plano)
docker-compose up -d --build
```

### 2. Verificar que la API está funcionando

Abre tu navegador en: `http://localhost:8000`

O usa curl:
```bash
curl http://localhost:8000
```

## 🛠️ Comandos Útiles

### Detener los contenedores
```bash
docker-compose down
```

### Ver logs
```bash
# Logs en tiempo real
docker-compose logs -f

# Logs solo del servicio api
docker-compose logs -f api
```

### Reconstruir la imagen
```bash
docker-compose build --no-cache
```

### Reiniciar el servicio
```bash
docker-compose restart
```

## 📡 Endpoints Disponibles

- `GET /` - Información de la API
- `GET /opensky/states` - Obtener todos los estados de aeronaves
- `GET /opensky/track/{aircraft_id}` - Obtener trayectoria de una aeronave
- `GET /opensky/state/{aircraft_id}` - Obtener estado de una aeronave específica
- `GET /opensky/flights/{aircraft_id}` - Obtener vuelos de una aeronave

### Ejemplo de uso:
```bash
# Obtener todos los estados
curl http://localhost:8000/opensky/states

# Obtener trayectoria de una aeronave específica
curl http://localhost:8000/opensky/track/a12345

# Obtener estado de una aeronave
curl http://localhost:8000/opensky/state/a12345
```

## 🔧 Desarrollo

El archivo `docker-compose.yml` está configurado con un volumen que monta `main.py`, permitiendo hot-reload durante el desarrollo. Cualquier cambio en `main.py` se reflejará automáticamente sin necesidad de reconstruir la imagen.

## 🏗️ Estructura de Archivos

```
endpoints/
├── Dockerfile              # Definición de la imagen Docker
├── docker-compose.yml      # Orquestación de servicios
├── requirements.txt        # Dependencias Python (FastAPI, Uvicorn)
├── .dockerignore          # Archivos excluidos del build
├── main.py                # Código principal de la API
├── opensky-api/           # Librería opensky-api (código fuente local)
│   └── python/            # Implementación Python de la API
└── README_DOCKER.md       # Este archivo
```

> [!NOTE]
> La librería `opensky-api` se instala desde el directorio local `opensky-api/python` durante el build de Docker, no desde PyPI.

## 🐛 Troubleshooting

### El puerto 8000 ya está en uso
```bash
# Cambiar el puerto en docker-compose.yml
ports:
  - "8080:8000"  # Usar puerto 8080 en lugar de 8000
```

### Problemas con permisos
```bash
# Ejecutar con sudo (Linux)
sudo docker-compose up
```

### Limpiar todo y empezar de nuevo
```bash
docker-compose down -v
docker-compose up --build
```

## 📝 Notas

- La API usa la OpenSky Network API pública que tiene límites de rate
- El healthcheck verifica cada 30 segundos que la API esté respondiendo
- Los logs se pueden ver con `docker-compose logs -f`
