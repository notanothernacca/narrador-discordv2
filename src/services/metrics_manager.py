import time
import logging
from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime, timedelta
import sqlite3
from utils.config import Config

logger = logging.getLogger(__name__)

@dataclass
class VoiceMetrics:
    total_connections: int = 0
    failed_connections: int = 0
    total_disconnections: int = 0
    unexpected_disconnections: int = 0
    total_audio_time: float = 0.0
    last_connection_time: float = 0.0

@dataclass
class AudioMetrics:
    total_queued: int = 0
    total_played: int = 0
    failed_playbacks: int = 0
    total_duration: float = 0.0
    average_queue_time: float = 0.0
    queue_times: List[float] = field(default_factory=list)

class MetricsManager:
    def __init__(self):
        self.config = Config()
        self.voice_metrics: Dict[int, VoiceMetrics] = {}
        self.audio_metrics: Dict[int, AudioMetrics] = {}
        self.db_path = self.config.DB_PATH
        self._setup_database()

    def _setup_database(self):
        """Configurar la base de datos para métricas"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        guild_id INTEGER,
                        metric_type TEXT,
                        metric_name TEXT,
                        metric_value REAL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
        except Exception as e:
            logger.error(f"Error configurando base de datos de métricas: {str(e)}")

    def record_voice_connection(self, guild_id: int, success: bool):
        """Registrar intento de conexión de voz"""
        if guild_id not in self.voice_metrics:
            self.voice_metrics[guild_id] = VoiceMetrics()

        metrics = self.voice_metrics[guild_id]
        metrics.total_connections += 1
        if not success:
            metrics.failed_connections += 1
        else:
            metrics.last_connection_time = time.time()

        self._save_metric(guild_id, "voice", "connection_attempt", int(success))

    def record_voice_disconnection(self, guild_id: int, expected: bool):
        """Registrar desconexión de voz"""
        if guild_id not in self.voice_metrics:
            self.voice_metrics[guild_id] = VoiceMetrics()

        metrics = self.voice_metrics[guild_id]
        metrics.total_disconnections += 1
        if not expected:
            metrics.unexpected_disconnections += 1

        if metrics.last_connection_time > 0:
            session_duration = time.time() - metrics.last_connection_time
            metrics.total_audio_time += session_duration
            self._save_metric(guild_id, "voice", "session_duration", session_duration)

    def record_audio_queued(self, guild_id: int):
        """Registrar audio agregado a la cola"""
        if guild_id not in self.audio_metrics:
            self.audio_metrics[guild_id] = AudioMetrics()

        metrics = self.audio_metrics[guild_id]
        metrics.total_queued += 1
        metrics.queue_times.append(time.time())
        self._save_metric(guild_id, "audio", "queued", 1)

    def record_audio_played(self, guild_id: int, success: bool, duration: float):
        """Registrar reproducción de audio"""
        if guild_id not in self.audio_metrics:
            self.audio_metrics[guild_id] = AudioMetrics()

        metrics = self.audio_metrics[guild_id]
        if success:
            metrics.total_played += 1
            metrics.total_duration += duration
            
            # Calcular tiempo en cola
            if metrics.queue_times:
                queue_time = time.time() - metrics.queue_times.pop(0)
                metrics.average_queue_time = (
                    (metrics.average_queue_time * (metrics.total_played - 1) + queue_time)
                    / metrics.total_played
                )
        else:
            metrics.failed_playbacks += 1

        self._save_metric(guild_id, "audio", "played", int(success))
        if success:
            self._save_metric(guild_id, "audio", "duration", duration)

    def get_guild_stats(self, guild_id: int) -> dict:
        """Obtener estadísticas para un servidor"""
        voice_metrics = self.voice_metrics.get(guild_id, VoiceMetrics())
        audio_metrics = self.audio_metrics.get(guild_id, AudioMetrics())

        return {
            "voice": {
                "total_connections": voice_metrics.total_connections,
                "connection_success_rate": (
                    (voice_metrics.total_connections - voice_metrics.failed_connections)
                    / voice_metrics.total_connections * 100 if voice_metrics.total_connections > 0 else 0
                ),
                "unexpected_disconnection_rate": (
                    voice_metrics.unexpected_disconnections
                    / voice_metrics.total_disconnections * 100 if voice_metrics.total_disconnections > 0 else 0
                ),
                "total_audio_time": str(timedelta(seconds=int(voice_metrics.total_audio_time)))
            },
            "audio": {
                "total_queued": audio_metrics.total_queued,
                "total_played": audio_metrics.total_played,
                "success_rate": (
                    audio_metrics.total_played
                    / audio_metrics.total_queued * 100 if audio_metrics.total_queued > 0 else 0
                ),
                "average_queue_time": f"{audio_metrics.average_queue_time:.2f}s",
                "total_duration": str(timedelta(seconds=int(audio_metrics.total_duration)))
            }
        }

    def _save_metric(self, guild_id: int, metric_type: str, metric_name: str, metric_value: float):
        """Guardar métrica en la base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO metrics (guild_id, metric_type, metric_name, metric_value) VALUES (?, ?, ?, ?)",
                    (guild_id, metric_type, metric_name, metric_value)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error guardando métrica: {str(e)}")

    def get_metrics_history(self, guild_id: int, metric_type: str = None, 
                          start_time: datetime = None, end_time: datetime = None) -> List[dict]:
        """Obtener historial de métricas"""
        try:
            query = "SELECT * FROM metrics WHERE guild_id = ?"
            params = [guild_id]

            if metric_type:
                query += " AND metric_type = ?"
                params.append(metric_type)

            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time.isoformat())

            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time.isoformat())

            query += " ORDER BY timestamp DESC"

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error obteniendo historial de métricas: {str(e)}")
            return [] 