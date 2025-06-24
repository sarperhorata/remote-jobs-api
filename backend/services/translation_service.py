"""
Translation service for job listings with optional GoogleTrans support
"""

import logging
from typing import Optional, Dict, Any, List
import asyncio

# Optional imports - graceful fallback if not available
try:
    from googletrans import Translator, LANGUAGES
    GOOGLETRANS_AVAILABLE = True
except ImportError:
    GOOGLETRANS_AVAILABLE = False
    LANGUAGES = {}
    Translator = None

logger = logging.getLogger(__name__)

class TranslationService:
    """Enhanced translation service with optional GoogleTrans support"""
    
    def __init__(self):
        if GOOGLETRANS_AVAILABLE:
            try:
                self.translator = Translator()
                self.enabled = True
                logger.info("GoogleTrans translation service enabled")
            except Exception as e:
                logger.warning(f"GoogleTrans initialization failed: {e}")
                self.enabled = False
                self.translator = None
        else:
            logger.warning("GoogleTrans not available - translation service disabled")
            self.enabled = False
            self.translator = None
    
    def is_enabled(self) -> bool:
        """Check if translation service is available"""
        return self.enabled and self.translator is not None
    
    async def detect_language(self, text: str) -> str:
        """Detect language of text with fallback"""
        if not self.is_enabled() or not text:
            return "en"  # Default fallback
        
        try:
            detected = self.translator.detect(text)
            return detected.lang if detected and hasattr(detected, 'lang') else "en"
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return "en"
    
    async def translate_text(self, text: str, target_lang: str = "tr") -> Optional[str]:
        """Translate text with error handling"""
        if not self.is_enabled() or not text:
            return None
        
        try:
            result = self.translator.translate(text, dest=target_lang)
            return result.text if result and hasattr(result, 'text') else None
        except Exception as e:
            logger.warning(f"Translation failed: {e}")
            return None
    
    async def translate_job_listing(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Translate job listing with comprehensive error handling"""
        if not self.is_enabled():
            logger.info("Translation service disabled - returning original job data")
            return {
                "needs_translation": False,
                "original_language": "unknown",
                "translated_fields": {},
                "translation_metadata": {
                    "service_available": False,
                    "error": "Translation service not available"
                }
            }
        
        try:
            # Detect original language
            title = job_data.get("title", "")
            description = job_data.get("description", "")
            
            if not title and not description:
                return {
                    "needs_translation": False,
                    "original_language": "unknown",
                    "translated_fields": {},
                    "translation_metadata": {"error": "No content to translate"}
                }
            
            # Detect language using title (usually more reliable than description)
            original_lang = await self.detect_language(title)
            
            # Only translate if not already in Turkish
            if original_lang == "tr":
                return {
                    "needs_translation": False,
                    "original_language": "tr",
                    "translated_fields": {},
                    "translation_metadata": {"status": "already_turkish"}
                }
            
            # Translate key fields
            translated_fields = {}
            
            if title:
                translated_title = await self.translate_text(title, "tr")
                if translated_title:
                    translated_fields["title"] = translated_title
            
            if description:
                # Limit description length for translation
                desc_sample = description[:500] + "..." if len(description) > 500 else description
                translated_desc = await self.translate_text(desc_sample, "tr")
                if translated_desc:
                    translated_fields["description"] = translated_desc
            
            # Translate other fields if available
            for field in ["requirements", "benefits"]:
                if job_data.get(field):
                    translated_field = await self.translate_text(job_data[field][:300], "tr")
                    if translated_field:
                        translated_fields[field] = translated_field
            
            return {
                "needs_translation": True,
                "original_language": original_lang,
                "translated_fields": translated_fields,
                "translation_metadata": {
                    "service": "googletrans",
                    "translated_field_count": len(translated_fields),
                    "status": "success"
                }
            }
            
        except Exception as e:
            logger.error(f"Translation job failed: {str(e)}")
            return {
                "needs_translation": False,
                "original_language": "unknown",
                "translated_fields": {},
                "translation_metadata": {
                    "error": str(e),
                    "status": "failed"
                }
            }

# Global translation service instance
translation_service = TranslationService()

# Compatibility functions for existing code
async def translate_job_to_turkish(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy function for backward compatibility"""
    return await translation_service.translate_job_listing(job_data)

def get_supported_languages() -> Dict[str, str]:
    """Get supported languages"""
    if GOOGLETRANS_AVAILABLE:
        return LANGUAGES
    return {"en": "English", "tr": "Turkish"}  # Fallback 