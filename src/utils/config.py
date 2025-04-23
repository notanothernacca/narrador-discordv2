import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        
        # Discord
        self.DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
        self.ENGLISH_CHANNEL_ID = os.getenv('ENGLISH_CHANNEL_ID')
        self.SPANISH_CHANNEL_ID = os.getenv('SPANISH_CHANNEL_ID')
        
        # Google Cloud
        self.GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT')
        self.GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        # TTS Configuration
        self.TTS_LANGUAGE_CODE = os.getenv('TTS_LANGUAGE_CODE', 'en-US')
        self.TTS_VOICE_NAME = os.getenv('TTS_VOICE_NAME', 'en-US-Neural2-D')
        self.TTS_SPEAKING_RATE = float(os.getenv('TTS_SPEAKING_RATE', '1.0'))
        self.TTS_PITCH = float(os.getenv('TTS_PITCH', '0.0'))
        
        # Audio
        self.AUDIO_TEMP_DIR = os.getenv('AUDIO_TEMP_DIR', 'temp_audio')
        self.AUDIO_FORMAT = os.getenv('AUDIO_FORMAT', 'mp3')
        
        # Rate Limiting
        self.RATE_LIMIT_MESSAGES = int(os.getenv('RATE_LIMIT_MESSAGES', '5'))
        self.RATE_LIMIT_PERIOD = int(os.getenv('RATE_LIMIT_PERIOD', '60'))
        
        # Database
        self.DB_PATH = os.getenv('DB_PATH', 'data/bot.db')
        
        # Logging
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE = os.getenv('LOG_FILE', 'logs/bot.log')
        
        # Validación de configuración crítica
        self._validate_config()
        
    def _validate_config(self):
        """Validar configuración crítica"""
        required_vars = [
            'DISCORD_TOKEN',
            'ENGLISH_CHANNEL_ID',
            'SPANISH_CHANNEL_ID',
            'GOOGLE_CLOUD_PROJECT',
            'GOOGLE_APPLICATION_CREDENTIALS'
        ]
        
        missing_vars = [var for var in required_vars if not getattr(self, var)]
        
        if missing_vars:
            raise ValueError(
                f"Faltan las siguientes variables de entorno requeridas: {', '.join(missing_vars)}"
            ) 