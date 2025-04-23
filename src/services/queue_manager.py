import asyncio
import discord
from collections import deque
import logging
from typing import Optional, Deque, Tuple
from utils.config import Config

logger = logging.getLogger(__name__)

class AudioQueueManager:
    def __init__(self):
        self.queue: Deque[Tuple[str, discord.Member]] = deque()
        self.current_audio: Optional[str] = None
        self.is_playing = False
        self.config = Config()
        self._lock = asyncio.Lock()
        
    async def add_to_queue(self, audio_file: str, author: discord.Member):
        """Agregar archivo de audio a la cola"""
        async with self._lock:
            self.queue.append((audio_file, author))
            logger.debug(f"Audio agregado a la cola: {audio_file}")
            
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
                        await voice_channel.connect()
                    except Exception as e:
                        logger.error(f"Error al conectar al canal de voz: {str(e)}")
                        self.queue.popleft()
                        continue
                        
                # Reproducir audio
                try:
                    self.current_audio = audio_file
                    guild.voice_client.play(
                        discord.FFmpegPCMAudio(audio_file),
                        after=lambda e: asyncio.run_coroutine_threadsafe(
                            self._song_finished(e, guild),
                            guild.loop
                        )
                    )
                    
                    # Esperar a que termine la reproducción
                    while guild.voice_client and guild.voice_client.is_playing():
                        await asyncio.sleep(0.1)
                        
                except Exception as e:
                    logger.error(f"Error reproduciendo audio: {str(e)}")
                    
                finally:
                    if self.queue:
                        self.queue.popleft()
                    self.current_audio = None
                    
        except Exception as e:
            logger.error(f"Error procesando cola: {str(e)}")
            
        finally:
            self.is_playing = False
            
    async def _song_finished(self, error, guild: discord.Guild):
        """Callback para cuando termina la reproducción"""
        if error:
            logger.error(f"Error en reproducción: {str(error)}")
            
        # Desconectar si la cola está vacía
        if not self.queue and guild.voice_client:
            await guild.voice_client.disconnect()
            
    def clear_queue(self):
        """Limpiar la cola de reproducción"""
        self.queue.clear()
        logger.info("Cola de reproducción limpiada") 