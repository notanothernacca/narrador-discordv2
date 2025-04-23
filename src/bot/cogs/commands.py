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

async def setup(bot):
    await bot.add_cog(CommandsCog(bot)) 