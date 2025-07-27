from unittest.mock import Mock, patch

import pytest
from services.job_matching_service import JobMatchingService


class TestJobMatchingService:

    @pytest.fixture
    def matcher(self):
        return JobMatchingService()

    @pytest.fixture
    def sample_resume_data(self):
        return {
            "personal_info": {
                "name": "John Doe",
                "email": "john@example.com",
                "location": "San Francisco, CA",
            },
            "skills": {
                "programming": ["python", "javascript", "java"],
                "frameworks": ["django", "react", "spring"],
                "databases": ["mysql", "postgresql"],
                "cloud": ["aws", "docker"],
                "tools": ["git", "jira"],
                "languages": ["english", "turkish"],
            },
            "experience": [
                {
                    "company": "Tech Corp",
                    "position": "Senior Developer",
                    "start_date": "2020",
                    "end_date": "present",
                    "duration": "3 years",
                },
                {
                    "company": "Startup Inc",
                    "position": "Junior Developer",
                    "start_date": "2018",
                    "end_date": "2020",
                    "duration": "2 years",
                },
            ],
            "education": [
                {
                    "degree": "Bachelor of Science",
                    "institution": "University of Technology",
                    "start_date": "2014",
                    "end_date": "2018",
                }
            ],
            "languages": ["english", "turkish"],
            "summary": "Experienced software engineer with 5+ years in web development.",
        }

    @pytest.fixture
    def sample_job_data(self):
        return {
            "id": "job_123",
            "title": "Senior Python Developer",
            "company": "Tech Company",
            "location": "San Francisco, CA",
            "description": """
            We are looking for a Senior Python Developer with experience in:
            - Python, Django, React
            - MySQL, PostgreSQL
            - AWS, Docker
            - Git, Jira
            
            Requirements:
            - 5+ years of experience
            - Bachelor's degree in Computer Science
            - Experience with web development
            """,
            "salary_range": {"min": 80000, "max": 120000},
        }

    def test_init(self, matcher):
        """Test service initialization"""
        assert matcher.skill_weights is not None
        assert matcher.experience_weights is not None
        assert matcher.level_keywords is not None

    def test_calculate_matching_score(
        self, matcher, sample_resume_data, sample_job_data
    ):
        """Test matching score calculation"""
        result = matcher.calculate_matching_score(sample_resume_data, sample_job_data)

        assert "overall_score" in result
        assert "skill_score" in result
        assert "experience_score" in result
        assert "location_score" in result
        assert "salary_score" in result
        assert "education_score" in result
        assert "matching_details" in result
        assert "calculated_at" in result

        # Check score ranges
        assert 0 <= result["overall_score"] <= 1
        assert 0 <= result["skill_score"] <= 1
        assert 0 <= result["experience_score"] <= 1
        assert 0 <= result["location_score"] <= 1
        assert 0 <= result["salary_score"] <= 1
        assert 0 <= result["education_score"] <= 1

    def test_extract_job_requirements(self, matcher, sample_job_data):
        """Test job requirements extraction"""
        requirements = matcher._extract_job_requirements(sample_job_data)

        assert "programming" in requirements
        assert "python" in requirements["programming"]

        assert "frameworks" in requirements
        assert "django" in requirements["frameworks"]
        assert "react" in requirements["frameworks"]

        assert "databases" in requirements
        assert "mysql" in requirements["databases"]
        assert "postgresql" in requirements["databases"]

        assert "cloud" in requirements
        assert "aws" in requirements["cloud"]
        assert "docker" in requirements["cloud"]

    def test_calculate_skill_matching(
        self, matcher, sample_resume_data, sample_job_data
    ):
        """Test skill matching calculation"""
        score = matcher._calculate_skill_matching(sample_resume_data, sample_job_data)

        assert 0 <= score <= 1
        assert score > 0  # Should have some matching skills

    def test_calculate_experience_matching(
        self, matcher, sample_resume_data, sample_job_data
    ):
        """Test experience matching calculation"""
        score = matcher._calculate_experience_matching(
            sample_resume_data, sample_job_data
        )

        assert 0 <= score <= 1

    def test_extract_job_level(self, matcher):
        """Test job level extraction"""
        # Test senior level
        senior_job = {
            "title": "Senior Python Developer",
            "description": "Looking for senior developer with 5+ years experience",
        }
        level = matcher._extract_job_level(senior_job)
        assert level == "senior"

        # Test junior level
        junior_job = {
            "title": "Junior Developer",
            "description": "Entry level position for recent graduates",
        }
        level = matcher._extract_job_level(junior_job)
        assert level == "junior"

        # Test default level
        default_job = {
            "title": "Developer",
            "description": "General developer position",
        }
        level = matcher._extract_job_level(default_job)
        assert level == "mid"

    def test_calculate_total_experience_years(self, matcher, sample_resume_data):
        """Test total experience calculation"""
        experience = sample_resume_data["experience"]
        total_years = matcher._calculate_total_experience_years(experience)

        assert total_years >= 5  # Should be at least 5 years (3 + 2)

    def test_map_years_to_level(self, matcher):
        """Test years to level mapping"""
        assert matcher._map_years_to_level(0.5) == "entry"
        assert matcher._map_years_to_level(2) == "junior"
        assert matcher._map_years_to_level(4) == "mid"
        assert matcher._map_years_to_level(6) == "senior"
        assert matcher._map_years_to_level(10) == "lead"
        assert matcher._map_years_to_level(15) == "manager"

    def test_calculate_location_matching(
        self, matcher, sample_resume_data, sample_job_data
    ):
        """Test location matching calculation"""
        score = matcher._calculate_location_matching(
            sample_resume_data, sample_job_data
        )

        assert 0 <= score <= 1
        assert score > 0.5  # Should match well since both are in San Francisco

    def test_calculate_location_matching_remote(self, matcher, sample_resume_data):
        """Test location matching for remote jobs"""
        remote_job = {"location": "Remote"}
        score = matcher._calculate_location_matching(sample_resume_data, remote_job)

        assert score > 0.5  # Should be good for remote jobs

    def test_calculate_location_matching_different_locations(
        self, matcher, sample_resume_data
    ):
        """Test location matching for different locations"""
        different_job = {"location": "New York, NY"}
        score = matcher._calculate_location_matching(sample_resume_data, different_job)

        assert score < 0.5  # Should be lower for different locations

    def test_calculate_education_matching(
        self, matcher, sample_resume_data, sample_job_data
    ):
        """Test education matching calculation"""
        score = matcher._calculate_education_matching(
            sample_resume_data, sample_job_data
        )

        assert 0 <= score <= 1
        assert score > 0.5  # Should match well since job requires bachelor's degree

    def test_calculate_overall_score(self, matcher):
        """Test overall score calculation"""
        scores = {
            "skill": 0.8,
            "experience": 0.7,
            "location": 0.9,
            "salary": 0.5,
            "education": 0.8,
        }

        overall_score = matcher._calculate_overall_score(scores)

        assert 0 <= overall_score <= 1
        assert overall_score > 0.5  # Should be good with these scores

    def test_get_matching_details(self, matcher, sample_resume_data, sample_job_data):
        """Test matching details extraction"""
        details = matcher._get_matching_details(sample_resume_data, sample_job_data)

        assert "matching_skills" in details
        assert "missing_skills" in details
        assert "skill_coverage" in details

        assert 0 <= details["skill_coverage"] <= 1

    def test_get_top_matches(self, matcher, sample_resume_data):
        """Test top matches retrieval"""
        jobs_data = [
            {
                "id": "job_1",
                "title": "Senior Python Developer",
                "company": "Tech Corp",
                "location": "San Francisco, CA",
                "description": "Python, Django, React, AWS",
            },
            {
                "id": "job_2",
                "title": "Frontend Developer",
                "company": "Startup Inc",
                "location": "New York, NY",
                "description": "JavaScript, React, Vue",
            },
            {
                "id": "job_3",
                "title": "Java Developer",
                "company": "Enterprise Corp",
                "location": "Remote",
                "description": "Java, Spring, MySQL",
            },
        ]

        matches = matcher.get_top_matches(
            sample_resume_data, jobs_data, limit=2, min_score=0.3
        )

        assert len(matches) <= 2
        assert all("overall_score" in match for match in matches)
        assert all("job_id" in match for match in matches)

        # Check sorting (should be descending by score)
        if len(matches) > 1:
            assert matches[0]["overall_score"] >= matches[1]["overall_score"]

    def test_get_resume_recommendations(self, matcher, sample_resume_data):
        """Test resume recommendations"""
        jobs_data = [
            {
                "id": "job_1",
                "title": "Senior Python Developer",
                "company": "Tech Corp",
                "location": "San Francisco, CA",
                "description": "Python, Django, React, AWS",
            },
            {
                "id": "job_2",
                "title": "Full Stack Developer",
                "company": "Startup Inc",
                "location": "Remote",
                "description": "Python, JavaScript, React, Node.js",
            },
        ]

        recommendations = matcher.get_resume_recommendations(
            sample_resume_data, jobs_data, limit=5
        )

        assert "top_recommendations" in recommendations
        assert "skill_gaps" in recommendations
        assert "industry_insights" in recommendations
        assert "total_jobs_analyzed" in recommendations
        assert "recommendations_generated_at" in recommendations

    def test_analyze_skill_gaps(self, matcher, sample_resume_data):
        """Test skill gap analysis"""
        jobs_data = [
            {
                "id": "job_1",
                "title": "Senior Python Developer",
                "company": "Tech Corp",
                "description": "Python, Django, React, AWS, Kubernetes, TypeScript",
            }
        ]

        skill_gaps = matcher._analyze_skill_gaps(sample_resume_data, jobs_data)

        assert "missing_skills" in skill_gaps
        assert "skill_gap_count" in skill_gaps
        assert "most_demanded_skills" in skill_gaps

        # Should find some missing skills
        assert skill_gaps["skill_gap_count"] > 0

    def test_get_most_demanded_skills(self, matcher):
        """Test most demanded skills extraction"""
        jobs_data = [
            {
                "id": "job_1",
                "title": "Python Developer",
                "description": "Python, Django, React",
            },
            {
                "id": "job_2",
                "title": "React Developer",
                "description": "React, JavaScript, TypeScript",
            },
            {
                "id": "job_3",
                "title": "Python Developer",
                "description": "Python, Flask, AWS",
            },
        ]

        demanded_skills = matcher._get_most_demanded_skills(jobs_data)

        assert "python" in demanded_skills
        assert "react" in demanded_skills
        assert demanded_skills["python"] >= 2  # Python appears in 2 jobs

    def test_get_industry_insights(self, matcher, sample_resume_data):
        """Test industry insights generation"""
        jobs_data = [
            {
                "id": "job_1",
                "title": "Python Developer",
                "company": "Tech Corp",
                "location": "San Francisco, CA",
            },
            {
                "id": "job_2",
                "title": "React Developer",
                "company": "Startup Inc",
                "location": "Remote",
            },
        ]

        insights = matcher._get_industry_insights(sample_resume_data, jobs_data)

        assert "total_jobs" in insights
        assert "remote_jobs_percentage" in insights
        assert "salary_ranges" in insights
        assert "top_companies" in insights

        assert insights["total_jobs"] == 2
        assert insights["remote_jobs_percentage"] == 50.0  # 1 out of 2 jobs is remote

    def test_calculate_remote_percentage(self, matcher):
        """Test remote job percentage calculation"""
        jobs_data = [
            {"location": "San Francisco, CA"},
            {"location": "Remote"},
            {"location": "New York, NY"},
            {"location": "Work from home"},
        ]

        percentage = matcher._calculate_remote_percentage(jobs_data)

        assert percentage == 50.0  # 2 out of 4 jobs are remote

    def test_get_top_companies(self, matcher):
        """Test top companies extraction"""
        jobs_data = [
            {"company": "Tech Corp"},
            {"company": "Startup Inc"},
            {"company": "Tech Corp"},
            {"company": "Enterprise Corp"},
        ]

        top_companies = matcher._get_top_companies(jobs_data)

        assert "Tech Corp" in top_companies
        assert top_companies[0] == "Tech Corp"  # Should be first (appears twice)

    def test_matching_score_with_empty_data(self, matcher):
        """Test matching score with empty data"""
        empty_resume = {}
        empty_job = {}

        result = matcher.calculate_matching_score(empty_resume, empty_job)

        assert "overall_score" in result
        assert result["overall_score"] == 0  # Should be 0 with no data

    def test_matching_score_error_handling(self, matcher):
        """Test error handling in matching score calculation"""
        # Test with invalid data that might cause errors
        invalid_resume = {"skills": "invalid"}
        invalid_job = {"description": None}

        result = matcher.calculate_matching_score(invalid_resume, invalid_job)

        assert "overall_score" in result
        assert result["overall_score"] == 0  # Should handle errors gracefully

    def test_skill_matching_with_no_requirements(self, matcher, sample_resume_data):
        """Test skill matching when job has no requirements"""
        job_no_requirements = {
            "title": "General Developer",
            "description": "We are looking for a general developer",
        }

        score = matcher._calculate_skill_matching(
            sample_resume_data, job_no_requirements
        )

        assert score == 0.5  # Should return neutral score

    def test_experience_matching_with_no_experience(self, matcher):
        """Test experience matching with no experience"""
        resume_no_experience = {"experience": []}
        job_data = {"title": "Senior Developer"}

        score = matcher._calculate_experience_matching(resume_no_experience, job_data)

        assert score == 0.1  # Should return very low score

    def test_location_matching_with_missing_location(self, matcher, sample_resume_data):
        """Test location matching with missing location data"""
        job_no_location = {"title": "Developer"}

        score = matcher._calculate_location_matching(
            sample_resume_data, job_no_location
        )

        assert score == 0.5  # Should return neutral score
