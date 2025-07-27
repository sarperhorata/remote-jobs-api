import os
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from services.fake_job_detector import FakeJobAnalysis, FakeJobDetector


class TestFakeJobDetector:
    """Fake Job Detector Service testleri"""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client"""
        mock_client = Mock()
        mock_client.chat.completions.create = AsyncMock()
        return mock_client

    @pytest.fixture
    def fake_job_detector_with_openai(self, mock_openai_client):
        """OpenAI ile fake job detector instance"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            with patch(
                "services.fake_job_detector.openai.OpenAI",
                return_value=mock_openai_client,
            ):
                detector = FakeJobDetector()
                detector.client = mock_openai_client
                return detector

    @pytest.fixture
    def fake_job_detector_without_openai(self):
        """OpenAI olmadan fake job detector instance"""
        with patch.dict(os.environ, {}, clear=True):
            detector = FakeJobDetector()
            return detector

    @pytest.fixture
    def sample_job_data(self):
        """Sample job data for testing"""
        return {
            "_id": "job123",
            "title": "Senior Python Developer",
            "company": "Tech Corp",
            "location": "Remote",
            "description": "We are looking for a senior Python developer with experience in Django and React.",
            "requirements": "Python, Django, React, PostgreSQL, AWS",
            "salary_range": "$100,000 - $150,000",
            "job_type": "Full-time",
            "experience_level": "Senior",
            "apply_url": "https://techcorp.com/careers",
            "url": "https://techcorp.com/job/123",
        }

    @pytest.fixture
    def sample_fake_job_data(self):
        """Sample fake job data for testing"""
        return {
            "_id": "fake_job123",
            "title": "Work from Home - Earn $5000 per week",
            "company": "Unknown Company",
            "location": "Remote",
            "description": "Easy money! No experience needed. Work from home and earn $5000 per week. Contact us via WhatsApp.",
            "requirements": "No experience required",
            "salary_range": "$5000 per week",
            "job_type": "Part-time",
            "experience_level": "Entry",
            "apply_url": "https://suspicious-site.com/apply",
            "url": "https://suspicious-site.com/job/123",
        }

    def test_service_initialization_with_openai(self, fake_job_detector_with_openai):
        """OpenAI ile service başlatma testi"""
        detector = fake_job_detector_with_openai

        assert detector is not None
        assert hasattr(detector, "client")
        assert detector.client is not None
        assert hasattr(detector, "red_flag_patterns")
        assert len(detector.red_flag_patterns) > 0

    def test_service_initialization_without_openai(
        self, fake_job_detector_without_openai
    ):
        """OpenAI olmadan service başlatma testi"""
        detector = fake_job_detector_without_openai

        assert detector is not None
        assert detector.client is None
        assert hasattr(detector, "red_flag_patterns")
        assert len(detector.red_flag_patterns) > 0

    def test_red_flag_patterns_initialization(self, fake_job_detector_with_openai):
        """Red flag patterns başlatma testi"""
        detector = fake_job_detector_with_openai

        expected_patterns = [
            "unrealistic_salary",
            "vague_job_description",
            "suspicious_contact",
            "urgency_pressure",
            "personal_info_request",
        ]

        for pattern in expected_patterns:
            assert pattern in detector.red_flag_patterns
            assert isinstance(detector.red_flag_patterns[pattern], list)
            assert len(detector.red_flag_patterns[pattern]) > 0

    @pytest.mark.asyncio
    async def test_analyze_job_success(
        self, fake_job_detector_with_openai, sample_job_data
    ):
        """Başarılı job analizi testi"""
        detector = fake_job_detector_with_openai

        # Mock AI analysis
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = (
            '{"is_fake": false, "confidence": 0.9, "reasons": ["Legitimate company"], "risk_score": 0.1}'
        )
        detector.client.chat.completions.create.return_value = mock_response

        result = await detector.analyze_job(sample_job_data)

        assert isinstance(result, FakeJobAnalysis)
        assert result.job_id == "job123"
        assert result.is_fake is False
        assert result.confidence == 0.9
        assert result.risk_score == 0.1
        assert len(result.reasons) > 0

    @pytest.mark.asyncio
    async def test_analyze_fake_job(
        self, fake_job_detector_with_openai, sample_fake_job_data
    ):
        """Fake job analizi testi"""
        detector = fake_job_detector_with_openai

        # Mock AI analysis for fake job
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = (
            '{"is_fake": true, "confidence": 0.95, "reasons": ["Unrealistic salary", "Suspicious contact"], "risk_score": 0.9}'
        )
        detector.client.chat.completions.create.return_value = mock_response

        result = await detector.analyze_job(sample_fake_job_data)

        assert isinstance(result, FakeJobAnalysis)
        assert result.job_id == "fake_job123"
        assert result.is_fake is True
        assert result.confidence == 0.95
        assert result.risk_score == 0.9
        assert len(result.reasons) > 0

    @pytest.mark.asyncio
    async def test_analyze_job_without_openai(
        self, fake_job_detector_without_openai, sample_job_data
    ):
        """OpenAI olmadan job analizi testi"""
        detector = fake_job_detector_without_openai

        result = await detector.analyze_job(sample_job_data)

        assert isinstance(result, FakeJobAnalysis)
        assert result.job_id == "job123"
        # Should still perform rule-based analysis
        assert hasattr(result, "is_fake")
        assert hasattr(result, "confidence")
        assert hasattr(result, "risk_score")

    @pytest.mark.asyncio
    async def test_analyze_job_error(
        self, fake_job_detector_with_openai, sample_job_data
    ):
        """Job analizi hatası testi"""
        detector = fake_job_detector_with_openai

        # Mock AI error
        detector.client.chat.completions.create.side_effect = Exception(
            "OpenAI API error"
        )

        result = await detector.analyze_job(sample_job_data)

        assert isinstance(result, FakeJobAnalysis)
        assert result.job_id == "job123"
        assert result.is_fake is False  # Default to safe
        assert result.confidence == 0.0
        assert result.risk_score == 0.5  # Default risk score
        assert "OpenAI API error" in result.reasons[0]

    def test_analyze_with_rules_legitimate_job(
        self, fake_job_detector_with_openai, sample_job_data
    ):
        """Rule-based analizi - legitimate job testi"""
        detector = fake_job_detector_with_openai

        result = detector._analyze_with_rules(sample_job_data)

        assert isinstance(result, dict)
        assert "red_flags" in result
        assert "risk_score" in result
        assert "confidence" in result
        assert result["risk_score"] < 0.5  # Should be low risk

    def test_analyze_with_rules_fake_job(
        self, fake_job_detector_with_openai, sample_fake_job_data
    ):
        """Rule-based analizi - fake job testi"""
        detector = fake_job_detector_with_openai

        result = detector._analyze_with_rules(sample_fake_job_data)

        assert isinstance(result, dict)
        assert "red_flags" in result
        assert "risk_score" in result
        assert "confidence" in result
        assert result["risk_score"] > 0.5  # Should be high risk
        assert len(result["red_flags"]) > 0  # Should detect red flags

    @pytest.mark.asyncio
    async def test_analyze_with_ai_success(
        self, fake_job_detector_with_openai, sample_job_data
    ):
        """AI analizi başarılı testi"""
        detector = fake_job_detector_with_openai

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = (
            '{"is_fake": false, "confidence": 0.9, "reasons": ["Legitimate"], "risk_score": 0.1}'
        )
        detector.client.chat.completions.create.return_value = mock_response

        result = await detector._analyze_with_ai(sample_job_data)

        assert isinstance(result, dict)
        assert result["is_fake"] is False
        assert result["confidence"] == 0.9
        assert result["risk_score"] == 0.1
        assert len(result["reasons"]) > 0

    @pytest.mark.asyncio
    async def test_analyze_with_ai_error(
        self, fake_job_detector_with_openai, sample_job_data
    ):
        """AI analizi hatası testi"""
        detector = fake_job_detector_with_openai

        detector.client.chat.completions.create.side_effect = Exception("AI error")

        result = await detector._analyze_with_ai(sample_job_data)

        assert result is None

    @pytest.mark.asyncio
    async def test_analyze_with_ai_invalid_json(
        self, fake_job_detector_with_openai, sample_job_data
    ):
        """AI analizi invalid JSON testi"""
        detector = fake_job_detector_with_openai

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "invalid json"
        detector.client.chat.completions.create.return_value = mock_response

        result = await detector._analyze_with_ai(sample_job_data)

        assert result is None

    def test_combine_analysis(self, fake_job_detector_with_openai):
        """Analiz sonuçlarını birleştirme testi"""
        detector = fake_job_detector_with_openai

        rule_results = {
            "red_flags": ["unrealistic_salary"],
            "risk_score": 0.7,
            "confidence": 0.8,
        }

        ai_results = {
            "is_fake": True,
            "confidence": 0.9,
            "reasons": ["AI detected suspicious patterns"],
            "risk_score": 0.8,
        }

        result = detector._combine_analysis("job123", {}, rule_results, ai_results)

        assert isinstance(result, FakeJobAnalysis)
        assert result.job_id == "job123"
        assert result.is_fake is True
        assert result.confidence > 0.8  # Should be high confidence
        assert result.risk_score > 0.7  # Should be high risk
        assert len(result.reasons) > 0

    def test_combine_analysis_no_ai(self, fake_job_detector_with_openai):
        """AI sonucu olmadan analiz birleştirme testi"""
        detector = fake_job_detector_with_openai

        rule_results = {
            "red_flags": ["unrealistic_salary"],
            "risk_score": 0.7,
            "confidence": 0.8,
        }

        result = detector._combine_analysis("job123", {}, rule_results, None)

        assert isinstance(result, FakeJobAnalysis)
        assert result.job_id == "job123"
        assert result.is_fake is True  # High risk from rules
        assert result.confidence == 0.8
        assert result.risk_score == 0.7

    @pytest.mark.asyncio
    async def test_log_analysis(self, fake_job_detector_with_openai):
        """Analiz loglama testi"""
        detector = fake_job_detector_with_openai

        analysis = FakeJobAnalysis(
            job_id="job123",
            is_fake=True,
            confidence=0.9,
            risk_score=0.8,
            reasons=["Test reason"],
            analysis_timestamp="2023-01-01T00:00:00Z",
        )

        # Mock database operations
        with patch("services.fake_job_detector.get_db") as mock_get_db:
            mock_db = Mock()
            mock_db.fake_job_analyses = Mock()
            mock_db.fake_job_analyses.insert_one = AsyncMock()
            mock_get_db.return_value = mock_db

            await detector._log_analysis(analysis)

            mock_db.fake_job_analyses.insert_one.assert_called_once()

    def test_create_error_analysis(self, fake_job_detector_with_openai):
        """Error analizi oluşturma testi"""
        detector = fake_job_detector_with_openai

        result = detector._create_error_analysis("job123", "Test error")

        assert isinstance(result, FakeJobAnalysis)
        assert result.job_id == "job123"
        assert result.is_fake is False  # Default to safe
        assert result.confidence == 0.0
        assert result.risk_score == 0.5  # Default risk score
        assert "Test error" in result.reasons[0]

    def test_detect_unrealistic_salary(self, fake_job_detector_with_openai):
        """Unrealistic salary tespiti testi"""
        detector = fake_job_detector_with_openai

        # Test unrealistic salary patterns
        fake_jobs = [
            {"salary_range": "$5000 per week"},
            {"salary_range": "earn $4000+ weekly"},
            {"salary_range": "$3000 per day"},
        ]

        for job in fake_jobs:
            result = detector._analyze_with_rules(job)
            assert result["risk_score"] > 0.5
            assert "unrealistic_salary" in result["red_flags"]

    def test_detect_vague_description(self, fake_job_detector_with_openai):
        """Vague description tespiti testi"""
        detector = fake_job_detector_with_openai

        # Test vague job descriptions
        fake_jobs = [
            {"description": "work from home easy money"},
            {"description": "no experience required flexible hours"},
            {"description": "part time full time"},
        ]

        for job in fake_jobs:
            result = detector._analyze_with_rules(job)
            assert result["risk_score"] > 0.5
            assert "vague_job_description" in result["red_flags"]

    def test_detect_suspicious_contact(self, fake_job_detector_with_openai):
        """Suspicious contact tespiti testi"""
        detector = fake_job_detector_with_openai

        # Test suspicious contact patterns
        fake_jobs = [
            {"description": "contact via whatsapp"},
            {"description": "text us at +1234567890"},
            {"description": "telegram @username"},
        ]

        for job in fake_jobs:
            result = detector._analyze_with_rules(job)
            assert result["risk_score"] > 0.5
            assert "suspicious_contact" in result["red_flags"]

    def test_service_methods_exist(self, fake_job_detector_with_openai):
        """Service metodlarının varlığını test et"""
        detector = fake_job_detector_with_openai

        required_methods = [
            "_initialize_openai",
            "analyze_job",
            "_analyze_with_rules",
            "_analyze_with_ai",
            "_combine_analysis",
            "_log_analysis",
            "_create_error_analysis",
        ]

        for method in required_methods:
            assert hasattr(detector, method)
            assert callable(getattr(detector, method))

    @pytest.mark.asyncio
    async def test_service_integration(
        self, fake_job_detector_with_openai, sample_job_data, sample_fake_job_data
    ):
        """Service integration testi"""
        detector = fake_job_detector_with_openai

        # Mock AI responses
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = (
            '{"is_fake": false, "confidence": 0.9, "reasons": ["Legitimate"], "risk_score": 0.1}'
        )
        detector.client.chat.completions.create.return_value = mock_response

        # Test legitimate job
        legitimate_result = await detector.analyze_job(sample_job_data)
        assert legitimate_result.is_fake is False
        assert legitimate_result.confidence > 0.8

        # Test fake job
        mock_response.choices[0].message.content = (
            '{"is_fake": true, "confidence": 0.95, "reasons": ["Fake"], "risk_score": 0.9}'
        )
        fake_result = await detector.analyze_job(sample_fake_job_data)
        assert fake_result.is_fake is True
        assert fake_result.confidence > 0.8
