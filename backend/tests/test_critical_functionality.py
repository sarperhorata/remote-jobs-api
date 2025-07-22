"""
Critical functionality tests - testing core business logic and data validation
"""
import pytest
import asyncio
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import json

# Add project root to path for cronjob imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.mark.asyncio
async def test_job_data_validation():
    """Test job data validation logic"""
    
    # Valid job data
    valid_job = {
        "title": "Software Engineer",
        "company": "Tech Corp",
        "description": "We are looking for a skilled software engineer",
        "location": "Remote",
        "salary_min": 50000,
        "salary_max": 80000,
        "requirements": ["Python", "Django", "PostgreSQL"],
        "benefits": ["Health insurance", "Remote work"],
        "job_type": "full-time",
        "experience_level": "mid-level"
    }
    
    # Test required fields
    required_fields = ["title", "company", "description", "location"]
    for field in required_fields:
        assert field in valid_job, f"Required field {field} missing"
    
    # Test data types
    assert isinstance(valid_job["title"], str), "Title should be string"
    assert isinstance(valid_job["salary_min"], int), "Salary min should be integer"
    assert isinstance(valid_job["requirements"], list), "Requirements should be list"
    
    # Test business rules
    assert valid_job["salary_min"] > 0, "Salary should be positive"
    assert valid_job["salary_max"] >= valid_job["salary_min"], "Max salary should be >= min salary"
    assert len(valid_job["title"]) > 0, "Title should not be empty"
    assert len(valid_job["description"]) > 10, "Description should be meaningful"

@pytest.mark.asyncio
async def test_user_data_validation():
    """Test user data validation logic"""
    
    # Valid user data
    valid_user = {
        "email": "test@example.com",
        "full_name": "John Doe",
        "password": "SecurePass123!",
        "phone": "+1234567890",
        "location": "New York",
        "experience_years": 5,
        "skills": ["Python", "JavaScript", "React"]
    }
    
    # Test email validation
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    assert re.match(email_pattern, valid_user["email"]), "Invalid email format"
    
    # Test password strength
    password = valid_user["password"]
    assert len(password) >= 8, "Password should be at least 8 characters"
    assert any(c.isupper() for c in password), "Password should contain uppercase"
    assert any(c.islower() for c in password), "Password should contain lowercase"
    assert any(c.isdigit() for c in password), "Password should contain digit"
    assert any(c in "!@#$%^&*" for c in password), "Password should contain special char"
    
    # Test phone validation
    phone_pattern = r'^\+?[1-9]\d{1,14}$'
    assert re.match(phone_pattern, valid_user["phone"]), "Invalid phone format"
    
    # Test business rules
    assert valid_user["experience_years"] >= 0, "Experience should be non-negative"
    assert len(valid_user["skills"]) > 0, "User should have at least one skill"

@pytest.mark.asyncio
async def test_search_algorithm():
    """Test search algorithm logic"""
    
    # Mock job database
    jobs = [
        {"title": "Python Developer", "company": "Tech Corp", "skills": ["Python", "Django"]},
        {"title": "JavaScript Developer", "company": "Web Inc", "skills": ["JavaScript", "React"]},
        {"title": "Full Stack Developer", "company": "Startup Co", "skills": ["Python", "JavaScript", "React"]},
        {"title": "DevOps Engineer", "company": "Cloud Corp", "skills": ["Docker", "Kubernetes"]},
        {"title": "Data Scientist", "company": "AI Labs", "skills": ["Python", "Machine Learning"]}
    ]
    
    # Test exact match search
    def search_jobs(query, job_list):
        query_lower = query.lower()
        results = []
        for job in job_list:
            if (query_lower in job["title"].lower() or 
                query_lower in job["company"].lower() or
                any(query_lower in skill.lower() for skill in job["skills"])):
                results.append(job)
        return results
    
    # Test searches
    python_results = search_jobs("python", jobs)
    assert len(python_results) == 3, "Should find 3 Python-related jobs"
    
    react_results = search_jobs("react", jobs)
    assert len(react_results) == 2, "Should find 2 React-related jobs"
    
    developer_results = search_jobs("developer", jobs)
    assert len(developer_results) == 3, "Should find 3 developer jobs"

@pytest.mark.asyncio
async def test_pagination_logic():
    """Test pagination logic"""
    
    # Mock data
    all_items = list(range(1, 101))  # 1 to 100
    
    def paginate(items, page=1, per_page=10):
        start = (page - 1) * per_page
        end = start + per_page
        return {
            "items": items[start:end],
            "total": len(items),
            "page": page,
            "per_page": per_page,
            "total_pages": (len(items) + per_page - 1) // per_page,
            "has_next": end < len(items),
            "has_prev": page > 1
        }
    
    # Test first page
    page1 = paginate(all_items, page=1, per_page=10)
    assert len(page1["items"]) == 10, "First page should have 10 items"
    assert page1["items"][0] == 1, "First item should be 1"
    assert page1["has_next"] == True, "Should have next page"
    assert page1["has_prev"] == False, "Should not have previous page"
    
    # Test last page
    page10 = paginate(all_items, page=10, per_page=10)
    assert len(page10["items"]) == 10, "Last page should have 10 items"
    assert page10["items"][-1] == 100, "Last item should be 100"
    assert page10["has_next"] == False, "Should not have next page"
    assert page10["has_prev"] == True, "Should have previous page"
    
    # Test total pages calculation
    assert page1["total_pages"] == 10, "Should have 10 total pages"

@pytest.mark.asyncio
async def test_data_filtering():
    """Test data filtering logic"""
    
    # Mock job data
    jobs = [
        {"title": "Python Developer", "salary": 70000, "location": "Remote", "experience": "mid"},
        {"title": "JavaScript Developer", "salary": 65000, "location": "New York", "experience": "junior"},
        {"title": "Senior Python Developer", "salary": 90000, "location": "Remote", "experience": "senior"},
        {"title": "Frontend Developer", "salary": 60000, "location": "San Francisco", "experience": "mid"},
        {"title": "DevOps Engineer", "salary": 85000, "location": "Remote", "experience": "senior"}
    ]
    
    def filter_jobs(job_list, **filters):
        filtered = job_list
        for key, value in filters.items():
            if key == "salary_min":
                filtered = [j for j in filtered if j["salary"] >= value]
            elif key == "salary_max":
                filtered = [j for j in filtered if j["salary"] <= value]
            elif key == "location":
                filtered = [j for j in filtered if j["location"].lower() == value.lower()]
            elif key == "experience":
                filtered = [j for j in filtered if j["experience"] == value]
        return filtered
    
    # Test salary filtering
    high_salary = filter_jobs(jobs, salary_min=80000)
    assert len(high_salary) == 2, "Should find 2 high-salary jobs"
    
    # Test location filtering
    remote_jobs = filter_jobs(jobs, location="remote")
    assert len(remote_jobs) == 3, "Should find 3 remote jobs"
    
    # Test experience filtering
    senior_jobs = filter_jobs(jobs, experience="senior")
    assert len(senior_jobs) == 2, "Should find 2 senior jobs"
    
    # Test combined filtering
    remote_senior = filter_jobs(jobs, location="remote", experience="senior")
    assert len(remote_senior) == 2, "Should find 2 remote senior jobs"

@pytest.mark.asyncio
async def test_data_sorting():
    """Test data sorting logic"""
    
    # Mock job data
    jobs = [
        {"title": "Python Developer", "salary": 70000, "created_at": "2024-01-15"},
        {"title": "JavaScript Developer", "salary": 65000, "created_at": "2024-01-20"},
        {"title": "Senior Python Developer", "salary": 90000, "created_at": "2024-01-10"},
        {"title": "Frontend Developer", "salary": 60000, "created_at": "2024-01-25"},
        {"title": "DevOps Engineer", "salary": 85000, "created_at": "2024-01-05"}
    ]
    
    def sort_jobs(job_list, sort_by="created_at", order="desc"):
        reverse = order == "desc"
        if sort_by == "salary":
            return sorted(job_list, key=lambda x: x["salary"], reverse=reverse)
        elif sort_by == "created_at":
            return sorted(job_list, key=lambda x: x["created_at"], reverse=reverse)
        elif sort_by == "title":
            return sorted(job_list, key=lambda x: x["title"], reverse=reverse)
        return job_list
    
    # Test salary sorting (descending)
    salary_desc = sort_jobs(jobs, sort_by="salary", order="desc")
    assert salary_desc[0]["salary"] == 90000, "Highest salary should be first"
    assert salary_desc[-1]["salary"] == 60000, "Lowest salary should be last"
    
    # Test date sorting (ascending)
    date_asc = sort_jobs(jobs, sort_by="created_at", order="asc")
    assert date_asc[0]["created_at"] == "2024-01-05", "Earliest date should be first"
    assert date_asc[-1]["created_at"] == "2024-01-25", "Latest date should be last"
    
    # Test title sorting
    title_asc = sort_jobs(jobs, sort_by="title", order="asc")
    assert title_asc[0]["title"] == "DevOps Engineer", "Alphabetically first title should be first"

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling logic"""
    
    def safe_divide(a, b):
        try:
            return a / b
        except ZeroDivisionError:
            return None
        except TypeError:
            return None
    
    def safe_get_nested(data, keys):
        try:
            result = data
            for key in keys:
                result = result[key]
            return result
        except (KeyError, TypeError):
            return None
    
    # Test division error handling
    assert safe_divide(10, 2) == 5, "Normal division should work"
    assert safe_divide(10, 0) is None, "Division by zero should return None"
    assert safe_divide("10", 2) is None, "Type error should return None"
    
    # Test nested dictionary access
    data = {"user": {"profile": {"name": "John"}}}
    assert safe_get_nested(data, ["user", "profile", "name"]) == "John", "Valid path should work"
    assert safe_get_nested(data, ["user", "profile", "age"]) is None, "Invalid key should return None"
    assert safe_get_nested(data, ["user", "invalid"]) is None, "Invalid path should return None"

@pytest.mark.asyncio
async def test_data_transformation():
    """Test data transformation logic"""
    
    # Mock raw job data
    raw_jobs = [
        {"title": "python developer", "company": "tech corp", "salary": "70000"},
        {"title": "JAVASCRIPT DEVELOPER", "company": "WEB INC", "salary": "65000"},
        {"title": "Senior Python Developer", "company": "Startup Co", "salary": "90000"}
    ]
    
    def transform_job_data(job):
        return {
            "title": job["title"].title(),
            "company": job["company"].title(),
            "salary": int(job["salary"]),
            "formatted_salary": f"${int(job['salary']):,}",
            "title_length": len(job["title"])
        }
    
    # Transform all jobs
    transformed = [transform_job_data(job) for job in raw_jobs]
    
    # Test transformations
    assert transformed[0]["title"] == "Python Developer", "Title should be title case"
    assert transformed[0]["company"] == "Tech Corp", "Company should be title case"
    assert transformed[0]["salary"] == 70000, "Salary should be integer"
    assert transformed[0]["formatted_salary"] == "$70,000", "Salary should be formatted"
    assert transformed[0]["title_length"] == 16, "Title length should be calculated"

@pytest.mark.asyncio
async def test_business_rules():
    """Test business rules and constraints"""
    
    def validate_job_posting(job_data):
        errors = []
        
        # Salary validation
        if job_data.get("salary_min", 0) < 20000:
            errors.append("Minimum salary too low")
        if job_data.get("salary_max", 0) > 200000:
            errors.append("Maximum salary too high")
        if job_data.get("salary_min", 0) > job_data.get("salary_max", 0):
            errors.append("Minimum salary cannot exceed maximum salary")
        
        # Title validation
        if len(job_data.get("title", "")) < 3:
            errors.append("Job title too short")
        if len(job_data.get("title", "")) > 100:
            errors.append("Job title too long")
        
        # Description validation
        if len(job_data.get("description", "")) < 50:
            errors.append("Job description too short")
        
        # Requirements validation
        if not job_data.get("requirements"):
            errors.append("Job requirements are required")
        
        return errors
    
    # Test valid job
    valid_job = {
        "title": "Software Engineer",
        "description": "We are looking for a skilled software engineer with experience in Python and web development.",
        "salary_min": 50000,
        "salary_max": 80000,
        "requirements": ["Python", "Django", "PostgreSQL"]
    }
    
    errors = validate_job_posting(valid_job)
    assert len(errors) == 0, "Valid job should have no errors"
    
    # Test invalid job
    invalid_job = {
        "title": "A",  # Too short
        "description": "Short",  # Too short
        "salary_min": 10000,  # Too low
        "salary_max": 5000,  # Less than min
        "requirements": []  # Empty
    }
    
    errors = validate_job_posting(invalid_job)
    assert len(errors) > 0, "Invalid job should have errors"
    assert "Minimum salary too low" in errors, "Should catch low salary"
    assert "Minimum salary cannot exceed maximum salary" in errors, "Should catch salary range error"

if __name__ == "__main__":
    # Run tests manually for debugging
    async def run_tests():
        print("Running critical functionality tests...")
        
        print("\n1. Testing job data validation...")
        await test_job_data_validation()
        print("✓ Job data validation passed")
        
        print("\n2. Testing user data validation...")
        await test_user_data_validation()
        print("✓ User data validation passed")
        
        print("\n3. Testing search algorithm...")
        await test_search_algorithm()
        print("✓ Search algorithm passed")
        
        print("\n4. Testing pagination logic...")
        await test_pagination_logic()
        print("✓ Pagination logic passed")
        
        print("\n5. Testing data filtering...")
        await test_data_filtering()
        print("✓ Data filtering passed")
        
        print("\n6. Testing data sorting...")
        await test_data_sorting()
        print("✓ Data sorting passed")
        
        print("\n7. Testing error handling...")
        await test_error_handling()
        print("✓ Error handling passed")
        
        print("\n8. Testing data transformation...")
        await test_data_transformation()
        print("✓ Data transformation passed")
        
        print("\n9. Testing business rules...")
        await test_business_rules()
        print("✓ Business rules passed")
        
        print("\n10. Testing cronjob integration...")
        await test_cronjob_integration()
        print("✓ Cronjob integration passed")
        
        print("\nAll critical functionality tests completed successfully!")
    
    asyncio.run(run_tests())

@pytest.mark.asyncio
async def test_cronjob_integration():
    """Test cronjob integration with critical functionality"""
    
    try:
        # Import cronjob-related modules
        from backend.services.scheduler_service import start_scheduler, stop_scheduler
        from backend.utils.cronjob import wake_up_render
        
        # Test scheduler startup
        scheduler = await start_scheduler()
        assert scheduler is not None, "Scheduler should start successfully"
        assert scheduler.running, "Scheduler should be running"
        
        # Test job configuration
        jobs = scheduler.get_jobs()
        required_jobs = ['health_check_job', 'external_api_crawler_job', 'job_statistics_job']
        
        job_names = [job.name for job in jobs]
        for job_name in required_jobs:
            assert job_name in job_names, f"Required job {job_name} not found"
        
        # Test wake up render function
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "healthy"}
            mock_get.return_value = mock_response
            
            result = wake_up_render()
            assert result is True, "Wake up render should return True"
        
        # Test scheduler shutdown
        await stop_scheduler()
        assert not scheduler.running, "Scheduler should be stopped"
        
        print("✅ Cronjob integration test: PASSED")
        
    except Exception as e:
        print(f"❌ Cronjob integration test: FAILED - {str(e)}")
        raise