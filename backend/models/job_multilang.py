from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, List
from datetime import datetime
from bson import ObjectId

class MultiLangText(BaseModel):
    """Multi-language text field with original and translations"""
    original: str = Field(..., description="Original text in source language")
    original_lang: str = Field(..., description="ISO 639-1 language code of original")
    translations: Dict[str, str] = Field(default_factory=dict, description="Translations by language code")
    
    def get_text(self, lang: str = "en") -> str:
        """Get text in requested language, fallback to original if translation not available"""
        if lang == self.original_lang:
            return self.original
        return self.translations.get(lang, self.original)
    
    def add_translation(self, lang: str, text: str):
        """Add a translation for a specific language"""
        self.translations[lang] = text

class JobMultiLang(BaseModel):
    """Multi-language job posting model"""
    id: Optional[str] = Field(default=None, alias="_id")
    
    # Multi-language fields
    title: MultiLangText
    description: MultiLangText
    requirements: Optional[MultiLangText] = None
    benefits: Optional[MultiLangText] = None
    
    # Language-neutral fields
    company: str
    location: str
    salary_range: Optional[str] = None
    job_type: str = "Full-time"
    experience_level: str = "mid"
    apply_url: str
    source: str
    source_lang: str = Field(..., description="Primary language of the job source")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    # Translation status
    translation_status: Dict[str, str] = Field(
        default_factory=dict, 
        description="Translation status by language: pending, translated, failed"
    )
    auto_translated: List[str] = Field(
        default_factory=list, 
        description="Languages that were auto-translated"
    )
    
    
    def get_localized_job(self, lang: str = "en") -> dict:
        """Get job data localized to specific language"""
        return {
            "id": self.id,
            "title": self.title.get_text(lang),
            "description": self.description.get_text(lang),
            "requirements": self.requirements.get_text(lang) if self.requirements else None,
            "benefits": self.benefits.get_text(lang) if self.benefits else None,
            "company": self.company,
            "location": self.location,
            "salary_range": self.salary_range,
            "job_type": self.job_type,
            "experience_level": self.experience_level,
            "apply_url": self.apply_url,
            "source": self.source,
            "source_lang": self.source_lang,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_active": self.is_active,
            "is_auto_translated": lang in self.auto_translated,
            "available_languages": [self.source_lang] + list(self.title.translations.keys())
        }

class TranslationService(BaseModel):
    """Service for handling job translations using Google Translate"""
    
    @staticmethod
    async def translate_job(job: JobMultiLang, target_lang: str = "en") -> bool:
        """
        Translate job to target language using Google Translate API
        Returns True if successful, False otherwise
        """
        try:
            # Import Google Translate here to avoid dependency issues if not installed
            from googletrans import Translator
            
            translator = Translator()
            
            # Translate title
            if target_lang not in job.title.translations:
                translated_title = translator.translate(job.title.original, dest=target_lang)
                job.title.add_translation(target_lang, translated_title.text)
            
            # Translate description  
            if target_lang not in job.description.translations:
                translated_desc = translator.translate(job.description.original, dest=target_lang)
                job.description.add_translation(target_lang, translated_desc.text)
            
            # Translate requirements if exists
            if job.requirements and target_lang not in job.requirements.translations:
                translated_req = translator.translate(job.requirements.original, dest=target_lang)
                job.requirements.add_translation(target_lang, translated_req.text)
            
            # Translate benefits if exists
            if job.benefits and target_lang not in job.benefits.translations:
                translated_benefits = translator.translate(job.benefits.original, dest=target_lang)
                job.benefits.add_translation(target_lang, translated_benefits.text)
            
            # Update translation status
            job.translation_status[target_lang] = "translated"
            job.auto_translated.append(target_lang)
            job.updated_at = datetime.utcnow()
            
            return True
            
        except Exception as e:
            job.translation_status[target_lang] = "failed"
            print(f"Translation failed for job {job.id} to {target_lang}: {str(e)}")
            return False
    
    @staticmethod
    def detect_language(text: str) -> str:
        """Detect language of text and return ISO 639-1 code"""
        try:
            from googletrans import Translator
            translator = Translator()
            detection = translator.detect(text)
            return detection.lang
        except:
            return "en"  # Default to English if detection fails

# Migration utility to convert existing jobs to multi-language format
class JobMigrationService:
    """Service to migrate existing jobs to multi-language format"""
    
    @staticmethod
    async def migrate_existing_job(existing_job: dict) -> JobMultiLang:
        """Convert existing job to multi-language format"""
        
        # Detect source language
        title = existing_job.get("title", "")
        description = existing_job.get("description", "")
        source_lang = TranslationService.detect_language(f"{title} {description}")
        
        # Create multi-language job
        multilang_job = JobMultiLang(
            id=str(existing_job.get("_id", "")),
            title=MultiLangText(
                original=title,
                original_lang=source_lang
            ),
            description=MultiLangText(
                original=description,
                original_lang=source_lang
            ),
            requirements=MultiLangText(
                original=existing_job.get("requirements", ""),
                original_lang=source_lang
            ) if existing_job.get("requirements") else None,
            company=existing_job.get("company", ""),
            location=existing_job.get("location", ""),
            salary_range=existing_job.get("salary_range"),
            job_type=existing_job.get("job_type", "Full-time"),
            experience_level=existing_job.get("experience_level", "mid"),
            apply_url=existing_job.get("apply_url", ""),
            source=existing_job.get("source", ""),
            source_lang=source_lang,
            created_at=existing_job.get("created_at", datetime.utcnow()),
            updated_at=datetime.utcnow(),
            is_active=existing_job.get("is_active", True)
        )
        
        # Auto-translate to English if source is not English
        if source_lang != "en":
            await TranslationService.translate_job(multilang_job, "en")
        
        return multilang_job 