import base64
from unittest.mock import MagicMock, Mock, patch

import pytest
from services.resume_parser_service import ResumeParserService


class TestResumeParserService:

    @pytest.fixture
    def parser(self):
        return ResumeParserService()

    @pytest.fixture
    def sample_resume_text(self):
        return """
        John Doe
        Software Engineer
        john.doe@email.com
        +1-555-123-4567
        linkedin.com/in/johndoe
        github.com/johndoe
        
        SUMMARY
        Experienced software engineer with 5+ years in web development.
        
        EXPERIENCE
        Senior Developer - Tech Corp
        2020 - Present
        - Developed web applications using Python and React
        - Led team of 5 developers
        
        Junior Developer - Startup Inc
        2018 - 2020
        - Built REST APIs with Django
        - Worked with MySQL and Redis
        
        EDUCATION
        Bachelor of Science in Computer Science
        University of Technology
        2014 - 2018
        
        SKILLS
        Programming: Python, JavaScript, Java
        Frameworks: Django, React, Spring
        Databases: MySQL, PostgreSQL, MongoDB
        Tools: Git, Docker, AWS
        Languages: English, Turkish
        """

    @pytest.fixture
    def sample_pdf_content(self):
        # Mock PDF content
        return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"

    @pytest.fixture
    def sample_docx_content(self):
        # Mock DOCX content
        return b"PK\x03\x04\x14\x00\x00\x00\x08\x00"

    def test_init(self, parser):
        """Test service initialization"""
        assert parser.email_pattern is not None
        assert parser.phone_pattern is not None
        assert "programming" in parser.tech_skills
        assert "frameworks" in parser.tech_skills
        assert "databases" in parser.tech_skills

    def test_extract_personal_info(self, parser, sample_resume_text):
        """Test personal information extraction"""
        info = parser._extract_personal_info(sample_resume_text)

        assert info["email"] == "john.doe@email.com"
        assert info["phone"] == "+1-555-123-4567"
        assert info["linkedin"] == "linkedin.com/in/johndoe"
        assert info["github"] == "github.com/johndoe"
        assert info["name"] == "John Doe"

    def test_extract_skills(self, parser, sample_resume_text):
        """Test skills extraction"""
        skills = parser._extract_skills(sample_resume_text)

        assert "programming" in skills
        assert "python" in skills["programming"]
        assert "javascript" in skills["programming"]
        assert "java" in skills["programming"]

        assert "frameworks" in skills
        assert "django" in skills["frameworks"]
        assert "react" in skills["frameworks"]

        assert "databases" in skills
        assert "mysql" in skills["databases"]
        assert "postgresql" in skills["databases"]
        assert "mongodb" in skills["databases"]

    def test_extract_experience(self, parser, sample_resume_text):
        """Test experience extraction"""
        lines = sample_resume_text.split("\n")
        experience = parser._extract_experience(sample_resume_text, lines)

        assert len(experience) >= 1
        # Check if experience contains expected data
        exp = experience[0]
        assert "company" in exp or "position" in exp

    def test_extract_education(self, parser, sample_resume_text):
        """Test education extraction"""
        lines = sample_resume_text.split("\n")
        education = parser._extract_education(sample_resume_text, lines)

        assert len(education) >= 1
        # Check if education contains expected data
        edu = education[0]
        assert "degree" in edu or "institution" in edu

    def test_extract_languages(self, parser, sample_resume_text):
        """Test language extraction"""
        languages = parser._extract_languages(sample_resume_text)

        assert "english" in languages
        assert "turkish" in languages

    def test_extract_summary(self, parser, sample_resume_text):
        """Test summary extraction"""
        summary = parser._extract_summary(sample_resume_text)

        assert "experienced software engineer" in summary.lower()
        assert len(summary) > 0

    @patch("services.resume_parser_service.PyPDF2.PdfReader")
    def test_extract_text_from_pdf(self, mock_pdf_reader, parser, sample_pdf_content):
        """Test PDF text extraction"""
        # Mock PDF reader
        mock_reader = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = "Sample PDF content"
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader

        text = parser._extract_text_from_pdf(sample_pdf_content)

        assert text == "Sample PDF content\n"
        mock_pdf_reader.assert_called_once()

    @patch("services.resume_parser_service.Document")
    def test_extract_text_from_docx(self, mock_document, parser, sample_docx_content):
        """Test DOCX text extraction"""
        # Mock document
        mock_doc = Mock()
        mock_paragraph = Mock()
        mock_paragraph.text = "Sample DOCX content"
        mock_doc.paragraphs = [mock_paragraph]
        mock_document.return_value = mock_doc

        text = parser._extract_text_from_docx(sample_docx_content)

        assert text == "Sample DOCX content\n"
        mock_document.assert_called_once()

    def test_parse_text(self, parser, sample_resume_text):
        """Test complete text parsing"""
        result = parser._parse_text(sample_resume_text)

        assert "personal_info" in result
        assert "skills" in result
        assert "experience" in result
        assert "education" in result
        assert "languages" in result
        assert "summary" in result
        assert "parsed_at" in result

    def test_parse_resume_pdf(self, parser, sample_pdf_content):
        """Test PDF resume parsing"""
        with patch.object(
            parser, "_extract_text_from_pdf", return_value="Sample content"
        ):
            result = parser.parse_resume(sample_pdf_content, "pdf")

            assert "personal_info" in result
            assert "skills" in result
            assert "experience" in result

    def test_parse_resume_docx(self, parser, sample_docx_content):
        """Test DOCX resume parsing"""
        with patch.object(
            parser, "_extract_text_from_docx", return_value="Sample content"
        ):
            result = parser.parse_resume(sample_docx_content, "docx")

            assert "personal_info" in result
            assert "skills" in result
            assert "experience" in result

    def test_parse_resume_txt(self, parser):
        """Test TXT resume parsing"""
        content = b"Sample text content"
        result = parser.parse_resume(content, "txt")

        assert "personal_info" in result
        assert "skills" in result
        assert "experience" in result

    def test_parse_resume_unsupported_format(self, parser):
        """Test unsupported file format"""
        content = b"Sample content"
        result = parser.parse_resume(content, "unsupported")

        assert "error" in result
        assert "Unsupported file type" in result["error"]

    def test_parse_resume_from_base64(self, parser):
        """Test base64 resume parsing"""
        content = "Sample content"
        base64_content = base64.b64encode(content.encode()).decode()

        with patch.object(parser, "parse_resume", return_value={"test": "data"}):
            result = parser.parse_resume_from_base64(base64_content, "txt")

            assert result == {"test": "data"}

    def test_parse_resume_from_base64_invalid(self, parser):
        """Test invalid base64 content"""
        result = parser.parse_resume_from_base64("invalid_base64", "txt")

        assert "error" in result

    def test_get_parsed_resume_summary(self, parser):
        """Test resume summary generation"""
        parsed_data = {
            "personal_info": {"name": "John Doe"},
            "skills": {"programming": ["python"]},
            "experience": [{"company": "Tech Corp"}],
            "education": [{"degree": "Bachelor"}],
            "languages": ["english"],
            "summary": "Experienced developer",
        }

        summary = parser.get_parsed_resume_summary(parsed_data)

        assert summary["has_personal_info"] is True
        assert summary["has_skills"] is True
        assert summary["has_experience"] is True
        assert summary["has_education"] is True
        assert summary["has_languages"] is True
        assert summary["has_summary"] is True
        assert summary["total_skills"] == 1
        assert summary["experience_count"] == 1
        assert summary["education_count"] == 1
        assert summary["language_count"] == 1

    def test_parse_resume_error_handling(self, parser):
        """Test error handling in resume parsing"""
        with patch.object(
            parser, "_extract_text_from_pdf", side_effect=Exception("PDF error")
        ):
            result = parser.parse_resume(b"content", "pdf")

            assert "error" in result
            assert "PDF error" in result["error"]

    def test_email_pattern_matching(self, parser):
        """Test email pattern matching"""
        text = "Contact me at john.doe@email.com or jane@company.org"
        emails = parser._extract_personal_info(text)

        assert emails["email"] == "john.doe@email.com"

    def test_phone_pattern_matching(self, parser):
        """Test phone pattern matching"""
        text = "Call me at +1-555-123-4567 or 555-987-6543"
        phones = parser._extract_personal_info(text)

        assert phones["phone"] == "+1-555-123-4567"

    def test_linkedin_pattern_matching(self, parser):
        """Test LinkedIn pattern matching"""
        text = "Find me on linkedin.com/in/johndoe"
        linkedin = parser._extract_personal_info(text)

        assert linkedin["linkedin"] == "linkedin.com/in/johndoe"

    def test_github_pattern_matching(self, parser):
        """Test GitHub pattern matching"""
        text = "Check my code at github.com/johndoe"
        github = parser._extract_personal_info(text)

        assert github["github"] == "github.com/johndoe"

    def test_skill_categories(self, parser):
        """Test all skill categories"""
        text = """
        Skills:
        Programming: Python, JavaScript, Java
        Frameworks: React, Django, Spring
        Databases: MySQL, PostgreSQL
        Cloud: AWS, Docker, Kubernetes
        Tools: Git, Jira
        Languages: English, German
        """

        skills = parser._extract_skills(text)

        assert "programming" in skills
        assert "frameworks" in skills
        assert "databases" in skills
        assert "cloud" in skills
        assert "tools" in skills
        assert "languages" in skills

    def test_experience_date_extraction(self, parser):
        """Test experience date extraction"""
        text = """
        EXPERIENCE
        Senior Developer - Tech Corp
        2020 - Present
        Junior Developer - Startup Inc
        2018 - 2020
        """

        lines = text.split("\n")
        experience = parser._extract_experience(text, lines)

        assert len(experience) >= 1
        # Check if dates are extracted
        for exp in experience:
            if "start_date" in exp:
                assert exp["start_date"] in ["2020", "2018"]

    def test_education_degree_extraction(self, parser):
        """Test education degree extraction"""
        text = """
        EDUCATION
        Master of Science in Computer Science
        University of Technology
        2016 - 2018
        Bachelor of Science in Engineering
        Another University
        2012 - 2016
        """

        lines = text.split("\n")
        education = parser._extract_education(text, lines)

        assert len(education) >= 1
        # Check if degrees are extracted
        for edu in education:
            if "degree" in edu:
                assert (
                    "master" in edu["degree"].lower()
                    or "bachelor" in edu["degree"].lower()
                )
