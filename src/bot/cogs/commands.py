import discord
from discord import app_commands
from discord.ext import commands
import logging
from models.stats import Database

logger = logging.getLogger(__name__)

class CommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        
    @app_commands.command(name="narrar", description="Narra un texto en inglés")
    async def narrate(self, interaction: discord.Interaction, texto: str):
        """Narrar texto directamente en inglés"""
        try:
            await interaction.response.defer()
            
            # Narrar el texto
            await self.bot.narrate_english(
                texto, 
                interaction.user,
                str(interaction.channel_id)
            )
            
            await interaction.followup.send("✅ Texto agregado a la cola de narración")
            
        except Exception as e:
            logger.error(f"Error en comando narrar: {str(e)}")
            await interaction.followup.send("❌ Error al procesar la narración")
            
    @app_commands.command(name="status", description="Muestra el estado del bot")
    async def status(self, interaction: discord.Interaction):
        """Mostrar estado actual del bot"""
        try:
            await interaction.response.defer()
            
            # Obtener estadísticas
            queue_size = len(self.bot.queue_manager.queue)
            voice_connected = bool(interaction.guild.voice_client)
            
            embed = discord.Embed(
                title="Estado del Bot",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="Estado de Conexión",
                value="🟢 Conectado" if voice_connected else "🔴 Desconectado",
                inline=False
            )
            
            embed.add_field(
                name="Cola de Audio",
                value=f"📝 {queue_size} elementos en cola",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error en comando status: {str(e)}")
            await interaction.followup.send("❌ Error al obtener el estado")
            
    @app_commands.command(name="stats", description="Muestra estadísticas de uso")
    async def stats(self, interaction: discord.Interaction):
        """Mostrar estadísticas de uso"""
        try:
            await interaction.response.defer()
            
            # Obtener estadísticas del canal
            channel_stats = self.db.get_channel_stats(str(interaction.channel_id))
            
            embed = discord.Embed(
                title="Estadísticas de Uso",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="Traducciones",
                value=f"📊 {channel_stats['translation_count']} traducciones realizadas",
                inline=False
            )
            
            embed.add_field(
                name="Narraciones",
                value=f"🎙️ {channel_stats['tts_count']} narraciones generadas",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error en comando stats: {str(e)}")
            await interaction.followup.send("❌ Error al obtener estadísticas")
            
    @app_commands.command(name="limpiar", description="Limpia la cola de reproducción")
    async def clear(self, interaction: discord.Interaction):
        """Limpiar cola de reproducción"""
        try:
            await interaction.response.defer()
            
            # Limpiar cola
            self.bot.queue_manager.clear_queue()
            
            await interaction.followup.send("🧹 Cola de reproducción limpiada")
            
        except Exception as e:
            logger.error(f"Error en comando limpiar: {str(e)}")
            await interaction.followup.send("❌ Error al limpiar la cola")
            
    @app_commands.command(name="salir", description="Desconecta el bot del canal de voz")
    async def leave(self, interaction: discord.Interaction):
        """Desconectar del canal de voz"""
        try:
            await interaction.response.defer()
            
            if interaction.guild.voice_client:
                await interaction.guild.voice_client.disconnect()
                await interaction.followup.send("👋 Desconectado del canal de voz")
            else:
                await interaction.followup.send("❌ No estoy conectado a ningún canal de voz")
                
        except Exception as e:
            logger.error(f"Error en comando salir: {str(e)}")
            await interaction.followup.send("❌ Error al desconectar")

    @app_commands.command(name="metrics", description="Muestra métricas del bot")
    @app_commands.describe(tipo="Tipo de métricas a mostrar")
    @app_commands.choices(tipo=[
        app_commands.Choice(name="general", value="general"),
        app_commands.Choice(name="voz", value="voice"),
        app_commands.Choice(name="audio", value="audio")
    ])
    async def metrics(self, interaction: discord.Interaction, tipo: str = "general"):
        """Mostrar métricas del bot"""
        try:
            await interaction.response.defer()
            logger.info(f"Comando metrics ejecutado con tipo: {tipo}")
            
            # Obtener estadísticas
            stats = self.bot.metrics_manager.get_guild_stats(interaction.guild_id)
            
            embed = discord.Embed(
                title="📊 Métricas del Bot",
                color=discord.Color.blue()
            )

            if tipo == "general":
                # Métricas generales
                embed.add_field(
                    name="🎙️ Conexiones de Voz",
                    value=f"Total: {stats['voice']['total_connections']}\n"
                          f"Tasa de éxito: {stats['voice']['connection_success_rate']:.1f}%",
                    inline=False
                )
                embed.add_field(
                    name="🔊 Audio",
                    value=f"Total reproducidos: {stats['audio']['total_played']}\n"
                          f"Tasa de éxito: {stats['audio']['success_rate']:.1f}%",
                    inline=False
                )
                embed.add_field(
                    name="⏱️ Tiempos",
                    value=f"Tiempo total de audio: {stats['audio']['total_duration']}\n"
                          f"Tiempo promedio en cola: {stats['audio']['average_queue_time']}",
                    inline=False
                )

            elif tipo == "voice":
                # Métricas de voz
                embed.add_field(
                    name="📊 Conexiones",
                    value=f"Total intentos: {stats['voice']['total_connections']}\n"
                          f"Conexiones fallidas: {stats['voice']['failed_connections']}\n"
                          f"Tasa de éxito: {stats['voice']['connection_success_rate']:.1f}%",
                    inline=False
                )
                embed.add_field(
                    name="🔌 Desconexiones",
                    value=f"Total: {stats['voice']['total_disconnections']}\n"
                          f"Inesperadas: {stats['voice']['unexpected_disconnections']}\n"
                          f"Tasa de desconexiones inesperadas: {stats['voice']['unexpected_disconnection_rate']:.1f}%",
                    inline=False
                )
                embed.add_field(
                    name="⏱️ Tiempo Total",
                    value=f"Tiempo en canales: {stats['voice']['total_audio_time']}",
                    inline=False
                )

            else:  # audio
                # Métricas de audio
                embed.add_field(
                    name="📊 Reproducciones",
                    value=f"Total en cola: {stats['audio']['total_queued']}\n"
                          f"Reproducidos: {stats['audio']['total_played']}\n"
                          f"Fallidos: {stats['audio']['failed_playbacks']}",
                    inline=False
                )
                embed.add_field(
                    name="⏱️ Tiempos",
                    value=f"Duración total: {stats['audio']['total_duration']}\n"
                          f"Tiempo promedio en cola: {stats['audio']['average_queue_time']}",
                    inline=False
                )
                embed.add_field(
                    name="📈 Rendimiento",
                    value=f"Tasa de éxito: {stats['audio']['success_rate']:.1f}%",
                    inline=False
                )

            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error en comando metrics: {str(e)}")
            await interaction.followup.send("❌ Error al obtener métricas")

async def setup(bot):
    await bot.add_cog(CommandsCog(bot)) 