import os
import discord
from discord.ext import commands
import logging
import time
from services.translator import TranslationService
from services.tts import TTSService
from services.queue_manager import AudioQueueManager
from services.metrics_manager import MetricsManager
from utils.config import Config

logger = logging.getLogger(__name__)

class NarradorBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        
        super().__init__(
            command_prefix='/',
            intents=intents,
            help_command=None
        )
        
        # Inicializar servicios
        logger.info("Iniciando servicios...")
        self.translator = TranslationService()
        logger.info("TranslationService iniciado")
        self.tts = TTSService()
        logger.info("TTSService iniciado")
        self.metrics_manager = MetricsManager()
        logger.info("MetricsManager iniciado")
        self.queue_manager = AudioQueueManager(self)
        logger.info("AudioQueueManager iniciado")
        
        # Cargar configuración
        self.config = Config()
        logger.info("Configuración cargada")
        
        # Registrar eventos
        self.setup_events()
        logger.info("Eventos registrados")
        
    async def setup_hook(self):
        """Configuración inicial del bot"""
        await self.load_cogs()
        
    async def load_cogs(self):
        """Cargar todos los cogs (comandos y eventos)"""
        logger.info("Iniciando carga de cogs...")
        for filename in os.listdir('./src/bot/cogs'):
            if filename.endswith('.py'):
                try:
                    logger.info(f'Intentando cargar cog: {filename}')
                    await self.load_extension(f'bot.cogs.{filename[:-3]}')
                    logger.info(f'Cog cargado exitosamente: {filename}')
                except Exception as e:
                    logger.error(f'Error al cargar cog {filename}: {str(e)}')
                    logger.error(f'Detalles del error: {e.__class__.__name__}')
        logger.info("Proceso de carga de cogs finalizado")
                    
    def setup_events(self):
        """Configurar eventos del bot"""
        
        @self.event
        async def on_ready():
            logger.info(f'Bot conectado como {self.user.name}')
            # Sincronizar comandos slash
            try:
                logger.info("Sincronizando comandos...")
                await self.tree.sync()
                logger.info("Comandos sincronizados exitosamente")
            except Exception as e:
                logger.error(f"Error sincronizando comandos: {str(e)}")
            await self.change_presence(activity=discord.Game(name="/help para comandos"))
            
        @self.event
        async def on_message(message):
            if message.author == self.user:
                return
                
            # Procesar mensajes en canales específicos
            if str(message.channel.id) in [
                self.config.ENGLISH_CHANNEL_ID,
                self.config.SPANISH_CHANNEL_ID
            ]:
                await self.process_channel_message(message)
                
            await self.process_commands(message)
            
    async def process_channel_message(self, message):
        """Procesar mensajes en canales específicos"""
        try:
            channel_id = str(message.channel.id)
            
            # Canal en inglés - narración directa
            if channel_id == self.config.ENGLISH_CHANNEL_ID:
                await self.narrate_english(
                    message.content,
                    message.author,
                    channel_id
                )
                
            # Canal en español - traducir y narrar
            elif channel_id == self.config.SPANISH_CHANNEL_ID:
                translated_text = await self.translator.translate(
                    message.content,
                    channel_id,
                    str(message.author.id)
                )
                await self.narrate_english(
                    translated_text,
                    message.author,
                    channel_id
                )
                
        except Exception as e:
            logger.error(f'Error procesando mensaje: {str(e)}')
            await message.channel.send('❌ Error al procesar el mensaje')
            
    async def narrate_english(self, text, author, channel_id):
        """Narrar texto en inglés"""
        try:
            # Generar audio
            audio_file = await self.tts.generate_audio(
                text,
                channel_id,
                str(author.id)
            )
            
            # Agregar a la cola de reproducción
            await self.queue_manager.add_to_queue(audio_file, author)
            
        except Exception as e:
            logger.error(f'Error en narración: {str(e)}') 