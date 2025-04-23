from google.cloud import texttospeech
import os
import logging
import uuid
import time
from utils.config import Config
from models.stats import Database

logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self):
        self.client = texttospeech.TextToSpeechClient()
        self.config = Config()
        self.db = Database()
        
        # Crear directorio temporal si no existe
        os.makedirs(self.config.AUDIO_TEMP_DIR, exist_ok=True)
        
    async def generate_audio(self, text: str, channel_id: str, user_id: str) -> str:
        """Generar archivo de audio a partir de texto"""
        start_time = time.time()
        try:
            # Configurar la entrada de texto
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Configurar la voz
            voice = texttospeech.VoiceSelectionParams(
                language_code=self.config.TTS_LANGUAGE_CODE,
                name=self.config.TTS_VOICE_NAME
            )
            
            # Configurar el audio
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=self.config.TTS_SPEAKING_RATE,
                pitch=self.config.TTS_PITCH
            )
            
            # Realizar la síntesis
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # Generar nombre único para el archivo
            filename = f"{uuid.uuid4()}.{self.config.AUDIO_FORMAT}"
            filepath = os.path.join(self.config.AUDIO_TEMP_DIR, filename)
            
            # Guardar el audio
            with open(filepath, "wb") as out:
                out.write(response.audio_content)
                
            # Registrar estadísticas
            processing_time = time.time() - start_time
            self.db.add_tts(
                channel_id=channel_id,
                user_id=user_id,
                text=text,
                audio_file=filepath,
                processing_time=processing_time
            )
                
            logger.debug(f"Audio generado: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error en generación de audio: {str(e)}")
            raise
            
    def cleanup_old_files(self, max_age_hours: int = 1):
        """Limpiar archivos de audio antiguos"""
        try:
            current_time = time.time()
            
            for filename in os.listdir(self.config.AUDIO_TEMP_DIR):
                filepath = os.path.join(self.config.AUDIO_TEMP_DIR, filename)
                
                # Verificar edad del archivo
                file_age = current_time - os.path.getctime(filepath)
                if file_age > (max_age_hours * 3600):
                    try:
                        os.remove(filepath)
                        logger.debug(f"Archivo eliminado: {filepath}")
                    except Exception as e:
                        logger.warning(f"Error al eliminar archivo {filepath}: {str(e)}")
                        
        except Exception as e:
            logger.error(f"Error en limpieza de archivos: {str(e)}")
            
    def cleanup_file(self, filepath: str):
        """Limpiar un archivo específico"""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.debug(f"Archivo eliminado: {filepath}")
        except Exception as e:
            logger.warning(f"Error al eliminar archivo {filepath}: {str(e)}") 