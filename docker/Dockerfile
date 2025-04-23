FROM python:3.10-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libffi-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de la aplicación
WORKDIR /app

# Crear directorios necesarios
RUN mkdir -p /app/temp_audio /app/data /app/logs && \
    chmod -R 777 /app/temp_audio /app/data /app/logs

# Copiar archivos de requisitos
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# Establecer variables de entorno
ENV PYTHONPATH=/app
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json
ENV PYTHONUNBUFFERED=1

# Comando para ejecutar el bot
CMD ["python", "src/main.py"] 