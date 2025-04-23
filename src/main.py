import os
import logging
from dotenv import load_dotenv
from bot.discord_bot import NarradorBot
from utils.logger import setup_logging

# Cargar variables de entorno
load_dotenv()

# Configurar logging
setup_logging()
logger = logging.getLogger(__name__)

def main():
    try:
        # Obtener token de Discord
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            raise ValueError("No se encontró el token de Discord en las variables de entorno")

        # Inicializar y ejecutar el bot
        bot = NarradorBot()
        bot.run(token)

    except Exception as e:
        logger.error(f"Error al iniciar el bot: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main() 