import logging
import os
from logging.handlers import RotatingFileHandler
from utils.config import Config

def setup_logging():
    """Configurar el sistema de logging"""
    config = Config()
    
    # Crear directorio de logs si no existe
    os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)
    
    # Configurar formato de logging
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configurar handler para archivo
    file_handler = RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=10485760,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # Configurar handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configurar logger root
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.LOG_LEVEL.upper()))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Configurar loggers específicos
    logging.getLogger('discord').setLevel(logging.WARNING)
    logging.getLogger('google').setLevel(logging.WARNING)
    
    # Log inicial
    root_logger.info('Sistema de logging inicializado')