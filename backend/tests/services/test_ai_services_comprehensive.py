import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.services.ai_application_service import AIApplicationService
from backend.services.ai_job_matching_service import AIJobMatchingService
from backend.services.salary_prediction_service import SalaryPredictionService
from backend.services.resume_parser_service import ResumeParserService

class TestAIApplicationService:
    """Test AI Application Service functionality."""
    
    @pytest.fixture
    def ai_service(self):
        """Create AI application service instance."""
        return AIApplicationService()
    
    @pytest.fixture
    def sample_job_data(self):
        """Sample job data for testing."""
        return {
            "title": "Senior Python Developer",
            "company": "TechCorp",
            "description": "We are looking for a senior Python developer with 5+ years of experience in FastAPI, Django, and MongoDB.",
            "requirements": "Python, FastAPI, Django, MongoDB, Docker, AWS",
            "salary_range": "$80,000 - $120,000",
            "location": "Remote",
            "job_type": "Full-time"
        }
    
    @pytest.fixture
    def sample_user_data(self):
        """Sample user data for testing."""
        return {
            "full_name": "John Doe",
            "email": "john.doe@example.com",
            "experience_years": 6,
            "skills": ["Python", "FastAPI", "Django", "MongoDB", "Docker"],
            "current_position": "Python Developer",
            "education": "Bachelor's in Computer Science"
        }
    
    def test_ai_service_initialization(self, ai_service):
        """Test AI service initialization."""
        assert ai_service is not None
        assert hasattr(ai_service, 'generate_cover_letter')
        assert hasattr(ai_service, 'analyze_job_fit')
    
    @patch('backend.services.ai_application_service.openai.ChatCompletion.create')
    def test_generate_cover_letter(self, mock_openai, ai_service, sample_job_data, sample_user_data):
        """Test cover letter generation."""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Dear Hiring Manager, I am excited to apply..."
        mock_openai.return_value = mock_response
        
        result = ai_service.generate_cover_letter(sample_job_data, sample_user_data)
        
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
        mock_openai.assert_called_once()
    
    @patch('backend.services.ai_application_service.openai.ChatCompletion.create')
    def test_analyze_job_fit(self, mock_openai, ai_service, sample_job_data, sample_user_data):
        """Test job fit analysis."""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"fit_score": 85, "strengths": ["Python experience"], "weaknesses": ["AWS"]}'
        mock_openai.return_value = mock_response
        
        result = ai_service.analyze_job_fit(sample_job_data, sample_user_data)
        
        assert result is not None
        assert "fit_score" in result
        assert "strengths" in result
        assert "weaknesses" in result
        mock_openai.assert_called_once()
    
    def test_generate_cover_letter_with_invalid_data(self, ai_service):
        """Test cover letter generation with invalid data."""
        with pytest.raises(Exception):
            ai_service.generate_cover_letter({}, {})
    
    def test_analyze_job_fit_with_invalid_data(self, ai_service):
        """Test job fit analysis with invalid data."""
        with pytest.raises(Exception):
            ai_service.analyze_job_fit({}, {})

class TestAIJobMatchingService:
    """Test AI Job Matching Service functionality."""
    
    @pytest.fixture
    def matching_service(self):
        """Create AI job matching service instance."""
        return AIJobMatchingService()
    
    @pytest.fixture
    def sample_jobs(self):
        """Sample jobs for testing."""
        return [
            {
                "title": "Python Developer",
                "company": "TechCorp",
                "description": "Python development role",
                "requirements": "Python, FastAPI",
                "salary_range": "$60,000 - $80,000"
            },
            {
                "title": "Senior Python Developer",
                "company": "StartupXYZ",
                "description": "Senior Python development role",
                "requirements": "Python, Django, MongoDB",
                "salary_range": "$80,000 - $120,000"
            }
        ]
    
    @pytest.fixture
    def sample_user_profile(self):
        """Sample user profile for testing."""
        return {
            "skills": ["Python", "FastAPI", "Django"],
            "experience_years": 5,
            "preferred_salary": "$70,000",
            "preferred_location": "Remote"
        }
    
    def test_matching_service_initialization(self, matching_service):
        """Test matching service initialization."""
        assert matching_service is not None
        assert hasattr(matching_service, 'find_matching_jobs')
        assert hasattr(matching_service, 'calculate_job_score')
    
    def test_calculate_job_score(self, matching_service, sample_jobs, sample_user_profile):
        """Test job score calculation."""
        score = matching_service.calculate_job_score(sample_jobs[0], sample_user_profile)
        
        assert isinstance(score, (int, float))
        assert score >= 0
        assert score <= 100
    
    def test_find_matching_jobs(self, matching_service, sample_jobs, sample_user_profile):
        """Test finding matching jobs."""
        matches = matching_service.find_matching_jobs(sample_jobs, sample_user_profile, limit=5)
        
        assert isinstance(matches, list)
        assert len(matches) <= 5
        for match in matches:
            assert "job" in match
            assert "score" in match
            assert isinstance(match["score"], (int, float))
    
    def test_find_matching_jobs_empty_list(self, matching_service, sample_user_profile):
        """Test finding matching jobs with empty job list."""
        matches = matching_service.find_matching_jobs([], sample_user_profile)
        
        assert isinstance(matches, list)
        assert len(matches) == 0
    
    def test_calculate_job_score_with_missing_data(self, matching_service):
        """Test job score calculation with missing data."""
        score = matching_service.calculate_job_score({}, {})
        
        assert isinstance(score, (int, float))
        assert score >= 0

class TestSalaryPredictionService:
    """Test Salary Prediction Service functionality."""
    
    @pytest.fixture
    def salary_service(self):
        """Create salary prediction service instance."""
        return SalaryPredictionService()
    
    @pytest.fixture
    def sample_job_data(self):
        """Sample job data for salary prediction."""
        return {
            "title": "Python Developer",
            "company": "TechCorp",
            "location": "San Francisco",
            "experience_level": "Mid-level",
            "job_type": "Full-time",
            "requirements": "Python, FastAPI, MongoDB"
        }
    
    def test_salary_service_initialization(self, salary_service):
        """Test salary service initialization."""
        assert salary_service is not None
        assert hasattr(salary_service, 'predict_salary')
        assert hasattr(salary_service, 'get_salary_range')
    
    def test_predict_salary(self, salary_service, sample_job_data):
        """Test salary prediction."""
        prediction = salary_service.predict_salary(sample_job_data)
        
        assert prediction is not None
        assert "min_salary" in prediction
        assert "max_salary" in prediction
        assert "currency" in prediction
        assert prediction["min_salary"] > 0
        assert prediction["max_salary"] > prediction["min_salary"]
    
    def test_get_salary_range(self, salary_service, sample_job_data):
        """Test salary range calculation."""
        salary_range = salary_service.get_salary_range(sample_job_data)
        
        assert isinstance(salary_range, str)
        assert "$" in salary_range or "€" in salary_range or "£" in salary_range
    
    def test_predict_salary_with_invalid_data(self, salary_service):
        """Test salary prediction with invalid data."""
        prediction = salary_service.predict_salary({})
        
        assert prediction is not None
        assert "min_salary" in prediction
        assert "max_salary" in prediction
    
    def test_predict_salary_different_locations(self, salary_service):
        """Test salary prediction for different locations."""
        job_data_sf = {"title": "Python Developer", "location": "San Francisco"}
        job_data_ny = {"title": "Python Developer", "location": "New York"}
        
        prediction_sf = salary_service.predict_salary(job_data_sf)
        prediction_ny = salary_service.predict_salary(job_data_ny)
        
        assert prediction_sf != prediction_ny

class TestResumeParserService:
    """Test Resume Parser Service functionality."""
    
    @pytest.fixture
    def parser_service(self):
        """Create resume parser service instance."""
        return ResumeParserService()
    
    @pytest.fixture
    def sample_resume_text(self):
        """Sample resume text for testing."""
        return """
        JOHN DOE
        Software Engineer
        john.doe@example.com
        
        EXPERIENCE
        Senior Python Developer at TechCorp (2020-2023)
        - Developed web applications using FastAPI and Django
        - Worked with MongoDB and PostgreSQL databases
        - Led team of 3 developers
        
        Python Developer at StartupXYZ (2018-2020)
        - Built REST APIs using Flask
        - Implemented CI/CD pipelines
        
        SKILLS
        Python, FastAPI, Django, Flask, MongoDB, PostgreSQL, Docker, AWS
        
        EDUCATION
        Bachelor's in Computer Science, University of Technology (2018)
        """
    
    def test_parser_service_initialization(self, parser_service):
        """Test parser service initialization."""
        assert parser_service is not None
        assert hasattr(parser_service, 'parse_resume')
        assert hasattr(parser_service, 'extract_skills')
    
    def test_parse_resume(self, parser_service, sample_resume_text):
        """Test resume parsing."""
        parsed_data = parser_service.parse_resume(sample_resume_text)
        
        assert parsed_data is not None
        assert "name" in parsed_data
        assert "email" in parsed_data
        assert "skills" in parsed_data
        assert "experience" in parsed_data
        assert "education" in parsed_data
    
    def test_extract_skills(self, parser_service, sample_resume_text):
        """Test skills extraction."""
        skills = parser_service.extract_skills(sample_resume_text)
        
        assert isinstance(skills, list)
        assert len(skills) > 0
        assert "Python" in skills
        assert "FastAPI" in skills
    
    def test_parse_resume_empty_text(self, parser_service):
        """Test resume parsing with empty text."""
        parsed_data = parser_service.parse_resume("")
        
        assert parsed_data is not None
        assert "name" in parsed_data
        assert "email" in parsed_data
        assert "skills" in parsed_data
    
    def test_extract_skills_empty_text(self, parser_service):
        """Test skills extraction with empty text."""
        skills = parser_service.extract_skills("")
        
        assert isinstance(skills, list)
        assert len(skills) == 0
    
    def test_parse_resume_with_special_characters(self, parser_service):
        """Test resume parsing with special characters."""
        resume_text = "John Doe & Associates\nEmail: john.doe@example.com\nSkills: Python, C++, C#"
        
        parsed_data = parser_service.parse_resume(resume_text)
        
        assert parsed_data is not None
        assert "name" in parsed_data
        assert "email" in parsed_data
        assert "skills" in parsed_data 