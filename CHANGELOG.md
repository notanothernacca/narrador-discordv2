# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

## [2.0.0] - 2024-04-23

### Agregado
- Sistema de métricas completo con comando `/metrics`
- Caché en memoria para traducciones con TTL
- Limpieza automática de archivos temporales
- Sistema de reconexión automática para desconexiones inesperadas
- Límite de tamaño en cola de audio (50 elementos)
- TTL para elementos en cola (5 minutos)
- Logging mejorado en todo el sistema

### Mejorado
- Manejo de errores más robusto
- Sistema de cola de audio optimizado
- Limpieza automática de archivos cada 30 minutos
- Reconexión automática en desconexiones
- Documentación actualizada

### Corregido
- Problemas de desconexión en canal de voz
- Acumulación de archivos temporales
- Manejo de errores en traducciones
- Sincronización de comandos slash

## [1.0.0] - 2024-04-22

### Características Iniciales
- Traducción automática español-inglés
- Conversión de texto a voz
- Sistema básico de cola de audio
- Comandos slash básicos
- Soporte para canales específicos
- Sistema de logging básico
- Integración con Google Cloud
- Configuración con Docker 