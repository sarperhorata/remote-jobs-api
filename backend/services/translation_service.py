"""
Translation service for job listings with optional GoogleTrans support
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# Optional imports - graceful fallback if not available
try:
    from googletrans import LANGUAGES, Translator

    GOOGLETRANS_AVAILABLE = True
except ImportError:
    GOOGLETRANS_AVAILABLE = False
    LANGUAGES = {}
    Translator = None

# Try to import langdetect for better language detection
try:
    from langdetect import detect

    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    detect = None

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

        # Cache for translations
        self._translation_cache = {}

    def is_enabled(self) -> bool:
        """Check if translation service is available"""
        return self.enabled and self.translator is not None

    def _clean_text_for_detection(self, text: str) -> str:
        """Clean text for better language detection"""
        if not text:
            return ""

        # Remove URLs
        text = re.sub(r"https?://\S+", "", text)
        # Remove email addresses
        text = re.sub(r"\S+@\S+", "", text)
        # Remove phone numbers
        text = re.sub(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "", text)
        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text).strip()

        return text

    async def detect_language(self, text: str) -> Tuple[str, float]:
        """Detect language of text with confidence score"""
        if not text:
            return "en", 0.5

        # Clean text for detection
        cleaned_text = self._clean_text_for_detection(text)

        if len(cleaned_text) < 3:
            return "en", 0.5

        try:
            if LANGDETECT_AVAILABLE:
                detected_lang = detect(cleaned_text)
                return detected_lang, 0.8
            elif self.is_enabled():
                detected = self.translator.detect(cleaned_text)
                confidence = getattr(detected, "confidence", 0.7)
                return (
                    detected.lang if detected and hasattr(detected, "lang") else "en"
                ), confidence
            else:
                return "en", 0.3
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return "en", 0.3

    async def translate_text(
        self, text: str, target_lang: str = "tr", source_lang: Optional[str] = None
    ) -> Dict[str, Any]:
        """Translate text with comprehensive error handling"""
        if not text:
            return {
                "translated_text": "",
                "original_text": "",
                "source_language": source_lang or "en",
                "target_language": target_lang,
                "translation_confidence": 1.0,
            }

        # Check cache
        cache_key = f"{text}:{target_lang}:{source_lang}"
        if cache_key in self._translation_cache:
            return self._translation_cache[cache_key]

        # Detect source language if not provided
        if not source_lang:
            source_lang, confidence = await self.detect_language(text)
        else:
            confidence = 0.8

        # If source and target are the same, return original
        if source_lang == target_lang:
            result = {
                "translated_text": text,
                "original_text": text,
                "source_language": source_lang,
                "target_language": target_lang,
                "translation_confidence": 1.0,
            }
            self._translation_cache[cache_key] = result
            return result

        if not self.is_enabled():
            result = {
                "translated_text": text,
                "original_text": text,
                "source_language": source_lang,
                "target_language": target_lang,
                "translation_confidence": 0.0,
                "error": "Translation service not available",
            }
            return result

        try:
            translation = self.translator.translate(
                text, dest=target_lang, src=source_lang
            )
            translated_text = (
                translation.text
                if translation and hasattr(translation, "text")
                else text
            )

            result = {
                "translated_text": translated_text,
                "original_text": text,
                "source_language": source_lang,
                "target_language": target_lang,
                "translation_confidence": min(confidence + 0.05, 1.0),
            }

            # Cache the result
            self._translation_cache[cache_key] = result
            return result

        except Exception as e:
            logger.warning(f"Translation failed: {e}")
            result = {
                "translated_text": text,
                "original_text": text,
                "source_language": source_lang,
                "target_language": target_lang,
                "translation_confidence": 0.0,
                "error": str(e),
            }
            return result

    async def validate_translation_quality(
        self, original: str, translated: str
    ) -> Dict[str, Any]:
        """Validate translation quality"""
        issues = []

        # Check if translation is empty
        if not translated or translated.strip() == "":
            issues.append("Empty translation")

        # Check for error keywords
        error_keywords = ["error", "failed", "invalid", "cannot"]
        if any(keyword in translated.lower() for keyword in error_keywords):
            issues.append("Translation contains error keywords")

        # Check unusual length ratios
        if original and translated:
            ratio = len(translated) / len(original)
            if ratio > 3.0 or ratio < 0.2:
                issues.append(f"Unusual length ratio: {ratio:.2f}")

        # Calculate quality score
        quality_score = 1.0
        if issues:
            quality_score = max(0.0, 1.0 - (len(issues) * 0.3))

        return {
            "is_acceptable": quality_score >= 0.6,
            "quality_score": quality_score,
            "issues": issues,
        }

    async def translate_job_listing(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Translate job listing with comprehensive error handling"""
        if not self.is_enabled():
            logger.info("Translation service disabled - returning original job data")
            return {
                "needs_translation": False,
                "original_language": "unknown",
                "translated_data": job_data,
                "original_data": job_data,
                "translation_metadata": {
                    "service_available": False,
                    "error": "Translation service not available",
                    "translation_required": False,
                },
            }

        try:
            # Detect original language
            title = job_data.get("title", "")
            description = job_data.get("description", "")

            if not title and not description:
                return {
                    "needs_translation": False,
                    "original_language": "unknown",
                    "translated_data": job_data,
                    "original_data": job_data,
                    "translation_metadata": {
                        "error": "No content to translate",
                        "translation_required": False,
                    },
                }

            # Detect language using title (usually more reliable than description)
            original_lang, confidence = await self.detect_language(title)

            # Only translate if not already in English
            if original_lang == "en":
                return {
                    "needs_translation": False,
                    "original_language": "en",
                    "translated_data": job_data,
                    "original_data": job_data,
                    "translation_metadata": {
                        "status": "already_english",
                        "translation_required": False,
                        "detected_language": "en",
                    },
                }

            # Create translated data copy
            translated_data = job_data.copy()

            # Translate key fields
            if title:
                title_result = await self.translate_text(title, "en")
                translated_data["title"] = title_result["translated_text"]

            if description:
                # Limit description length for translation
                desc_sample = (
                    description[:500] + "..." if len(description) > 500 else description
                )
                desc_result = await self.translate_text(desc_sample, "en")
                translated_data["description"] = desc_result["translated_text"]

            # Translate other fields if available
            for field in ["requirements", "benefits"]:
                if job_data.get(field):
                    field_result = await self.translate_text(
                        job_data[field][:300], "en"
                    )
                    translated_data[field] = field_result["translated_text"]

            # Translate skills array if present
            if "skills" in job_data and isinstance(job_data["skills"], list):
                translated_skills = []
                for skill in job_data["skills"]:
                    if isinstance(skill, str) and len(skill) > 3:
                        skill_result = await self.translate_text(skill, "en")
                        translated_skills.append(skill_result["translated_text"])
                    else:
                        translated_skills.append(skill)  # Keep short skills unchanged
                translated_data["skills"] = translated_skills

            return {
                "needs_translation": True,
                "original_language": original_lang,
                "translated_data": translated_data,
                "original_data": job_data,
                "translation_metadata": {
                    "detected_language": original_lang,
                    "translation_required": True,
                    "translated_at": datetime.utcnow().isoformat(),
                    "service": "googletrans",
                    "status": "success",
                },
            }

        except Exception as e:
            logger.error(f"Translation job failed: {str(e)}")
            return {
                "needs_translation": False,
                "original_language": "unknown",
                "translated_data": job_data,
                "original_data": job_data,
                "translation_metadata": {
                    "error": str(e),
                    "status": "failed",
                    "translation_required": False,
                },
            }

    async def batch_translate_jobs(
        self, jobs: List[Dict[str, Any]], batch_size: int = 10
    ) -> List[Dict[str, Any]]:
        """Translate multiple jobs in batches with rate limiting"""
        results = []

        for i in range(0, len(jobs), batch_size):
            batch = jobs[i : i + batch_size]
            batch_results = []

            for job in batch:
                try:
                    result = await self.translate_job_listing(job)
                    batch_results.append(result)
                except Exception as e:
                    error_result = {
                        "needs_translation": False,
                        "original_language": "unknown",
                        "translated_data": job,
                        "original_data": job,
                        "translation_metadata": {"error": str(e), "status": "failed"},
                    }
                    batch_results.append(error_result)

            results.extend(batch_results)

            # Rate limiting: wait between batches
            if i + batch_size < len(jobs):
                await asyncio.sleep(1)

        return results

    def get_supported_languages(self) -> Dict[str, str]:
        """Get supported languages"""
        if GOOGLETRANS_AVAILABLE and LANGUAGES:
            return LANGUAGES
        return {
            "en": "english",
            "tr": "turkish",
            "es": "spanish",
            "fr": "french",
            "de": "german",
            "it": "italian",
            "pt": "portuguese",
            "ru": "russian",
            "zh": "chinese",
            "ja": "japanese",
            "ko": "korean",
            "ar": "arabic",
        }


# Global translation service instance
translation_service = TranslationService()


# Compatibility functions for existing code
async def translate_job_to_turkish(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy function for backward compatibility"""
    return await translation_service.translate_job_listing(job_data)


def get_supported_languages() -> Dict[str, str]:
    """Get supported languages"""
    return translation_service.get_supported_languages()
