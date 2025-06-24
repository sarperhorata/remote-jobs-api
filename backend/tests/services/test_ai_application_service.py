import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
import aiohttp

from backend.services.ai_application_service import AIApplicationService

class TestAIApplicationService:
    """Test suite for AI Application Service"""
    
    @pytest.fixture
    async def ai_service(self):
        """Create AI application service instance"""
        async with AIApplicationService() as service:
            yield service
    
    @pytest.fixture
    def mock_job_url(self):
        """Mock job URL"""
        return "https://example.com/jobs/software-engineer"
    
    @pytest.fixture
    def mock_html_content(self):
        """Mock HTML content with application form"""
        return """
        <html>
            <body>
                <h1>Software Engineer - Tech Company</h1>
                <div class="company">Tech Company</div>
                <div class="description">
                    We are looking for a talented software engineer...
                </div>
                <form action="/apply" method="post">
                    <label for="first_name">First Name:</label>
                    <input type="text" id="first_name" name="first_name" required>
                    
                    <label for="last_name">Last Name:</label>
                    <input type="text" id="last_name" name="last_name" required>
                    
                    <label for="email">Email:</label>
                    <input type="email" id="email" name="email" required>
                    
                    <label for="cover_letter">Cover Letter:</label>
                    <textarea id="cover_letter" name="cover_letter" required></textarea>
                    
                    <label for="experience">Years of Experience:</label>
                    <select id="experience" name="experience">
                        <option value="0-1">0-1 years</option>
                        <option value="2-3">2-3 years</option>
                        <option value="4-5">4-5 years</option>
                        <option value="5+">5+ years</option>
                    </select>
                    
                    <label for="custom_question">Why do you want to work here?</label>
                    <textarea id="custom_question" name="custom_question"></textarea>
                    
                    <input type="submit" value="Apply Now">
                </form>
            </body>
        </html>
        """
    
    @pytest.fixture
    def mock_user_profile(self):
        """Mock user profile"""
        return {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "+1234567890",
            "location": "San Francisco, CA",
            "skills": ["Python", "JavaScript", "React", "Node.js", "SQL"],
            "work_experience": [
                {
                    "title": "Senior Software Engineer",
                    "company": "Previous Corp",
                    "years": 3,
                    "description": "Led development of web applications"
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science",
                    "field": "Computer Science",
                    "school": "University of Technology"
                }
            ],
            "salary_expectation": "$120,000",
            "availability": "2 weeks notice"
        }

    async def test_scrape_job_application_form_success(self, ai_service, mock_job_url, mock_html_content):
        """Test successful form scraping"""
        # Mock HTTP response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = mock_html_content
        
        with patch.object(ai_service.session, 'get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await ai_service.scrape_job_application_form(mock_job_url)
        
        assert "form_fields" in result
        assert "form_action" in result
        assert "application_flow" in result
        assert "job_details" in result
        
        # Check extracted fields
        fields = result["form_fields"]
        field_names = [field["name"] for field in fields]
        assert "first_name" in field_names
        assert "last_name" in field_names
        assert "email" in field_names
        assert "cover_letter" in field_names
        assert "experience" in field_names
        assert "custom_question" in field_names
        
        # Check field categorization
        first_name_field = next(f for f in fields if f["name"] == "first_name")
        assert first_name_field["category"] == "first_name"
        
        cover_letter_field = next(f for f in fields if f["name"] == "cover_letter")
        assert cover_letter_field["category"] == "cover_letter"
        
        custom_field = next(f for f in fields if f["name"] == "custom_question")
        assert custom_field["category"] == "custom_question"

    async def test_scrape_job_application_form_http_error(self, ai_service, mock_job_url):
        """Test form scraping with HTTP error"""
        # Mock HTTP error response
        mock_response = AsyncMock()
        mock_response.status = 404
        
        with patch.object(ai_service.session, 'get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(Exception) as exc_info:
                await ai_service.scrape_job_application_form(mock_job_url)
            
            assert "Failed to fetch job page" in str(exc_info.value)

    async def test_extract_field_info_various_types(self, ai_service):
        """Test field information extraction for various input types"""
        from bs4 import BeautifulSoup
        
        # Test text input
        html = '<input type="text" name="full_name" id="name" placeholder="Enter your name" required>'
        soup = BeautifulSoup(html, 'html.parser')
        input_element = soup.find('input')
        
        field_info = ai_service._extract_field_info(input_element)
        
        assert field_info["name"] == "full_name"
        assert field_info["type"] == "text"
        assert field_info["category"] == "full_name"
        assert field_info["required"] == True
        
        # Test email input
        html = '<input type="email" name="email_address" placeholder="your@email.com">'
        soup = BeautifulSoup(html, 'html.parser')
        input_element = soup.find('input')
        
        field_info = ai_service._extract_field_info(input_element)
        assert field_info["category"] == "email"
        
        # Test select field
        html = '''
        <select name="experience_level">
            <option value="entry">Entry Level</option>
            <option value="mid">Mid Level</option>
            <option value="senior">Senior Level</option>
        </select>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        select_element = soup.find('select')
        
        field_info = ai_service._extract_field_info(select_element)
        assert field_info["type"] == "select"
        assert len(field_info["options"]) == 3
        assert field_info["options"][0]["value"] == "entry"

    async def test_categorize_field_accuracy(self, ai_service):
        """Test field categorization accuracy"""
        test_cases = [
            ("first_name", "fname", "First Name", "", "first_name"),
            ("lastname", "ln", "Last Name", "", "last_name"),
            ("user_email", "email", "Email Address", "your@email.com", "email"),
            ("phone_number", "tel", "Phone", "123-456-7890", "phone"),
            ("cover_letter", "cl", "Cover Letter", "Tell us about yourself", "cover_letter"),
            ("resume_file", "cv", "Upload Resume", "", "resume"),
            ("work_experience", "exp", "Experience", "Years of experience", "experience"),
            ("technical_skills", "skills", "Skills", "Programming languages", "skills"),
            ("degree", "education", "Education", "University degree", "education"),
            ("salary_expectation", "comp", "Salary", "Expected compensation", "salary"),
            ("start_date", "available", "Availability", "When can you start", "start_date"),
            ("why_company", "question", "Why do you want to work here?", "", "custom_question")
        ]
        
        for name, id_attr, label, placeholder, expected_category in test_cases:
            result = ai_service._categorize_field(name, id_attr, label, placeholder)
            assert result == expected_category, f"Failed for {name}: expected {expected_category}, got {result}"

    async def test_determine_application_flow(self, ai_service):
        """Test application flow determination"""
        from bs4 import BeautifulSoup
        
        # Test external ATS
        html = '''
        <html>
            <body>
                <a href="https://greenhouse.io/apply">Apply Now</a>
            </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        flow = ai_service._determine_application_flow(soup, "https://example.com")
        assert flow == "external_ats"
        
        # Test embedded form
        html = '''
        <html>
            <body>
                <form action="/apply">
                    <input type="text" name="name">
                    <input type="submit" value="Apply">
                </form>
            </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        flow = ai_service._determine_application_flow(soup, "https://example.com")
        assert flow == "embedded_form"
        
        # Test multi-step
        html = '''
        <html>
            <body>
                <div class="step-wizard">
                    <div class="step">Step 1</div>
                    <div class="step">Step 2</div>
                </div>
            </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        flow = ai_service._determine_application_flow(soup, "https://example.com")
        assert flow == "multi_step"

    async def test_extract_job_details(self, ai_service, mock_html_content):
        """Test job details extraction"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(mock_html_content, 'html.parser')
        job_details = ai_service._extract_job_details(soup)
        
        assert "title" in job_details
        assert "company" in job_details
        assert "description" in job_details
        assert job_details["title"] == "Software Engineer - Tech Company"
        assert job_details["company"] == "Tech Company"

    async def test_generate_intelligent_responses(self, ai_service, mock_user_profile):
        """Test intelligent response generation"""
        form_fields = [
            {"name": "first_name", "category": "first_name", "label": "First Name"},
            {"name": "last_name", "category": "last_name", "label": "Last Name"},
            {"name": "email", "category": "email", "label": "Email"},
            {"name": "experience", "category": "experience", "label": "Experience"},
            {"name": "skills", "category": "skills", "label": "Technical Skills"},
            {"name": "cover_letter", "category": "cover_letter", "label": "Cover Letter"},
            {"name": "custom_question", "category": "custom_question", "label": "Why do you want to work here?"}
        ]
        
        job_details = {
            "title": "Software Engineer",
            "company": "Tech Company",
            "description": "We are looking for a talented engineer..."
        }
        
        # Mock OpenAI responses
        with patch.object(ai_service.openai_client.chat.completions, 'create') as mock_create:
            mock_response = AsyncMock()
            mock_response.choices = [AsyncMock()]
            mock_response.choices[0].message.content = "Generated response"
            mock_create.return_value = mock_response
            
            responses = await ai_service.generate_intelligent_responses(
                form_fields, mock_user_profile, job_details
            )
        
        # Check basic profile fields
        assert responses["first_name"] == "John"
        assert responses["last_name"] == "Doe"
        assert responses["email"] == "john.doe@example.com"
        
        # Check professional fields
        assert "experience" in responses["experience"]
        assert "Python" in responses["skills"]
        
        # Check AI-generated fields
        assert "cover_letter" in responses
        assert "custom_question" in responses

    async def test_get_profile_field_mapping(self, ai_service, mock_user_profile):
        """Test profile field mapping"""
        assert ai_service._get_profile_field(mock_user_profile, "first_name") == "John"
        assert ai_service._get_profile_field(mock_user_profile, "last_name") == "Doe"
        assert ai_service._get_profile_field(mock_user_profile, "full_name") == "John Doe"
        assert ai_service._get_profile_field(mock_user_profile, "email") == "john.doe@example.com"
        assert ai_service._get_profile_field(mock_user_profile, "phone") == "+1234567890"

    async def test_get_professional_field_extraction(self, ai_service, mock_user_profile):
        """Test professional field extraction"""
        experience = ai_service._get_professional_field(mock_user_profile, "experience")
        assert "3 years" in experience
        assert "Senior Software Engineer" in experience
        
        skills = ai_service._get_professional_field(mock_user_profile, "skills")
        assert "Python" in skills
        assert "JavaScript" in skills
        
        education = ai_service._get_professional_field(mock_user_profile, "education")
        assert "Bachelor of Science" in education
        assert "Computer Science" in education

    async def test_generate_cover_letter(self, ai_service, mock_user_profile):
        """Test AI cover letter generation"""
        job_details = {
            "title": "Software Engineer",
            "company": "Tech Company",
            "description": "We are looking for a talented engineer..."
        }
        
        # Mock OpenAI responses
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "I am excited to apply for the Software Engineer position..."
        
        with patch.object(ai_service.openai_client.chat.completions, 'create', return_value=mock_response):
            cover_letter = await ai_service._generate_cover_letter(mock_user_profile, job_details)
        
        assert len(cover_letter) > 0
        assert isinstance(cover_letter, str)

    async def test_generate_question_response(self, ai_service, mock_user_profile):
        """Test AI question response generation"""
        question = "Why do you want to work at our company?"
        job_details = {
            "title": "Software Engineer",
            "company": "Tech Company"
        }
        
        # Mock OpenAI responses
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "I am attracted to your company because..."
        
        with patch.object(ai_service.openai_client.chat.completions, 'create', return_value=mock_response):
            response = await ai_service._generate_question_response(question, mock_user_profile, job_details)
        
        assert len(response) > 0
        assert isinstance(response, str)

    async def test_humanize_text(self, ai_service):
        """Test text humanization"""
        original_text = "I am extremely enthusiastic about this extraordinary opportunity to contribute to your prestigious organization."
        
        # Mock OpenAI response
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "I'm really excited about this opportunity to join your team."
        
        with patch.object(ai_service.openai_client.chat.completions, 'create', return_value=mock_response):
            humanized = await ai_service._humanize_text(original_text)
        
        assert humanized != original_text
        assert len(humanized) > 0

    async def test_submit_application_success(self, ai_service):
        """Test successful application submission"""
        form_data = {
            "form_action": "https://example.com/apply",
            "form_method": "post",
            "form_fields": [
                {"name": "first_name"},
                {"name": "last_name"},
                {"name": "email"}
            ]
        }
        
        responses = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com"
        }
        
        job_url = "https://example.com/jobs/123"
        
        # Mock successful HTTP response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = "Thank you for your application!"
        
        with patch.object(ai_service.session, 'post') as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            result = await ai_service.submit_application(form_data, responses, job_url)
        
        assert result["success"] == True
        assert result["status_code"] == 200
        assert "submitted_at" in result

    async def test_submit_application_failure(self, ai_service):
        """Test application submission failure"""
        form_data = {
            "form_action": "https://example.com/apply",
            "form_method": "post",
            "form_fields": [{"name": "email"}]
        }
        
        responses = {"email": "invalid-email"}
        job_url = "https://example.com/jobs/123"
        
        # Mock error HTTP response
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.text.return_value = "Invalid email address"
        
        with patch.object(ai_service.session, 'post') as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            result = await ai_service.submit_application(form_data, responses, job_url)
        
        assert result["success"] == False
        assert result["status_code"] == 400

    async def test_detect_submission_success_scenarios(self, ai_service):
        """Test submission success detection"""
        # Success scenarios
        success_texts = [
            "Thank you for your application!",
            "Your application has been submitted successfully",
            "Application received - we will review it soon",
            "Confirmation: Application sent"
        ]
        
        for text in success_texts:
            assert ai_service._detect_submission_success(text, 200) == True
        
        # Error scenarios
        error_texts = [
            "Error: Missing required field",
            "Application failed to submit",
            "Please try again",
            "Something went wrong"
        ]
        
        for text in error_texts:
            assert ai_service._detect_submission_success(text, 200) == False
        
        # HTTP error codes
        assert ai_service._detect_submission_success("Any text", 404) == False
        assert ai_service._detect_submission_success("Any text", 500) == False

    async def test_openai_api_error_handling(self, ai_service, mock_user_profile):
        """Test OpenAI API error handling"""
        job_details = {"title": "Engineer", "company": "Test"}
        
        # Mock OpenAI API error
        with patch.object(ai_service.openai_client.chat.completions, 'create') as mock_create:
            mock_create.side_effect = Exception("OpenAI API Error")
            
            # Should return fallback text instead of crashing
            cover_letter = await ai_service._generate_cover_letter(mock_user_profile, job_details)
            
            assert len(cover_letter) > 0
            assert "excited to apply" in cover_letter.lower()

    async def test_network_error_handling(self, ai_service, mock_job_url):
        """Test network error handling"""
        # Mock network error
        with patch.object(ai_service.session, 'get') as mock_get:
            mock_get.side_effect = aiohttp.ClientError("Network error")
            
            with pytest.raises(Exception) as exc_info:
                await ai_service.scrape_job_application_form(mock_job_url)
            
            assert "Failed to scrape application form" in str(exc_info.value)

    async def test_malformed_html_handling(self, ai_service, mock_job_url):
        """Test handling of malformed HTML"""
        malformed_html = "<html><body><form><input name='test' type='text'></body></html>"
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = malformed_html
        
        with patch.object(ai_service.session, 'get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # Should handle gracefully without crashing
            result = await ai_service.scrape_job_application_form(mock_job_url)
            
            assert "form_fields" in result
            assert isinstance(result["form_fields"], list)

    async def test_empty_form_handling(self, ai_service, mock_job_url):
        """Test handling of pages with no forms"""
        no_form_html = "<html><body><h1>Job Details</h1><p>No application form here</p></body></html>"
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = no_form_html
        
        with patch.object(ai_service.session, 'get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await ai_service.scrape_job_application_form(mock_job_url)
            
            assert result["form_fields"] == []
            assert result["form_action"] == ""

    async def test_context_manager_cleanup(self):
        """Test that context manager properly cleans up resources"""
        service = AIApplicationService()
        
        async with service:
            assert service.session is not None
        
        # Session should be closed after context manager exit
        assert service.session.closed

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 