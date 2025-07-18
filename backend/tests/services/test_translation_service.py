import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from services.translation_service import TranslationService

class TestTranslationService:
    """Translation Service testleri"""
    
    @pytest.fixture
    def translation_service(self):
        """Translation service instance"""
        return TranslationService()
    
    @pytest.fixture
    def sample_job_data(self):
        """Sample job data for translation testing"""
        return {
            "title": "Senior Python Developer",
            "company": "Tech Corp",
            "location": "San Francisco, CA",
            "description": "We are looking for a senior Python developer with experience in Django and React.",
            "requirements": "Python, Django, React, PostgreSQL, AWS",
            "salary_range": "$100,000 - $150,000",
            "job_type": "Full-time",
            "experience_level": "Senior"
        }
    
    def test_service_initialization(self, translation_service):
        """Service başlatma testi"""
        assert translation_service is not None
        assert hasattr(translation_service, 'enabled')
        assert hasattr(translation_service, 'translator')
        assert hasattr(translation_service, '_translation_cache')
    
    @patch('services.translation_service.GOOGLETRANS_AVAILABLE', True)
    @patch('services.translation_service.Translator')
    def test_service_with_googletrans_available(self, mock_translator):
        """GoogleTrans mevcut olduğunda service başlatma testi"""
        mock_translator_instance = Mock()
        mock_translator.return_value = mock_translator_instance
        
        service = TranslationService()
        
        assert service.enabled is True
        assert service.translator is not None
        mock_translator.assert_called_once()
    
    @patch('services.translation_service.GOOGLETRANS_AVAILABLE', False)
    def test_service_without_googletrans(self):
        """GoogleTrans mevcut olmadığında service başlatma testi"""
        service = TranslationService()
        
        assert service.enabled is False
        assert service.translator is None
    
    def test_is_enabled(self, translation_service):
        """Service enabled durumu testi"""
        # Mock the enabled property
        translation_service.enabled = True
        translation_service.translator = Mock()
        
        assert translation_service.is_enabled() is True
        
        translation_service.enabled = False
        assert translation_service.is_enabled() is False
        
        translation_service.enabled = True
        translation_service.translator = None
        assert translation_service.is_enabled() is False
    
    @patch('services.translation_service.GOOGLETRANS_AVAILABLE', True)
    @patch('services.translation_service.Translator')
    @pytest.mark.asyncio
    async def test_detect_language_with_googletrans(self, mock_translator):
        """GoogleTrans ile dil tespiti testi"""
        mock_translator_instance = Mock()
        mock_translator_instance.detect.return_value.lang = 'en'
        mock_translator.return_value = mock_translator_instance
        
        service = TranslationService()
        result = await service.detect_language("Hello world")
        
        assert result[0] == 'en'  # First element is language
        assert isinstance(result[1], float)  # Second element is confidence
        mock_translator_instance.detect.assert_called_once()
    
    @patch('services.translation_service.GOOGLETRANS_AVAILABLE', False)
    @patch('services.translation_service.LANGDETECT_AVAILABLE', True)
    @patch('services.translation_service.detect')
    @pytest.mark.asyncio
    async def test_detect_language_with_langdetect(self, mock_detect):
        """Langdetect ile dil tespiti testi"""
        mock_detect.return_value = 'en'
        
        service = TranslationService()
        result = await service.detect_language("Hello world")
        
        assert result[0] == 'en'
        assert isinstance(result[1], float)
        mock_detect.assert_called_once()
    
    @patch('services.translation_service.GOOGLETRANS_AVAILABLE', False)
    @patch('services.translation_service.LANGDETECT_AVAILABLE', False)
    @pytest.mark.asyncio
    async def test_detect_language_fallback(self, translation_service):
        """Dil tespiti fallback testi"""
        result = await translation_service.detect_language("Hello world")
        assert result[0] == 'en'  # Default fallback
    
    @patch('services.translation_service.GOOGLETRANS_AVAILABLE', True)
    @patch('services.translation_service.Translator')
    @pytest.mark.asyncio
    async def test_translate_text_with_googletrans(self, mock_translator):
        """GoogleTrans ile metin çevirisi testi"""
        mock_translator_instance = Mock()
        mock_translator_instance.translate.return_value.text = "Merhaba dünya"
        mock_translator.return_value = mock_translator_instance
        
        service = TranslationService()
        result = await service.translate_text("Hello world", "tr")
        
        assert result['translated_text'] == "Merhaba dünya"
        assert result['target_language'] == "tr"
        mock_translator_instance.translate.assert_called_once()
    
    @patch('services.translation_service.GOOGLETRANS_AVAILABLE', False)
    @pytest.mark.asyncio
    async def test_translate_text_fallback(self, translation_service):
        """Metin çevirisi fallback testi"""
        result = await translation_service.translate_text("Hello world", "tr")
        assert result['translated_text'] == "Hello world"  # Return original text
        assert result['error'] == 'Translation service not available'
    
    @patch('services.translation_service.GOOGLETRANS_AVAILABLE', True)
    @patch('services.translation_service.Translator')
    @pytest.mark.asyncio
    async def test_translate_job_listing(self, mock_translator, sample_job_data):
        """Job listing çevirisi testi"""
        mock_translator_instance = Mock()
        mock_translator_instance.detect.return_value.lang = 'en'
        mock_translator_instance.translate.side_effect = lambda text, dest, src: Mock(text=f"Translated {text}")
        mock_translator.return_value = mock_translator_instance
        
        service = TranslationService()
        result = await service.translate_job_listing(sample_job_data)
        
        assert result['needs_translation'] is False  # Already in English
        assert result['original_language'] == 'en'
        assert 'translated_data' in result
        assert 'original_data' in result
        assert 'translation_metadata' in result
    
    @patch('services.translation_service.GOOGLETRANS_AVAILABLE', True)
    @patch('services.translation_service.Translator')
    @pytest.mark.asyncio
    async def test_translate_job_listing_same_language(self, mock_translator, sample_job_data):
        """Aynı dilde job listing çevirisi testi"""
        mock_translator_instance = Mock()
        mock_translator_instance.detect.return_value.lang = 'tr'
        mock_translator.return_value = mock_translator_instance
        
        service = TranslationService()
        result = await service.translate_job_listing(sample_job_data)
        
        assert result['needs_translation'] is True  # Should translate to English
        assert result['original_language'] == 'tr'
        assert result['translated_data'] != sample_job_data
    
    @patch('services.translation_service.GOOGLETRANS_AVAILABLE', True)
    @patch('services.translation_service.Translator')
    @pytest.mark.asyncio
    async def test_batch_translate_jobs(self, mock_translator, sample_job_data):
        """Batch job çevirisi testi"""
        mock_translator_instance = Mock()
        mock_translator_instance.detect.return_value.lang = 'tr'  # Non-English
        mock_translator_instance.translate.side_effect = lambda text, dest, src: Mock(text=f"Translated {text}")
        mock_translator.return_value = mock_translator_instance
        
        service = TranslationService()
        jobs = [sample_job_data, sample_job_data]  # Two identical jobs
        
        results = await service.batch_translate_jobs(jobs, batch_size=1)
        
        assert len(results) == 2
        for result in results:
            assert result['needs_translation'] is True  # Should translate from Turkish
            assert result['original_language'] == 'tr'
            assert 'translated_data' in result
    
    def test_get_supported_languages_with_googletrans(self):
        """GoogleTrans ile desteklenen diller testi"""
        with patch('services.translation_service.GOOGLETRANS_AVAILABLE', True):
            with patch('services.translation_service.LANGUAGES', {'en': 'english', 'tr': 'turkish'}):
                service = TranslationService()
                languages = service.get_supported_languages()
                
                assert 'en' in languages
                assert 'tr' in languages
                assert languages['en'] == 'english'
                assert languages['tr'] == 'turkish'
    
    def test_get_supported_languages_fallback(self):
        """Desteklenen diller fallback testi"""
        with patch('services.translation_service.GOOGLETRANS_AVAILABLE', False):
            service = TranslationService()
            languages = service.get_supported_languages()
            
            assert 'en' in languages
            assert 'tr' in languages
            assert 'es' in languages
            assert 'fr' in languages
            assert len(languages) >= 10  # Should have fallback languages
    
    @patch('services.translation_service.GOOGLETRANS_AVAILABLE', True)
    @patch('services.translation_service.Translator')
    @pytest.mark.asyncio
    async def test_translation_cache(self, mock_translator, sample_job_data):
        """Translation cache testi"""
        mock_translator_instance = Mock()
        mock_translator_instance.detect.return_value.lang = 'tr'
        mock_translator_instance.translate.side_effect = lambda text, dest, src: Mock(text=f"Translated {text}")
        mock_translator.return_value = mock_translator_instance
        
        service = TranslationService()
        
        # First translation
        result1 = await service.translate_job_listing(sample_job_data)
        
        # Second translation (should use cache)
        result2 = await service.translate_job_listing(sample_job_data)
        
        assert result1['needs_translation'] == result2['needs_translation']
        assert result1['original_language'] == result2['original_language']
        # Check that cache is being used
        assert len(service._translation_cache) > 0
    
    @patch('services.translation_service.GOOGLETRANS_AVAILABLE', True)
    @patch('services.translation_service.Translator')
    @pytest.mark.asyncio
    async def test_translation_error_handling(self, mock_translator, sample_job_data):
        """Translation error handling testi"""
        mock_translator_instance = Mock()
        mock_translator_instance.detect.side_effect = Exception("Translation service error")
        mock_translator.return_value = mock_translator_instance
        
        service = TranslationService()
        result = await service.translate_job_listing(sample_job_data)
        
        assert result['needs_translation'] is False
        assert result['original_language'] == 'unknown'
        assert result['translated_data'] == sample_job_data
        assert 'error' in result['translation_metadata']
    
    @pytest.mark.asyncio
    async def test_validate_translation_quality(self, translation_service):
        """Translation quality validation testi"""
        # Test good translation
        result = await translation_service.validate_translation_quality(
            "Hello world", "Merhaba dünya"
        )
        assert result['is_acceptable'] is True
        assert result['quality_score'] > 0.6
        
        # Test empty translation
        result = await translation_service.validate_translation_quality(
            "Hello world", ""
        )
        assert result['is_acceptable'] is False
        assert "Empty translation" in result['issues']
        
        # Test error keywords
        result = await translation_service.validate_translation_quality(
            "Hello world", "Translation error occurred"
        )
        assert result['is_acceptable'] is False
        assert "error keywords" in result['issues'][0]
    
    def test_clean_text_for_detection(self, translation_service):
        """Text cleaning for detection testi"""
        dirty_text = "Hello world https://example.com test@email.com 123-456-7890"
        cleaned = translation_service._clean_text_for_detection(dirty_text)
        
        assert "https://example.com" not in cleaned
        assert "test@email.com" not in cleaned
        assert "123-456-7890" not in cleaned
        assert "Hello world" in cleaned
    
    def test_service_methods_exist(self, translation_service):
        """Service metodlarının varlığını test et"""
        required_methods = [
            'is_enabled',
            'detect_language',
            'translate_text',
            'translate_job_listing',
            'batch_translate_jobs',
            'get_supported_languages',
            'validate_translation_quality',
            '_clean_text_for_detection'
        ]
        
        for method in required_methods:
            assert hasattr(translation_service, method)
            assert callable(getattr(translation_service, method))
    
    @pytest.mark.asyncio
    async def test_service_integration(self, translation_service, sample_job_data):
        """Service integration testi"""
        # Test full translation workflow
        
        # Detect language
        lang, confidence = await translation_service.detect_language("Hello world")
        assert isinstance(lang, str)
        assert isinstance(confidence, float)
        
        # Translate text
        text_result = await translation_service.translate_text("Hello world", "tr")
        assert isinstance(text_result, dict)
        assert 'translated_text' in text_result
        
        # Translate job listing
        job_result = await translation_service.translate_job_listing(sample_job_data)
        assert isinstance(job_result, dict)
        assert 'needs_translation' in job_result
        
        # Validate quality
        quality_result = await translation_service.validate_translation_quality(
            "Hello", "Merhaba"
        )
        assert isinstance(quality_result, dict)
        assert 'is_acceptable' in quality_result 