# Narrador AI v2 - Bot de Discord para Trading

Bot de Discord que proporciona funcionalidades de traducción y texto a voz (TTS) para canales específicos, con sistema de métricas y gestión automática de recursos.

## Características

- Traducción automática de mensajes (español a inglés)
- Conversión de texto a voz en tiempo real
- Sistema de cola de audio con límite y TTL
- Limpieza automática de archivos temporales
- Sistema completo de métricas y estadísticas
- Reconexión automática en desconexiones

### Comandos

- `/narrar` - Lectura de texto a voz
- `/metrics` - Muestra métricas del bot (general/voz/audio)
- `/status` - Muestra el estado actual del bot
- `/stats` - Muestra estadísticas de uso
- `/limpiar` - Limpia la cola de reproducción
- `/salir` - Desconecta el bot del canal de voz

## Requisitos

- Python 3.8+
- Docker y Docker Compose
- Cuenta de Discord Developer
- Proyecto de Google Cloud (para Translate y TTS)

## Configuración

1. Crea un archivo `.env` basado en `.env.example`
2. Configura las credenciales de Discord y Google Cloud
3. Asegúrate de tener el archivo `credentials.json` de Google Cloud
4. Asegúrate de que el bot tenga los permisos necesarios:
   - Ver canales
   - Enviar mensajes
   - Conectar (voz)
   - Hablar
   - Usar actividad de voz
   - Leer el historial de mensajes
   - Adjuntar archivos

## Instalación con Docker

```bash
# Clonar el repositorio
git clone https://github.com/TU_USUARIO/narrador-discord.git
cd narrador-discord

# Crear directorios necesarios
mkdir -p data logs temp_audio

# Iniciar el bot
docker-compose up --build
```

## Variables de Entorno

- `DISCORD_TOKEN`: Token del bot de Discord
- `ENGLISH_CHANNEL_ID`: ID del canal en inglés
- `SPANISH_CHANNEL_ID`: ID del canal en español
- `GOOGLE_CLOUD_PROJECT`: ID del proyecto de Google Cloud
- `TTS_LANGUAGE_CODE`: Código de idioma para TTS (default: en-US)
- `TTS_VOICE_NAME`: Nombre de la voz a usar (default: en-US-Neural2-D)
- `TTS_SPEAKING_RATE`: Velocidad de habla (default: 1.0)
- `TTS_PITCH`: Tono de voz (default: 0.0)

## Estructura del Proyecto

```
narrador-discord/
├── src/              # Código fuente
│   ├── bot/         # Núcleo del bot y comandos
│   ├── services/    # Servicios (TTS, traducción, métricas)
│   ├── models/      # Modelos de datos
│   └── utils/       # Utilidades
├── data/             # Base de datos SQLite
├── logs/             # Archivos de registro
├── temp_audio/       # Archivos de audio temporales
├── docker/           # Configuración de Docker
├── CHANGELOG.md      # Registro de cambios
└── README.md
```

## Licencia

MIT 