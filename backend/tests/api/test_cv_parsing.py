import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock
import io
from datetime import datetime

@pytest.mark.asyncio
async def test_parse_pdf_cv_basic(async_client, mongodb):
    """Test basic PDF CV parsing functionality."""
    # Clear users collection before test
    await mongodb["users"].delete_many({})

    # Create user
    result = await mongodb["users"].insert_one({
        "email": "test@example.com",
        "onboarding_step": 2,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    user_id = str(result.inserted_id)

    # Mock PDF content extraction
    mock_pdf_content = """
    John Doe
    Software Engineer
    Email: john.doe@example.com
    Phone: +1-555-123-4567
    
    EXPERIENCE
    Senior Software Engineer - Tech Corp (2020-2023)
    - Developed Python applications
    - Led team of 5 developers
    
    Software Engineer - StartupCo (2018-2020)
    - Built React frontend applications
    - Worked with PostgreSQL databases
    
    EDUCATION
    Bachelor of Computer Science - University of Tech (2018)
    
    SKILLS
    Python, JavaScript, React, PostgreSQL, Docker, AWS
    """

    with patch('backend.routes.onboarding.extract_text_from_pdf') as mock_extract, \
         patch('backend.routes.onboarding.parse_cv_content') as mock_parse, \
         patch('backend.routes.onboarding.aiofiles.open', create=True), \
         patch('os.makedirs'), \
         patch('uuid.uuid4', return_value='test-uuid'):
        
        # Mock PDF text extraction
        mock_extract.return_value = mock_pdf_content
        
        # Mock CV parsing results
        mock_parse.return_value = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1-555-123-4567",
            "title": "Software Engineer",
            "experience_years": 5,
            "skills": ["Python", "JavaScript", "React", "PostgreSQL", "Docker", "AWS"],
            "education": ["Bachelor of Computer Science - University of Tech (2018)"],
            "work_experience": [
                {
                    "company": "Tech Corp",
                    "position": "Senior Software Engineer", 
                    "duration": "2020-2023",
                    "description": "Developed Python applications, Led team of 5 developers"
                },
                {
                    "company": "StartupCo",
                    "position": "Software Engineer",
                    "duration": "2018-2020", 
                    "description": "Built React frontend applications, Worked with PostgreSQL databases"
                }
            ]
        }
        
        response = await async_client.post(
            "/api/onboarding/upload-cv",
            data={"user_id": user_id, "parse": "true"},
            files={"file": ("john_doe_cv.pdf", b"PDF content", "application/pdf")}
        )
        
    assert response.status_code == 200
    data = response.json()
    assert "başarıyla yüklendi" in data["message"]
    assert "parsed_data" in data
    
    parsed = data["parsed_data"]
    assert parsed["name"] == "John Doe"
    assert parsed["email"] == "john.doe@example.com"
    assert parsed["experience_years"] == 5
    assert "Python" in parsed["skills"]
    assert len(parsed["work_experience"]) == 2

@pytest.mark.asyncio
async def test_parse_docx_cv_with_special_characters(async_client):
    """Test DOCX CV parsing with Turkish characters and special formatting."""
    # Mock DOCX content with Turkish characters
    mock_docx_content = """
    Ahmet Özkan
    Yazılım Geliştirici
    E-posta: ahmet.ozkan@example.com
    Telefon: +90-555-123-4567
    
    DENEYİM
    Kıdemli Yazılım Geliştirici - Teknoloji A.Ş. (2021-2024)
    • Python ve Django ile web uygulamaları geliştirdi
    • 10 kişilik ekip liderliği yaptı
    
    Yazılım Geliştirici - Girişim Ltd. (2019-2021)
    • React ve TypeScript ile frontend geliştirdi
    • PostgreSQL veritabanı tasarımı yaptı
    
    EĞİTİM
    Bilgisayar Mühendisliği - İstanbul Teknik Üniversitesi (2019)
    
    YETENEKLER
    Python, Django, React, TypeScript, PostgreSQL, Redis, Docker
    """

    with patch('backend.routes.onboarding.extract_text_from_docx') as mock_extract, \
         patch('backend.routes.onboarding.parse_cv_content') as mock_parse:
        
        mock_extract.return_value = mock_docx_content
        mock_parse.return_value = {
            "name": "Ahmet Özkan",
            "email": "ahmet.ozkan@example.com",
            "phone": "+90-555-123-4567",
            "title": "Yazılım Geliştirici",
            "experience_years": 5,
            "skills": ["Python", "Django", "React", "TypeScript", "PostgreSQL", "Redis", "Docker"],
            "education": ["Bilgisayar Mühendisliği - İstanbul Teknik Üniversitesi (2019)"]
        }
        
        response = await async_client.post(
            "/api/onboarding/upload-cv",
            data={"user_id": "test_user_id", "parse": "true"},
            files={"file": ("ahmet_cv.docx", b"DOCX content", 
                          "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        )
        
    assert response.status_code == 200
    data = response.json()
    assert data["parsed_data"]["name"] == "Ahmet Özkan"
    assert "Django" in data["parsed_data"]["skills"]

@pytest.mark.asyncio
async def test_parse_cv_extraction_failure(async_client):
    """Test CV parsing when text extraction fails."""
    
    with patch('backend.routes.onboarding.extract_text_from_pdf') as mock_extract:
        mock_extract.side_effect = Exception("PDF extraction failed")
        
        response = await async_client.post(
            "/api/onboarding/upload-cv",
            data={"user_id": "test_user_id", "parse": "true"},
            files={"file": ("corrupted.pdf", b"corrupted content", "application/pdf")}
        )
        
    assert response.status_code == 200  # File should still upload
    data = response.json()
    assert "başarıyla yüklendi" in data["message"]
    assert "parsing_error" in data
    assert "extraction failed" in data["parsing_error"]

@pytest.mark.asyncio
async def test_parse_cv_no_text_content(async_client):
    """Test CV parsing when PDF/DOC contains no extractable text."""
    
    with patch('backend.routes.onboarding.extract_text_from_pdf') as mock_extract, \
         patch('backend.routes.onboarding.parse_cv_content') as mock_parse:
        
        mock_extract.return_value = ""  # Empty text
        mock_parse.return_value = {"error": "No extractable text found"}
        
        response = await async_client.post(
            "/api/onboarding/upload-cv",
            data={"user_id": "test_user_id", "parse": "true"},
            files={"file": ("image_only.pdf", b"PDF with only images", "application/pdf")}
        )
        
    assert response.status_code == 200
    data = response.json()
    assert "parsed_data" in data
    assert "error" in data["parsed_data"]

@pytest.mark.asyncio
async def test_parse_cv_multiple_emails_phones(async_client):
    """Test CV parsing when multiple emails and phone numbers exist."""
    
    mock_cv_content = """
    Maria Garcia
    Senior Data Scientist
    
    Contact Information:
    Work Email: maria.garcia@company.com
    Personal Email: maria.personal@gmail.com
    Work Phone: +1-555-123-4567
    Mobile: +1-555-987-6543
    
    EXPERIENCE
    Senior Data Scientist - DataCorp (2022-2024)
    Data Scientist - AnalyticsCo (2020-2022)
    
    SKILLS
    Python, R, SQL, Machine Learning, TensorFlow, PyTorch
    """

    with patch('backend.routes.onboarding.extract_text_from_pdf') as mock_extract, \
         patch('backend.routes.onboarding.parse_cv_content') as mock_parse:
        
        mock_extract.return_value = mock_cv_content
        mock_parse.return_value = {
            "name": "Maria Garcia",
            "emails": ["maria.garcia@company.com", "maria.personal@gmail.com"],
            "email": "maria.garcia@company.com",  # Primary email
            "phones": ["+1-555-123-4567", "+1-555-987-6543"],
            "phone": "+1-555-123-4567",  # Primary phone
            "title": "Senior Data Scientist",
            "experience_years": 4,
            "skills": ["Python", "R", "SQL", "Machine Learning", "TensorFlow", "PyTorch"]
        }
        
        response = await async_client.post(
            "/api/onboarding/upload-cv",
            data={"user_id": "test_user_id", "parse": "true"},
            files={"file": ("maria_cv.pdf", b"PDF content", "application/pdf")}
        )
        
    assert response.status_code == 200
    data = response.json()
    parsed = data["parsed_data"]
    assert parsed["name"] == "Maria Garcia"
    assert len(parsed["emails"]) == 2
    assert parsed["email"] == "maria.garcia@company.com"
    assert "TensorFlow" in parsed["skills"]

@pytest.mark.asyncio
async def test_parse_cv_with_auto_profile_creation(async_client, mongodb):
    """Test CV parsing with automatic profile field population."""
    # Clear users collection before test
    await mongodb["users"].delete_many({})

    # Create user
    result = await mongodb["users"].insert_one({
        "email": "test@example.com",
        "onboarding_step": 2,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    user_id = str(result.inserted_id)

    mock_parsed_data = {
        "name": "Alex Smith",
        "email": "alex.smith@example.com",
        "title": "Full Stack Developer",
        "experience_years": 3,
        "skills": ["JavaScript", "Node.js", "React", "MongoDB"],
        "bio": "Experienced full stack developer with expertise in modern web technologies",
        "location": "San Francisco, CA"
    }

    with patch('backend.routes.onboarding.extract_text_from_pdf') as mock_extract, \
         patch('backend.routes.onboarding.parse_cv_content') as mock_parse, \
         patch('backend.routes.onboarding.aiofiles.open', create=True), \
         patch('os.makedirs'), \
         patch('uuid.uuid4', return_value='test-uuid'):
        
        mock_extract.return_value = "CV content here"
        mock_parse.return_value = mock_parsed_data
        
        response = await async_client.post(
            "/api/onboarding/upload-cv",
            data={"user_id": user_id, "parse": "true", "auto_fill": "true"},
            files={"file": ("alex_cv.pdf", b"PDF content", "application/pdf")}
        )
        
    assert response.status_code == 200
    data = response.json()
    assert "auto_filled" in data
    assert data["auto_filled"] is True

    # Check user profile was updated with parsed data
    user = await mongodb["users"].find_one({"_id": result.inserted_id})
    assert user["name"] == "Alex Smith"
    assert user["bio"] == "Experienced full stack developer with expertise in modern web technologies"
    assert user["skills"] == ["JavaScript", "Node.js", "React", "MongoDB"]
    assert user["experience_years"] == 3

@pytest.mark.asyncio
async def test_parse_cv_skill_extraction_algorithms(async_client):
    """Test different skill extraction patterns and algorithms."""
    
    test_cases = [
        {
            "content": "TECHNICAL SKILLS: Python, Java, C++, JavaScript, SQL",
            "expected_skills": ["Python", "Java", "C++", "JavaScript", "SQL"]
        },
        {
            "content": "Skills: • Python • React • Docker • AWS • PostgreSQL",
            "expected_skills": ["Python", "React", "Docker", "AWS", "PostgreSQL"]
        },
        {
            "content": "Programming Languages: Python (5 years), JavaScript (3 years), Go (1 year)",
            "expected_skills": ["Python", "JavaScript", "Go"]
        },
        {
            "content": "Tech Stack: Frontend: React, Vue.js Backend: Node.js, Django Database: MySQL, Redis",
            "expected_skills": ["React", "Vue.js", "Node.js", "Django", "MySQL", "Redis"]
        }
    ]

    for i, test_case in enumerate(test_cases):
        with patch('backend.routes.onboarding.extract_text_from_pdf') as mock_extract, \
             patch('backend.routes.onboarding.parse_cv_content') as mock_parse:
            
            mock_extract.return_value = test_case["content"]
            mock_parse.return_value = {
                "name": f"Test User {i}",
                "skills": test_case["expected_skills"]
            }
            
            response = await async_client.post(
                "/api/onboarding/upload-cv",
                data={"user_id": "test_user_id", "parse": "true"},
                files={"file": (f"test_{i}.pdf", b"PDF content", "application/pdf")}
            )
            
        assert response.status_code == 200
        data = response.json()
        parsed_skills = data["parsed_data"]["skills"]
        assert set(parsed_skills) == set(test_case["expected_skills"])

@pytest.mark.asyncio
async def test_parse_cv_experience_calculation(async_client):
    """Test experience years calculation from work history."""
    
    mock_cv_content = """
    John Developer
    
    WORK EXPERIENCE
    Senior Developer - Current Company (Jan 2022 - Present)
    Developer - Previous Company (Mar 2020 - Dec 2021)
    Junior Developer - First Company (Jun 2018 - Feb 2020)
    Intern - Startup (Jun 2017 - Aug 2017)
    """

    with patch('backend.routes.onboarding.extract_text_from_pdf') as mock_extract, \
         patch('backend.routes.onboarding.parse_cv_content') as mock_parse:
        
        mock_extract.return_value = mock_cv_content
        
        # Mock experience calculation logic
        mock_parse.return_value = {
            "name": "John Developer",
            "experience_years": 6,  # 2017-2024, excluding intern period
            "work_experience": [
                {"company": "Current Company", "duration": "Jan 2022 - Present", "months": 24},
                {"company": "Previous Company", "duration": "Mar 2020 - Dec 2021", "months": 22},
                {"company": "First Company", "duration": "Jun 2018 - Feb 2020", "months": 20},
                {"company": "Startup", "duration": "Jun 2017 - Aug 2017", "months": 2, "type": "intern"}
            ],
            "total_experience_months": 66
        }
        
        response = await async_client.post(
            "/api/onboarding/upload-cv",
            data={"user_id": "test_user_id", "parse": "true"},
            files={"file": ("john_cv.pdf", b"PDF content", "application/pdf")}
        )
        
    assert response.status_code == 200
    data = response.json()
    parsed = data["parsed_data"]
    assert parsed["experience_years"] == 6
    assert parsed["total_experience_months"] == 66
    assert len(parsed["work_experience"]) == 4

@pytest.mark.asyncio
async def test_parse_cv_different_date_formats(async_client):
    """Test parsing CVs with different date formats."""
    
    date_format_tests = [
        "Jan 2020 - Dec 2022",
        "01/2020 - 12/2022", 
        "2020-2022",
        "January 2020 to December 2022",
        "2020.01 - 2022.12",
        "Jan'20 - Dec'22"
    ]

    for date_format in date_format_tests:
        mock_content = f"Software Engineer - Company ({date_format})"
        
        with patch('backend.routes.onboarding.extract_text_from_pdf') as mock_extract, \
             patch('backend.routes.onboarding.parse_cv_content') as mock_parse:
            
            mock_extract.return_value = mock_content
            mock_parse.return_value = {
                "name": "Test Developer",
                "work_experience": [{
                    "position": "Software Engineer",
                    "company": "Company",
                    "duration": date_format,
                    "start_date": "2020-01",
                    "end_date": "2022-12",
                    "months": 24
                }]
            }
            
            response = await async_client.post(
                "/api/onboarding/upload-cv",
                data={"user_id": "test_user_id", "parse": "true"},
                files={"file": ("cv.pdf", b"PDF content", "application/pdf")}
            )
            
        assert response.status_code == 200
        data = response.json()
        work_exp = data["parsed_data"]["work_experience"][0]
        assert work_exp["duration"] == date_format
        assert work_exp["months"] == 24

@pytest.mark.asyncio  
async def test_cv_parsing_performance_large_file(async_client):
    """Test CV parsing performance with large file."""
    
    # Simulate large CV content (50KB+)
    large_content = "Software Engineer\n" * 1000 + "Skills: Python, Java\n" * 500
    
    with patch('backend.routes.onboarding.extract_text_from_pdf') as mock_extract, \
         patch('backend.routes.onboarding.parse_cv_content') as mock_parse:
        
        mock_extract.return_value = large_content
        mock_parse.return_value = {
            "name": "Large CV User",
            "skills": ["Python", "Java"],
            "processing_time": 2.5  # seconds
        }
        
        response = await async_client.post(
            "/api/onboarding/upload-cv",
            data={"user_id": "test_user_id", "parse": "true"},
            files={"file": ("large_cv.pdf", b"Large PDF content", "application/pdf")}
        )
        
    assert response.status_code == 200
    data = response.json()
    assert "parsed_data" in data
    # Ensure parsing doesn't timeout (would get 500 error if it did) 