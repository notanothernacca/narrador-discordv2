from google.cloud import translate_v2 as translate
import re
import logging
import time
from typing import List, Tuple
from models.stats import Database

logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self):
        self.client = translate.Client()
        self.financial_terms_cache = {}
        self.db = Database()
        
    async def translate(self, text: str, channel_id: str, user_id: str) -> str:
        """Traducir texto de español a inglés preservando términos financieros"""
        start_time = time.time()
        try:
            # Extraer y preservar elementos especiales
            preserved_items = self._extract_preservables(text)
            
            # Reemplazar elementos preservados con placeholders
            text_with_placeholders = self._replace_with_placeholders(text, preserved_items)
            
            # Traducir el texto
            translation = self.client.translate(
                text_with_placeholders,
                target_language='en',
                source_language='es'
            )
            
            # Restaurar elementos preservados
            final_text = self._restore_preserved_items(
                translation['translatedText'],
                preserved_items
            )
            
            # Registrar estadísticas
            processing_time = time.time() - start_time
            self.db.add_translation(
                channel_id=channel_id,
                user_id=user_id,
                original_text=text,
                translated_text=final_text,
                processing_time=processing_time
            )
            
            return final_text
            
        except Exception as e:
            logger.error(f"Error en traducción: {str(e)}")
            raise
            
    def _extract_preservables(self, text: str) -> List[Tuple[str, str, int]]:
        """Extraer elementos que deben preservarse durante la traducción"""
        preserved_items = []
        
        # Patrones a preservar
        patterns = {
            'stock_symbols': r'\$[A-Z]+',  # Símbolos bursátiles ($AAPL)
            'percentages': r'-?\d+\.?\d*%',  # Porcentajes
            'numbers': r'-?\d+\.?\d*',  # Números
            'mentions': r'<@!?\d+>',  # Menciones de Discord
            'emojis': r'<a?:\w+:\d+>',  # Emojis personalizados
            'channels': r'<#\d+>'  # Menciones de canales
        }
        
        for pattern_name, pattern in patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                preserved_items.append((
                    match.group(),
                    f'__PRESERVE_{pattern_name}_{len(preserved_items)}__',
                    match.start()
                ))
                
        # Ordenar por posición para reemplazar desde el final
        preserved_items.sort(key=lambda x: x[2], reverse=True)
        return preserved_items
        
    def _replace_with_placeholders(self, text: str, preserved_items: List[Tuple[str, str, int]]) -> str:
        """Reemplazar elementos preservados con placeholders"""
        for original, placeholder, _ in preserved_items:
            text = text.replace(original, placeholder)
        return text
        
    def _restore_preserved_items(self, text: str, preserved_items: List[Tuple[str, str, int]]) -> str:
        """Restaurar elementos preservados desde los placeholders"""
        # Restaurar en orden inverso para evitar conflictos
        for original, placeholder, _ in reversed(preserved_items):
            text = text.replace(placeholder, original)
        return text 