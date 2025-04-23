# Narrador AI - Bot de Discord para Trading

Bot de Discord que proporciona funcionalidades de traducción y texto a voz (TTS) para canales específicos.

## Características

- Traducción automática de mensajes (español a inglés)
- Conversión de texto a voz en tiempo real
- Sistema de cola de audio para múltiples solicitudes
- Comando `/narrar` para lectura de texto
- Soporte para canales específicos de inglés y español

## Requisitos

- Python 3.8+
- Docker y Docker Compose
- Cuenta de Discord Developer
- Proyecto de Google Cloud (para Translate y TTS)

## Configuración

1. Crea un archivo `.env` basado en `.env.example`
2. Configura las credenciales de Discord y Google Cloud
3. Asegúrate de tener el archivo `credentials.json` de Google Cloud

## Instalación con Docker

```bash
# Clonar el repositorio
git clone https://github.com/notanothernacca/narrador-discord.git
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
- `VOICE_CHANNEL_ID`: ID del canal de voz
- `GOOGLE_CLOUD_PROJECT`: ID del proyecto de Google Cloud

## Estructura del Proyecto

```
narrador-discord/
├── src/              # Código fuente
├── data/             # Base de datos SQLite
├── logs/             # Archivos de registro
├── temp_audio/       # Archivos de audio temporales
├── Dockerfile        # Configuración de Docker
├── docker-compose.yml
└── README.md
```

## Licencia

MIT 