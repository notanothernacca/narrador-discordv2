#!/bin/sh

echo "Iniciando script de configuración..."

# Crear directorios si no existen
echo "Creando directorios..."
mkdir -p /app/temp_audio /app/data /app/logs

# Establecer permisos
echo "Estableciendo permisos..."
chmod -R 777 /app/temp_audio /app/data /app/logs

# Verificar Python
echo "Verificando Python..."
which python3 || which python

# Verificar directorio actual
echo "Directorio actual: $(pwd)"
ls -la /app

# Iniciar el bot
echo "Iniciando el bot..."
cd /app && python3 src/main.py 