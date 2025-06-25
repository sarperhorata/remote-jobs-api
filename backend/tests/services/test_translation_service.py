import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any

from backend.services.translation_service import TranslationService, translation_service

class TestTranslationService:
    """Test suite for Translation Service"""
    
    @pytest.fixture
    def translation_svc(self) -> TranslationService:
        """Create translation service instance"""
        return TranslationService()
    
    @pytest.fixture
    def sample_turkish_job(self) -> Dict[str, Any]:
        """Sample Turkish job data"""
        return {
            "_id": "test_job_id",
            "title": "Yazılım Geliştirici",
            "company": "Teknoloji Şirketi",
            "location": "İstanbul, Türkiye",
            "description": "Python ve Django ile web uygulamaları geliştirmek için deneyimli bir yazılım geliştirici arıyoruz.",
            "requirements": "En az 3 yıl Python deneyimi, Django framework bilgisi",
            "benefits": "Sağlık sigortası, yemek kartı, esnek çalışma saatleri",
            "jobType": "Tam zamanlı",
            "experienceLevel": "Orta seviye",
            "skills": ["Python", "Django", "PostgreSQL", "Redis"],
            "isRemote": True
        }
    
    @pytest.fixture
    def sample_english_job(self) -> Dict[str, Any]:
        """Sample English job data"""
        return {
            "_id": "test_job_id_en",
            "title": "Software Developer",
            "company": "Tech Company",
            "location": "San Francisco, USA",
            "description": "We are looking for an experienced software developer to build web applications using Python and Django.",
            "requirements": "At least 3 years of Python experience, Django framework knowledge",
            "benefits": "Health insurance, meal allowance, flexible working hours",
            "jobType": "Full-time",
            "experienceLevel": "Mid-level",
            "skills": ["Python", "Django", "PostgreSQL", "Redis"],
            "isRemote": True
        }

    @pytest.mark.asyncio
    async def test_detect_language_turkish(self, translation_svc: TranslationService):
        """Test Turkish language detection"""
        turkish_text = "Merhaba dünya, bu bir Türkçe metin örneğidir."
        
        with patch('langdetect.detect', return_value='tr'):
            language, confidence = await translation_svc.detect_language(turkish_text)
        
        assert language == 'tr'
        assert isinstance(confidence, float)
        assert confidence > 0

    @pytest.mark.asyncio
    async def test_detect_language_english(self, translation_svc: TranslationService):
        """Test English language detection"""
        english_text = "Hello world, this is an English text example."
        
        with patch('langdetect.detect', return_value='en'):
            language, confidence = await translation_svc.detect_language(english_text)
        
        assert language == 'en'
        assert isinstance(confidence, float)

    @pytest.mark.asyncio
    async def test_detect_language_short_text(self, translation_svc: TranslationService):
        """Test language detection with short text"""
        short_text = "Hi"
        
        language, confidence = await translation_svc.detect_language(short_text)
        
        assert language == 'en'  # Default to English for short texts
        assert confidence == 0.5

    @pytest.mark.asyncio
    async def test_detect_language_empty_text(self, translation_svc: TranslationService):
        """Test language detection with empty text"""
        empty_text = ""
        
        language, confidence = await translation_svc.detect_language(empty_text)
        
        assert language == 'en'
        assert confidence == 0.5

    @pytest.mark.asyncio
    async def test_clean_text_for_detection(self, translation_svc: TranslationService):
        """Test text cleaning for language detection"""
        dirty_text = "Test text with https://example.com and email@test.com and 123-456-7890"
        
        cleaned = translation_svc._clean_text_for_detection(dirty_text)
        
        assert "https://example.com" not in cleaned
        assert "email@test.com" not in cleaned
        assert "Test text" in cleaned

    @pytest.mark.asyncio
    async def test_translate_text_success(self, translation_svc: TranslationService):
        """Test successful text translation"""
        turkish_text = "Merhaba dünya"
        
        # Mock Google Translate response
        mock_translation = MagicMock()
        mock_translation.text = "Hello world"
        
        with patch.object(translation_svc.translator, 'translate', return_value=mock_translation):
            with patch.object(translation_svc, 'detect_language', return_value=('tr', 0.8)):
                result = await translation_svc.translate_text(turkish_text, target_lang='en')
        
        assert result['translated_text'] == "Hello world"
        assert result['original_text'] == turkish_text
        assert result['source_language'] == 'tr'
        assert result['target_language'] == 'en'
        assert result['translation_confidence'] == 0.85

    @pytest.mark.asyncio
    async def test_translate_text_same_language(self, translation_svc: TranslationService):
        """Test translation when source and target are the same"""
        english_text = "Hello world"
        
        result = await translation_svc.translate_text(
            english_text, 
            target_lang='en', 
            source_lang='en'
        )
        
        assert result['translated_text'] == english_text
        assert result['original_text'] == english_text
        assert result['translation_confidence'] == 1.0

    @pytest.mark.asyncio
    async def test_translate_text_empty(self, translation_svc: TranslationService):
        """Test translation with empty text"""
        result = await translation_svc.translate_text("", target_lang='en')
        
        assert result['translated_text'] == ""
        assert result['original_text'] == ""
        assert result['translation_confidence'] == 1.0

    @pytest.mark.asyncio
    async def test_translate_text_error_handling(self, translation_svc: TranslationService):
        """Test translation error handling"""
        problematic_text = "Some text"
        
        with patch.object(translation_svc.translator, 'translate', side_effect=Exception("Translation API error")):
            result = await translation_svc.translate_text(problematic_text)
        
        assert result['translated_text'] == problematic_text  # Should return original on error
        assert 'error' in result
        assert result['translation_confidence'] == 0.0

    @pytest.mark.asyncio
    async def test_translate_job_listing_turkish(self, translation_svc: TranslationService, sample_turkish_job: Dict[str, Any]):
        """Test translating a Turkish job listing"""
        # Mock language detection
        with patch.object(translation_svc, 'detect_language', return_value=('tr', 0.9)):
            # Mock translation responses
            mock_translation = MagicMock()
            mock_translation.text = "Translated text"
            
            with patch.object(translation_svc.translator, 'translate', return_value=mock_translation):
                result = await translation_svc.translate_job_listing(sample_turkish_job)
        
        assert result['needs_translation'] == True
        assert result['original_language'] == 'tr'
        assert 'translated_data' in result
        assert 'original_data' in result
        assert 'translation_metadata' in result
        
        # Check that fields were translated
        translated_data = result['translated_data']
        assert translated_data['title'] == "Translated text"
        assert translated_data['description'] == "Translated text"

    @pytest.mark.asyncio
    async def test_translate_job_listing_english(self, translation_svc: TranslationService, sample_english_job: Dict[str, Any]):
        """Test translating an English job listing (should skip)"""
        # Mock language detection to return English
        with patch.object(translation_svc, 'detect_language', return_value=('en', 0.9)):
            result = await translation_svc.translate_job_listing(sample_english_job)
        
        assert result['needs_translation'] == False
        assert result['original_language'] == 'en'
        assert result['translated_data'] == sample_english_job
        assert result['translation_metadata']['translation_required'] == False

    @pytest.mark.asyncio
    async def test_translate_job_listing_skills_array(self, translation_svc: TranslationService):
        """Test translation of skills array in job listing"""
        job_with_foreign_skills = {
            "title": "Desarrollador",
            "description": "Trabajo de desarrollo",
            "skills": ["Python", "Desarrollo web", "Base de datos"]
        }
        
        # Mock language detection and translation
        with patch.object(translation_svc, 'detect_language', return_value=('es', 0.8)):
            mock_translation = MagicMock()
            
            def mock_translate_side_effect(*args, **kwargs):
                text = args[0] if args else kwargs.get('text', '')
                if text == "Desarrollador":
                    mock_translation.text = "Developer"
                elif text == "Trabajo de desarrollo":
                    mock_translation.text = "Development work"
                elif text == "Desarrollo web":
                    mock_translation.text = "Web development"
                elif text == "Base de datos":
                    mock_translation.text = "Database"
                else:
                    mock_translation.text = "Translated"
                return mock_translation
            
            with patch.object(translation_svc.translator, 'translate', side_effect=mock_translate_side_effect):
                result = await translation_svc.translate_job_listing(job_with_foreign_skills)
        
        translated_skills = result['translated_data']['skills']
        assert "Web development" in translated_skills
        assert "Database" in translated_skills
        assert "Python" in translated_skills  # Should remain unchanged

    @pytest.mark.asyncio
    async def test_batch_translate_jobs(self, translation_svc: TranslationService, sample_turkish_job: Dict[str, Any], sample_english_job: Dict[str, Any]):
        """Test batch translation of multiple jobs"""
        jobs = [sample_turkish_job, sample_english_job]
        
        # Mock individual job translation
        turkish_result = {
            'needs_translation': True,
            'original_language': 'tr',
            'translated_data': sample_turkish_job,
            'original_data': sample_turkish_job,
            'translation_metadata': {}
        }
        
        english_result = {
            'needs_translation': False,
            'original_language': 'en',
            'translated_data': sample_english_job,
            'original_data': sample_english_job,
            'translation_metadata': {}
        }
        
        with patch.object(translation_svc, 'translate_job_listing', side_effect=[turkish_result, english_result]):
            results = await translation_svc.batch_translate_jobs(jobs, batch_size=2)
        
        assert len(results) == 2
        assert results[0]['needs_translation'] == True
        assert results[1]['needs_translation'] == False

    @pytest.mark.asyncio
    async def test_batch_translate_with_rate_limiting(self, translation_svc: TranslationService):
        """Test batch translation with rate limiting"""
        jobs = [{"title": f"Job {i}", "description": f"Description {i}"} for i in range(25)]
        
        # Mock translation results
        mock_result = {
            'needs_translation': False,
            'original_language': 'en',
            'translated_data': {},
            'original_data': {},
            'translation_metadata': {}
        }
        
        with patch.object(translation_svc, 'translate_job_listing', return_value=mock_result):
            with patch('asyncio.sleep') as mock_sleep:
                results = await translation_svc.batch_translate_jobs(jobs, batch_size=10)
                
                # Should have called sleep for rate limiting
                assert mock_sleep.call_count >= 2  # At least 2 batches, so at least 2 sleep calls

    @pytest.mark.asyncio
    async def test_validate_translation_quality_good(self, translation_svc: TranslationService):
        """Test translation quality validation for good translation"""
        original = "This is a test sentence with reasonable length"
        translated = "Esta es una oración de prueba con longitud razonable"
        
        result = await translation_svc.validate_translation_quality(original, translated)
        
        assert result['is_acceptable'] == True
        assert result['quality_score'] >= 0.6
        assert len(result['issues']) == 0

    @pytest.mark.asyncio
    async def test_validate_translation_quality_poor(self, translation_svc: TranslationService):
        """Test translation quality validation for poor translation"""
        original = "This is a test sentence"
        translated = ""  # Empty translation
        
        result = await translation_svc.validate_translation_quality(original, translated)
        
        assert result['is_acceptable'] == False
        assert result['quality_score'] < 0.6
        assert "Empty translation" in result['issues']

    @pytest.mark.asyncio
    async def test_validate_translation_quality_error_keywords(self, translation_svc: TranslationService):
        """Test quality validation catches error keywords"""
        original = "Hello world"
        translated = "Translation failed due to error"
        
        result = await translation_svc.validate_translation_quality(original, translated)
        
        assert result['is_acceptable'] == False
        assert "error keywords" in str(result['issues'])

    @pytest.mark.asyncio
    async def test_validate_translation_quality_unusual_length(self, translation_svc: TranslationService):
        """Test quality validation catches unusual length ratios"""
        original = "Short"
        translated = "This is an extremely long translation that doesn't make sense for such a short original text"
        
        result = await translation_svc.validate_translation_quality(original, translated)
        
        assert result['is_acceptable'] == False
        assert any("length ratio" in issue for issue in result['issues'])

    @pytest.mark.asyncio
    async def test_get_supported_languages(self, translation_svc: TranslationService):
        """Test getting supported languages"""
        languages = translation_svc.get_supported_languages()
        
        assert isinstance(languages, dict)
        assert 'en' in languages
        assert 'tr' in languages
        assert 'es' in languages
        assert languages['en'] == 'english'

    @pytest.mark.asyncio
    async def test_translation_caching(self, translation_svc: TranslationService):
        """Test that translations are cached"""
        text = "Test text for caching"
        
        # Mock translation
        mock_translation = MagicMock()
        mock_translation.text = "Cached translation"
        
        with patch.object(translation_svc.translator, 'translate', return_value=mock_translation) as mock_translate:
            with patch.object(translation_svc, 'detect_language', return_value=('en', 0.8)):
                # First call
                result1 = await translation_svc.translate_text(text, target_lang='es')
                
                # Second call (should use cache)
                result2 = await translation_svc.translate_text(text, target_lang='es')
        
        # Should only call translate once due to caching
        assert mock_translate.call_count == 1
        assert result1 == result2

    @pytest.mark.asyncio
    async def test_error_handling_in_batch_translation(self, translation_svc: TranslationService):
        """Test error handling during batch translation"""
        jobs = [{"title": "Job 1"}, {"title": "Job 2"}]
        
        # Mock one successful, one failed translation
        def mock_translate_job(job):
            if job["title"] == "Job 1":
                return {
                    'needs_translation': True,
                    'original_language': 'en',
                    'translated_data': job,
                    'original_data': job,
                    'translation_metadata': {}
                }
            else:
                raise Exception("Translation error")
        
        with patch.object(translation_svc, 'translate_job_listing', side_effect=mock_translate_job):
            results = await translation_svc.batch_translate_jobs(jobs)
        
        assert len(results) == 2
        assert results[0]['needs_translation'] == True
        assert 'error' in results[1]['translation_metadata']

    @pytest.mark.asyncio
    async def test_language_detection_exception_handling(self, translation_svc: TranslationService):
        """Test handling of language detection exceptions"""
        from langdetect.lang_detect_exception import LangDetectException
        
        with patch('langdetect.detect', side_effect=LangDetectException("Detection failed", "error")):
            language, confidence = await translation_svc.detect_language("Some text")
        
        assert language == 'en'  # Should default to English
        assert confidence == 0.3  # Low confidence

    @pytest.mark.asyncio
    async def test_complex_job_translation_scenario(self, translation_svc: TranslationService):
        """Test complex job translation with multiple fields and edge cases"""
        complex_job = {
            "_id": "complex_job",
            "title": "Desarrollador Senior Full-Stack",
            "company": "Empresa Tecnológica",
            "location": "Madrid, España",
            "description": "Buscamos un desarrollador experimentado para trabajar en proyectos innovadores.",
            "requirements": "5+ años de experiencia, conocimiento de React y Node.js",
            "benefits": "Salario competitivo, trabajo remoto, seguro médico",
            "jobType": "Tiempo completo",
            "experienceLevel": "Senior",
            "skills": ["JavaScript", "React", "Node.js", "Base de datos", "Docker"],
            "isRemote": True,
            "salary": "50000-70000 EUR",
            "url": "https://company.com/jobs/123",
            "companyUrl": "https://company.com"
        }
        
        # Mock language detection and translations
        with patch.object(translation_svc, 'detect_language', return_value=('es', 0.9)):
            mock_translation = MagicMock()
            
            translation_map = {
                "Desarrollador Senior Full-Stack": "Senior Full-Stack Developer",
                "Empresa Tecnológica": "Technology Company",
                "Madrid, España": "Madrid, Spain",
                "Buscamos un desarrollador experimentado para trabajar en proyectos innovadores.": "We are looking for an experienced developer to work on innovative projects.",
                "5+ años de experiencia, conocimiento de React y Node.js": "5+ years of experience, knowledge of React and Node.js",
                "Salario competitivo, trabajo remoto, seguro médico": "Competitive salary, remote work, health insurance",
                "Tiempo completo": "Full time",
                "Senior": "Senior",
                "Base de datos": "Database"
            }
            
            def mock_translate_side_effect(*args, **kwargs):
                text = args[0] if args else kwargs.get('text', '')
                mock_translation.text = translation_map.get(text, f"Translated: {text}")
                return mock_translation
            
            with patch.object(translation_svc.translator, 'translate', side_effect=mock_translate_side_effect):
                result = await translation_svc.translate_job_listing(complex_job)
        
        assert result['needs_translation'] == True
        assert result['original_language'] == 'es'
        
        translated_data = result['translated_data']
        assert translated_data['title'] == "Senior Full-Stack Developer"
        assert translated_data['company'] == "Technology Company"
        assert "Database" in translated_data['skills']
        assert "JavaScript" in translated_data['skills']  # Should remain unchanged
        
        # Original data should be preserved
        original_data = result['original_data']
        assert original_data['title'] == "Desarrollador Senior Full-Stack"
        
        # Metadata should be present
        metadata = result['translation_metadata']
        assert metadata['detected_language'] == 'es'
        assert metadata['translation_required'] == True
        assert 'translated_at' in metadata

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 