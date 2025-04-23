from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging
from utils.config import Config

logger = logging.getLogger(__name__)
Base = declarative_base()

class TranslationStats(Base):
    __tablename__ = 'translation_stats'
    
    id = Column(Integer, primary_key=True)
    channel_id = Column(String)
    user_id = Column(String)
    original_text = Column(String)
    translated_text = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    processing_time = Column(Float)

class TTSStats(Base):
    __tablename__ = 'tts_stats'
    
    id = Column(Integer, primary_key=True)
    channel_id = Column(String)
    user_id = Column(String)
    text = Column(String)
    audio_file = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    processing_time = Column(Float)

class Database:
    def __init__(self):
        self.config = Config()
        self.engine = create_engine(f'sqlite:///{self.config.DB_PATH}')
        self.Session = sessionmaker(bind=self.engine)
        
        # Crear tablas si no existen
        Base.metadata.create_all(self.engine)
        
    def add_translation(self, channel_id: str, user_id: str, original_text: str, 
                       translated_text: str, processing_time: float):
        """Agregar estadísticas de traducción"""
        try:
            session = self.Session()
            stats = TranslationStats(
                channel_id=channel_id,
                user_id=user_id,
                original_text=original_text,
                translated_text=translated_text,
                processing_time=processing_time
            )
            session.add(stats)
            session.commit()
        except Exception as e:
            logger.error(f"Error al guardar estadísticas de traducción: {str(e)}")
            session.rollback()
        finally:
            session.close()
            
    def add_tts(self, channel_id: str, user_id: str, text: str, 
                audio_file: str, processing_time: float):
        """Agregar estadísticas de TTS"""
        try:
            session = self.Session()
            stats = TTSStats(
                channel_id=channel_id,
                user_id=user_id,
                text=text,
                audio_file=audio_file,
                processing_time=processing_time
            )
            session.add(stats)
            session.commit()
        except Exception as e:
            logger.error(f"Error al guardar estadísticas de TTS: {str(e)}")
            session.rollback()
        finally:
            session.close()
            
    def get_channel_stats(self, channel_id: str):
        """Obtener estadísticas por canal"""
        try:
            session = self.Session()
            
            # Estadísticas de traducción
            translation_count = session.query(TranslationStats).filter_by(
                channel_id=channel_id
            ).count()
            
            # Estadísticas de TTS
            tts_count = session.query(TTSStats).filter_by(
                channel_id=channel_id
            ).count()
            
            return {
                'translation_count': translation_count,
                'tts_count': tts_count
            }
        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {str(e)}")
            return {'translation_count': 0, 'tts_count': 0}
        finally:
            session.close() 