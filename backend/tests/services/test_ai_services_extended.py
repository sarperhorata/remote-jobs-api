import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
import json

class TestAIApplicationServiceExtended:
    """Extended tests for AI Application Service to increase coverage"""
    
    @patch('services.ai_application_service.OpenAI')
    def test_service_initialization(self, mock_openai):
        """Test AI Application Service initialization"""
        from services.ai_application_service import AIApplicationService
        
        service = AIApplicationService()
        assert service is not None
        assert hasattr(service, 'openai_client')
    
    @patch('services.ai_application_service.OpenAI')
    def test_generate_cover_letter_success(self, mock_openai):
        """Test successful cover letter generation"""
        from services.ai_application_service import AIApplicationService
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated cover letter content"
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        service = AIApplicationService()
        result = service.generate_cover_letter(
            job_title="Python Developer",
            company_name="Tech Corp",
            resume_summary="Experienced Python developer",
            job_description="We are looking for a Python developer"
        )
        
        assert result["success"] is True
        assert "cover_letter" in result
    
    @patch('services.ai_application_service.OpenAI')
    def test_generate_cover_letter_error(self, mock_openai):
        """Test cover letter generation with error"""
        from services.ai_application_service import AIApplicationService
        
        mock_openai.return_value.chat.completions.create.side_effect = Exception("API Error")
        
        service = AIApplicationService()
        result = service.generate_cover_letter(
            job_title="Python Developer",
            company_name="Tech Corp",
            resume_summary="Experience",
            job_description="Job description"
        )
        
        assert result["success"] is False
        assert "error" in result
    
    @patch('services.ai_application_service.OpenAI')
    def test_analyze_job_requirements(self, mock_openai):
        """Test job requirements analysis"""
        from services.ai_application_service import AIApplicationService
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "required_skills": ["Python", "Django"],
            "preferred_skills": ["React", "AWS"],
            "experience_level": "mid",
            "key_responsibilities": ["Develop web applications"]
        })
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        service = AIApplicationService()
        result = service.analyze_job_requirements("We are looking for a Python developer with Django experience")
        
        assert result["success"] is True
        assert "required_skills" in result["analysis"]
    
    @patch('services.ai_application_service.OpenAI')
    def test_optimize_resume_for_job(self, mock_openai):
        """Test resume optimization for specific job"""
        from services.ai_application_service import AIApplicationService
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "optimized_summary": "Optimized resume summary",
            "suggested_keywords": ["Python", "Django", "API"],
            "improvement_suggestions": ["Add more specific achievements"]
        })
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        service = AIApplicationService()
        result = service.optimize_resume_for_job(
            resume_content="Current resume content",
            job_description="Job description",
            job_requirements={"skills": ["Python", "Django"]}
        )
        
        assert result["success"] is True
        assert "optimized_summary" in result["optimization"]
    
    @patch('services.ai_application_service.OpenAI')
    def test_generate_interview_preparation(self, mock_openai):
        """Test interview preparation generation"""
        from services.ai_application_service import AIApplicationService
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "common_questions": ["Tell me about your Python experience"],
            "technical_questions": ["Explain Django ORM"],
            "preparation_tips": ["Review Python fundamentals"]
        })
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        service = AIApplicationService()
        result = service.generate_interview_preparation(
            job_title="Python Developer",
            company_name="Tech Corp",
            job_description="Python developer role"
        )
        
        assert result["success"] is True
        assert "common_questions" in result["preparation"]
    
    @patch('services.ai_application_service.OpenAI')
    def test_analyze_application_strength(self, mock_openai):
        """Test application strength analysis"""
        from services.ai_application_service import AIApplicationService
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "strength_score": 85,
            "strengths": ["Strong Python skills", "Relevant experience"],
            "weaknesses": ["Limited cloud experience"],
            "improvement_suggestions": ["Add AWS certification"]
        })
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        service = AIApplicationService()
        result = service.analyze_application_strength(
            resume_content="Resume content",
            job_description="Job description",
            cover_letter="Cover letter content"
        )
        
        assert result["success"] is True
        assert "strength_score" in result["analysis"]
    
    @patch('services.ai_application_service.OpenAI')
    def test_generate_follow_up_email(self, mock_openai):
        """Test follow-up email generation"""
        from services.ai_application_service import AIApplicationService
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Professional follow-up email content"
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        service = AIApplicationService()
        result = service.generate_follow_up_email(
            company_name="Tech Corp",
            position="Python Developer",
            application_date="2024-01-15",
            interviewer_name="John Doe"
        )
        
        assert result["success"] is True
        assert "email_content" in result
    
    @patch('services.ai_application_service.OpenAI')
    def test_analyze_salary_negotiation(self, mock_openai):
        """Test salary negotiation analysis"""
        from services.ai_application_service import AIApplicationService
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "market_rate": 95000,
            "negotiation_range": [90000, 110000],
            "negotiation_strategies": ["Highlight unique skills"],
            "counter_offer_suggestions": ["Request 105000 with benefits"]
        })
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        service = AIApplicationService()
        result = service.analyze_salary_negotiation(
            job_title="Python Developer",
            location="San Francisco",
            experience_years=5,
            offered_salary=90000
        )
        
        assert result["success"] is True
        assert "market_rate" in result["analysis"]


class TestAIJobMatchingServiceExtended:
    """Extended tests for AI Job Matching Service to increase coverage"""
    
    def test_service_initialization(self):
        """Test AI Job Matching Service initialization"""
        from services.ai_job_matching_service import AIJobMatchingService
        
        service = AIJobMatchingService()
        assert service is not None
    
    @patch('services.ai_job_matching_service.OpenAI')
    def test_analyze_job_compatibility(self, mock_openai):
        """Test job compatibility analysis"""
        from services.ai_job_matching_service import AIJobMatchingService
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "compatibility_score": 85,
            "matching_skills": ["Python", "Django"],
            "missing_skills": ["AWS"],
            "recommendations": ["Learn AWS basics"]
        })
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        service = AIJobMatchingService()
        result = service.analyze_job_compatibility(
            resume_skills=["Python", "Django", "SQL"],
            job_requirements=["Python", "Django", "AWS", "React"]
        )
        
        assert result["success"] is True
        assert "compatibility_score" in result["analysis"]
    
    @patch('services.ai_job_matching_service.OpenAI')
    def test_generate_career_path_suggestions(self, mock_openai):
        """Test career path suggestions generation"""
        from services.ai_job_matching_service import AIJobMatchingService
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "career_paths": [
                {"title": "Senior Python Developer", "steps": ["Gain leadership experience"]},
                {"title": "DevOps Engineer", "steps": ["Learn CI/CD", "Study cloud platforms"]}
            ],
            "timeline": "2-3 years",
            "skill_gaps": ["Leadership", "DevOps tools"]
        })
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        service = AIJobMatchingService()
        result = service.generate_career_path_suggestions(
            current_role="Python Developer",
            experience_years=3,
            skills=["Python", "Django", "SQL"]
        )
        
        assert result["success"] is True
        assert "career_paths" in result["suggestions"]
    
    @patch('services.ai_job_matching_service.OpenAI')
    def test_analyze_market_trends(self, mock_openai):
        """Test market trends analysis"""
        from services.ai_job_matching_service import AIJobMatchingService
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "trending_skills": ["AI/ML", "Cloud Computing", "DevOps"],
            "salary_trends": {"Python": "increasing", "Java": "stable"},
            "demand_forecast": {"Python": "high", "PHP": "declining"},
            "emerging_roles": ["AI Engineer", "DevOps Engineer"]
        })
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        service = AIJobMatchingService()
        result = service.analyze_market_trends(
            location="San Francisco",
            job_category="Software Development"
        )
        
        assert result["success"] is True
        assert "trending_skills" in result["trends"]
    
    @patch('services.ai_job_matching_service.OpenAI')
    def test_generate_skill_development_plan(self, mock_openai):
        """Test skill development plan generation"""
        from services.ai_job_matching_service import AIJobMatchingService
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "learning_path": [
                {"skill": "AWS", "resources": ["AWS documentation", "Online courses"]},
                {"skill": "React", "resources": ["React docs", "Tutorials"]}
            ],
            "timeline": "6 months",
            "priority_order": ["AWS", "React", "Docker"]
        })
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        service = AIJobMatchingService()
        result = service.generate_skill_development_plan(
            current_skills=["Python", "Django"],
            target_skills=["AWS", "React", "Docker"],
            time_available="6 months"
        )
        
        assert result["success"] is True
        assert "learning_path" in result["plan"]
    
    @patch('services.ai_job_matching_service.OpenAI')
    def test_analyze_company_culture_fit(self, mock_openai):
        """Test company culture fit analysis"""
        from services.ai_job_matching_service import AIJobMatchingService
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "culture_fit_score": 78,
            "matching_aspects": ["Remote work", "Learning culture"],
            "potential_challenges": ["Fast-paced environment"],
            "recommendations": ["Ask about work-life balance"]
        })
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        service = AIJobMatchingService()
        result = service.analyze_company_culture_fit(
            candidate_preferences={"remote_work": True, "learning": True},
            company_culture={"remote_friendly": True, "fast_paced": True}
        )
        
        assert result["success"] is True
        assert "culture_fit_score" in result["analysis"]
    
    @patch('services.ai_job_matching_service.OpenAI')
    def test_generate_job_search_strategy(self, mock_openai):
        """Test job search strategy generation"""
        from services.ai_job_matching_service import AIJobMatchingService
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "target_companies": ["Google", "Microsoft", "Startups"],
            "search_keywords": ["Python Developer", "Backend Engineer"],
            "networking_opportunities": ["Tech meetups", "LinkedIn connections"],
            "application_timeline": "3 months"
        })
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        service = AIJobMatchingService()
        result = service.generate_job_search_strategy(
            target_role="Python Developer",
            location="San Francisco",
            experience_level="mid"
        )
        
        assert result["success"] is True
        assert "target_companies" in result["strategy"]


class TestAutoApplicationServiceExtended:
    """Extended tests for Auto Application Service to increase coverage"""
    
    def test_service_initialization(self):
        """Test Auto Application Service initialization"""
        from services.auto_application_service import AutoApplicationService
        
        service = AutoApplicationService()
        assert service is not None
    
    @patch('services.auto_application_service.requests.post')
    def test_submit_application_success(self, mock_post):
        """Test successful application submission"""
        from services.auto_application_service import AutoApplicationService
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "application_id": "app123"}
        mock_post.return_value = mock_response
        
        service = AutoApplicationService()
        result = service.submit_application(
            job_url="https://example.com/job",
            form_data={"name": "John Doe", "email": "john@example.com"},
            resume_path="/path/to/resume.pdf"
        )
        
        assert result["success"] is True
        assert "application_id" in result
    
    @patch('services.auto_application_service.requests.post')
    def test_submit_application_error(self, mock_post):
        """Test application submission with error"""
        from services.auto_application_service import AutoApplicationService
        
        mock_post.side_effect = Exception("Network error")
        
        service = AutoApplicationService()
        result = service.submit_application(
            job_url="https://example.com/job",
            form_data={"name": "John Doe"},
            resume_path="/path/to/resume.pdf"
        )
        
        assert result["success"] is False
        assert "error" in result
    
    @patch('services.auto_application_service.requests.get')
    def test_scrape_application_form(self, mock_get):
        """Test application form scraping"""
        from services.auto_application_service import AutoApplicationService
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <form>
            <input name="name" type="text" />
            <input name="email" type="email" />
            <input name="resume" type="file" />
        </form>
        """
        mock_get.return_value = mock_response
        
        service = AutoApplicationService()
        result = service.scrape_application_form("https://example.com/apply")
        
        assert result["success"] is True
        assert "form_fields" in result
        assert "name" in result["form_fields"]
    
    def test_validate_form_data(self):
        """Test form data validation"""
        from services.auto_application_service import AutoApplicationService
        
        service = AutoApplicationService()
        
        # Valid data
        valid_data = {"name": "John Doe", "email": "john@example.com"}
        result = service.validate_form_data(valid_data)
        assert result["valid"] is True
        
        # Invalid data
        invalid_data = {"name": "", "email": "invalid-email"}
        result = service.validate_form_data(invalid_data)
        assert result["valid"] is False
        assert "errors" in result
    
    @patch('services.auto_application_service.requests.post')
    def test_track_application_status(self, mock_post):
        """Test application status tracking"""
        from services.auto_application_service import AutoApplicationService
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "under_review"}
        mock_post.return_value = mock_response
        
        service = AutoApplicationService()
        result = service.track_application_status("app123", "https://example.com/track")
        
        assert result["success"] is True
        assert result["status"] == "under_review"
    
    def test_generate_application_summary(self):
        """Test application summary generation"""
        from services.auto_application_service import AutoApplicationService
        
        service = AutoApplicationService()
        applications = [
            {"company": "Tech Corp", "position": "Python Developer", "status": "applied"},
            {"company": "Startup Inc", "position": "Backend Engineer", "status": "interviewed"}
        ]
        
        summary = service.generate_application_summary(applications)
        
        assert "total_applications" in summary
        assert "status_breakdown" in summary
        assert summary["total_applications"] == 2
    
    @patch('services.auto_application_service.requests.get')
    def test_check_job_availability(self, mock_get):
        """Test job availability checking"""
        from services.auto_application_service import AutoApplicationService
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Job is still available"
        mock_get.return_value = mock_response
        
        service = AutoApplicationService()
        result = service.check_job_availability("https://example.com/job")
        
        assert result["available"] is True
    
    def test_optimize_application_timing(self):
        """Test application timing optimization"""
        from services.auto_application_service import AutoApplicationService
        
        service = AutoApplicationService()
        result = service.optimize_application_timing(
            job_posted_date="2024-01-15",
            company_timezone="PST"
        )
        
        assert "optimal_time" in result
        assert "reasoning" in result
    
    @patch('services.auto_application_service.requests.post')
    def test_bulk_application_submission(self, mock_post):
        """Test bulk application submission"""
        from services.auto_application_service import AutoApplicationService
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response
        
        service = AutoApplicationService()
        jobs = [
            {"url": "https://example.com/job1", "title": "Python Developer"},
            {"url": "https://example.com/job2", "title": "Backend Engineer"}
        ]
        
        result = service.bulk_application_submission(
            jobs=jobs,
            form_data={"name": "John Doe", "email": "john@example.com"},
            resume_path="/path/to/resume.pdf"
        )
        
        assert result["success"] is True
        assert "submitted_count" in result
        assert "failed_count" in result


class TestJobScrapingServiceExtended:
    """Extended tests for Job Scraping Service to increase coverage"""
    
    def test_service_initialization(self):
        """Test Job Scraping Service initialization"""
        from services.job_scraping_service import JobScrapingService
        
        service = JobScrapingService()
        assert service is not None
    
    @patch('services.job_scraping_service.requests.get')
    def test_scrape_job_details(self, mock_get):
        """Test job details scraping"""
        from services.job_scraping_service import JobScrapingService
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <div class="job-title">Python Developer</div>
        <div class="company">Tech Corp</div>
        <div class="location">Remote</div>
        <div class="description">We are looking for a Python developer</div>
        """
        mock_get.return_value = mock_response
        
        service = JobScrapingService()
        result = service.scrape_job_details("https://example.com/job")
        
        assert result["success"] is True
        assert "title" in result["job_data"]
        assert "company" in result["job_data"]
    
    @patch('services.job_scraping_service.requests.get')
    def test_scrape_job_details_error(self, mock_get):
        """Test job details scraping with error"""
        from services.job_scraping_service import JobScrapingService
        
        mock_get.side_effect = Exception("Network error")
        
        service = JobScrapingService()
        result = service.scrape_job_details("https://example.com/job")
        
        assert result["success"] is False
        assert "error" in result
    
    def test_extract_job_information(self):
        """Test job information extraction from HTML"""
        from services.job_scraping_service import JobScrapingService
        
        service = JobScrapingService()
        html_content = """
        <div class="job-title">Senior Python Developer</div>
        <div class="company">Tech Corp</div>
        <div class="salary">$100,000 - $150,000</div>
        <div class="requirements">Python, Django, AWS</div>
        """
        
        result = service.extract_job_information(html_content)
        
        assert "title" in result
        assert "company" in result
        assert "salary" in result
        assert "requirements" in result
    
    def test_parse_salary_information(self):
        """Test salary information parsing"""
        from services.job_scraping_service import JobScrapingService
        
        service = JobScrapingService()
        
        # Test various salary formats
        salary_texts = [
            "$100,000 - $150,000",
            "100k-150k",
            "$100K+",
            "Competitive salary"
        ]
        
        for salary_text in salary_texts:
            result = service.parse_salary_information(salary_text)
            assert "min_salary" in result or "salary_range" in result
    
    def test_extract_skills_from_description(self):
        """Test skills extraction from job description"""
        from services.job_scraping_service import JobScrapingService
        
        service = JobScrapingService()
        description = """
        We are looking for a Python developer with experience in:
        - Python 3.x
        - Django framework
        - PostgreSQL
        - AWS services
        - Git version control
        """
        
        skills = service.extract_skills_from_description(description)
        
        assert "Python" in skills
        assert "Django" in skills
        assert "PostgreSQL" in skills
        assert "AWS" in skills
    
    def test_validate_job_data(self):
        """Test job data validation"""
        from services.job_scraping_service import JobScrapingService
        
        service = JobScrapingService()
        
        # Valid data
        valid_data = {
            "title": "Python Developer",
            "company": "Tech Corp",
            "location": "Remote",
            "description": "Job description"
        }
        result = service.validate_job_data(valid_data)
        assert result["valid"] is True
        
        # Invalid data
        invalid_data = {"title": "", "company": ""}
        result = service.validate_job_data(invalid_data)
        assert result["valid"] is False
        assert "errors" in result
    
    @patch('services.job_scraping_service.requests.get')
    def test_scrape_multiple_jobs(self, mock_get):
        """Test multiple jobs scraping"""
        from services.job_scraping_service import JobScrapingService
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <div class="job-listing">
            <div class="job-title">Python Developer</div>
            <div class="company">Tech Corp</div>
        </div>
        <div class="job-listing">
            <div class="job-title">Backend Engineer</div>
            <div class="company">Startup Inc</div>
        </div>
        """
        mock_get.return_value = mock_response
        
        service = JobScrapingService()
        result = service.scrape_multiple_jobs("https://example.com/jobs")
        
        assert result["success"] is True
        assert len(result["jobs"]) >= 1
    
    def test_clean_and_normalize_data(self):
        """Test data cleaning and normalization"""
        from services.job_scraping_service import JobScrapingService
        
        service = JobScrapingService()
        raw_data = {
            "title": "  Senior Python Developer  ",
            "company": "Tech Corp Inc.",
            "location": "San Francisco, CA",
            "salary": "$100,000 - $150,000 per year"
        }
        
        cleaned_data = service.clean_and_normalize_data(raw_data)
        
        assert cleaned_data["title"] == "Senior Python Developer"
        assert cleaned_data["company"] == "Tech Corp Inc"
        assert "San Francisco" in cleaned_data["location"]
        assert "100000" in str(cleaned_data["salary_min"])
    
    def test_detect_job_source(self):
        """Test job source detection"""
        from services.job_scraping_service import JobScrapingService
        
        service = JobScrapingService()
        
        urls = [
            "https://linkedin.com/jobs/view/123",
            "https://indeed.com/viewjob?jk=456",
            "https://glassdoor.com/Job/789",
            "https://company.com/careers/job"
        ]
        
        for url in urls:
            source = service.detect_job_source(url)
            assert source in ["LinkedIn", "Indeed", "Glassdoor", "Company Website", "Unknown"]
    
    def test_extract_application_deadline(self):
        """Test application deadline extraction"""
        from services.job_scraping_service import JobScrapingService
        
        service = JobScrapingService()
        description = """
        Application deadline: December 31, 2024
        Apply by: 2024-12-31
        Closing date: 31st Dec 2024
        """
        
        deadline = service.extract_application_deadline(description)
        assert deadline is not None
    
    def test_analyze_job_quality_score(self):
        """Test job quality score analysis"""
        from services.job_scraping_service import JobScrapingService
        
        service = JobScrapingService()
        job_data = {
            "title": "Senior Python Developer",
            "company": "Well-known Tech Corp",
            "description": "Comprehensive job description with requirements",
            "salary": "$120,000 - $180,000",
            "location": "San Francisco, CA"
        }
        
        quality_score = service.analyze_job_quality_score(job_data)
        assert 0 <= quality_score <= 100 