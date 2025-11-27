# Usar imagen base oficial de Python
FROM python:3.11-slim

# Instalar curl para healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar la librería opensky-api local (python y README.md necesario)
COPY opensky-api/python /app/opensky-api/python
COPY opensky-api/README.md /app/opensky-api/README.md

# Instalar la librería opensky-api desde el código fuente local
# Usar -e (editable mode) como recomienda la documentación oficial
RUN pip install --no-cache-dir -e /app/opensky-api/python

# Copiar archivo de dependencias
COPY requirements.txt .

# Instalar dependencias de la aplicación
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY main.py .

# Exponer el puerto en el que corre la aplicación
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
