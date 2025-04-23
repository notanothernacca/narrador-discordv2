import asyncio
import discord
from collections import deque
import logging
import time
from typing import Optional, Deque, Tuple
from utils.config import Config

logger = logging.getLogger(__name__)

class AudioQueueManager:
    def __init__(self, bot):
        self.queue: Deque[Tuple[str, discord.Member]] = deque()
        self.current_audio: Optional[str] = None
        self.is_playing = False
        self.config = Config()
        self._lock = asyncio.Lock()
        self.bot = bot
        self.reconnection_attempts = {}
        self._audio_start_time = 0
        
    async def add_to_queue(self, audio_file: str, author: discord.Member):
        """Agregar archivo de audio a la cola"""
        async with self._lock:
            self.queue.append((audio_file, author))
            logger.debug(f"Audio agregado a la cola: {audio_file}")
            
            # Registrar audio en cola
            self.bot.metrics_manager.record_audio_queued(author.guild.id)
            
            if not self.is_playing:
                await self._process_queue(author.guild)
                
    async def _process_queue(self, guild: discord.Guild):
        """Procesar la cola de audio"""
        if self.is_playing:
            return
            
        try:
            self.is_playing = True
            
            while self.queue:
                audio_file, author = self.queue[0]
                
                # Verificar si el autor está en un canal de voz
                if not author.voice:
                    logger.warning(f"Usuario {author.name} no está en un canal de voz")
                    self.queue.popleft()
                    continue
                    
                voice_channel = author.voice.channel
                
                # Conectar al canal de voz si no está conectado
                if not guild.voice_client:
                    try:
                        await self._connect_to_voice(voice_channel, guild)
                    except Exception as e:
                        logger.error(f"Error al conectar al canal de voz: {str(e)}")
                        self.bot.metrics_manager.record_voice_connection(guild.id, False)
                        self.queue.popleft()
                        continue
                        
                # Reproducir audio
                try:
                    self.current_audio = audio_file
                    self._audio_start_time = time.time()
                    
                    # Asegurarnos de usar el loop correcto
                    loop = self.bot.loop if hasattr(self.bot, 'loop') else asyncio.get_event_loop()
                    
                    guild.voice_client.play(
                        discord.FFmpegPCMAudio(audio_file),
                        after=lambda e: asyncio.run_coroutine_threadsafe(
                            self._song_finished(e, guild),
                            loop
                        )
                    )
                    
                    # Esperar a que termine la reproducción
                    while guild.voice_client and guild.voice_client.is_playing():
                        await asyncio.sleep(0.1)
                        
                except Exception as e:
                    logger.error(f"Error reproduciendo audio: {str(e)}")
                    await self._handle_playback_error(guild, e)
                    
                finally:
                    if self.queue:
                        self.queue.popleft()
                    self.current_audio = None
                    
        except Exception as e:
            logger.error(f"Error procesando cola: {str(e)}")
            
        finally:
            self.is_playing = False
            
    async def _connect_to_voice(self, voice_channel: discord.VoiceChannel, guild: discord.Guild, max_retries: int = 3):
        """Conectar al canal de voz con reintentos"""
        retries = self.reconnection_attempts.get(guild.id, 0)
        
        while retries < max_retries:
            try:
                await voice_channel.connect()
                self.reconnection_attempts[guild.id] = 0  # Reset counter on success
                logger.info(f"Conectado al canal de voz: {voice_channel.name}")
                self.bot.metrics_manager.record_voice_connection(guild.id, True)
                return
            except Exception as e:
                retries += 1
                self.reconnection_attempts[guild.id] = retries
                logger.warning(f"Intento {retries}/{max_retries} de conexión fallido: {str(e)}")
                if retries < max_retries:
                    await asyncio.sleep(1)  # Wait before retrying
                else:
                    self.bot.metrics_manager.record_voice_connection(guild.id, False)
                    raise
                    
    async def _handle_playback_error(self, guild: discord.Guild, error: Exception):
        """Manejar errores de reproducción"""
        logger.error(f"Error en reproducción: {str(error)}")
        
        # Registrar error de reproducción
        if self._audio_start_time > 0:
            duration = time.time() - self._audio_start_time
            self.bot.metrics_manager.record_audio_played(guild.id, False, duration)
        
        if guild.voice_client:
            try:
                await guild.voice_client.disconnect()
                self.bot.metrics_manager.record_voice_disconnection(guild.id, False)
                logger.info("Desconectado del canal de voz debido a error")
            except Exception as e:
                logger.error(f"Error al desconectar: {str(e)}")
                
        # Limpiar estado
        self.is_playing = False
        self.current_audio = None
            
    async def _song_finished(self, error, guild: discord.Guild):
        """Callback para cuando termina la reproducción"""
        duration = time.time() - self._audio_start_time if self._audio_start_time > 0 else 0
        
        if error:
            logger.error(f"Error en reproducción: {str(error)}")
            self.bot.metrics_manager.record_audio_played(guild.id, False, duration)
            await self._handle_playback_error(guild, error)
        else:
            self.bot.metrics_manager.record_audio_played(guild.id, True, duration)
            
        # Desconectar si la cola está vacía
        if not self.queue and guild.voice_client:
            try:
                await guild.voice_client.disconnect()
                self.bot.metrics_manager.record_voice_disconnection(guild.id, True)
                logger.info("Desconectado del canal de voz - Cola vacía")
            except Exception as e:
                logger.error(f"Error al desconectar: {str(e)}")
            
    def clear_queue(self):
        """Limpiar la cola de reproducción"""
        self.queue.clear()
        logger.info("Cola de reproducción limpiada") 