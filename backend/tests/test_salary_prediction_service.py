from unittest.mock import Mock, patch

import pytest
from services.salary_prediction_service import SalaryPredictionService


class TestSalaryPredictionService:

    @pytest.fixture
    def predictor(self):
        return SalaryPredictionService()

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

    def test_init(self, predictor):
        """Test service initialization"""
        assert predictor.base_salaries is not None
        assert predictor.location_multipliers is not None
        assert predictor.skill_multipliers is not None
        assert predictor.industry_multipliers is not None
        assert predictor.education_multipliers is not None

    def test_predict_salary(self, predictor, sample_resume_data, sample_job_data):
        """Test salary prediction"""
        result = predictor.predict_salary(sample_resume_data, sample_job_data)

        assert "predicted_salary" in result
        assert "confidence_score" in result
        assert "market_comparison" in result
        assert "factors" in result
        assert "predicted_at" in result

        # Check predicted salary structure
        salary = result["predicted_salary"]
        assert "min" in salary
        assert "max" in salary
        assert "avg" in salary
        assert "multiplier" in salary
        assert "factors" in salary
        assert "level" in salary

        # Check score ranges
        assert 0 <= result["confidence_score"] <= 1
        assert salary["min"] > 0
        assert salary["max"] > salary["min"]
        assert salary["avg"] >= salary["min"]
        assert salary["avg"] <= salary["max"]

    def test_calculate_base_salary(
        self, predictor, sample_resume_data, sample_job_data
    ):
        """Test base salary calculation"""
        base_salary = predictor._calculate_base_salary(
            sample_resume_data, sample_job_data
        )

        assert "min" in base_salary
        assert "max" in base_salary
        assert "avg" in base_salary
        assert "level" in base_salary

        # Check that values are reasonable
        assert base_salary["min"] > 0
        assert base_salary["max"] > base_salary["min"]
        assert base_salary["avg"] >= base_salary["min"]
        assert base_salary["avg"] <= base_salary["max"]

    def test_determine_experience_level(
        self, predictor, sample_resume_data, sample_job_data
    ):
        """Test experience level determination"""
        level = predictor._determine_experience_level(
            sample_resume_data, sample_job_data
        )

        assert level in [
            "entry",
            "junior",
            "mid",
            "senior",
            "lead",
            "manager",
            "director",
            "executive",
        ]

    def test_extract_job_level(self, predictor):
        """Test job level extraction"""
        # Test senior level
        senior_job = {
            "title": "Senior Python Developer",
            "description": "Looking for senior developer with 5+ years experience",
        }
        level = predictor._extract_job_level(senior_job)
        assert level == "senior"

        # Test junior level
        junior_job = {
            "title": "Junior Developer",
            "description": "Entry level position for recent graduates",
        }
        level = predictor._extract_job_level(junior_job)
        assert level == "junior"

        # Test default level
        default_job = {
            "title": "Developer",
            "description": "General developer position",
        }
        level = predictor._extract_job_level(default_job)
        assert level == "mid"

    def test_calculate_total_experience_years(self, predictor, sample_resume_data):
        """Test total experience calculation"""
        experience = sample_resume_data["experience"]
        total_years = predictor._calculate_total_experience_years(experience)

        assert total_years >= 5  # Should be at least 5 years (3 + 2)

    def test_map_years_to_level(self, predictor):
        """Test years to level mapping"""
        assert predictor._map_years_to_level(0.5) == "entry"
        assert predictor._map_years_to_level(2) == "junior"
        assert predictor._map_years_to_level(4) == "mid"
        assert predictor._map_years_to_level(6) == "senior"
        assert predictor._map_years_to_level(10) == "lead"
        assert predictor._map_years_to_level(15) == "manager"

    def test_apply_multipliers(self, predictor, sample_resume_data, sample_job_data):
        """Test multiplier application"""
        base_salary = {"min": 100000, "max": 150000, "avg": 125000, "level": "senior"}

        adjusted_salary = predictor._apply_multipliers(
            base_salary, sample_resume_data, sample_job_data
        )

        assert "min" in adjusted_salary
        assert "max" in adjusted_salary
        assert "avg" in adjusted_salary
        assert "multiplier" in adjusted_salary
        assert "factors" in adjusted_salary
        assert "level" in adjusted_salary

        # Check that multipliers were applied
        assert adjusted_salary["multiplier"] > 0
        assert len(adjusted_salary["factors"]) > 0

    def test_get_location_multiplier(self, predictor):
        """Test location multiplier calculation"""
        # Test San Francisco (high cost of living)
        sf_job = {"location": "San Francisco, CA"}
        sf_mult = predictor._get_location_multiplier(sf_job)
        assert sf_mult == 1.5

        # Test remote work
        remote_job = {"location": "Remote"}
        remote_mult = predictor._get_location_multiplier(remote_job)
        assert remote_mult == 0.9

        # Test unknown location
        unknown_job = {"location": "Unknown City"}
        unknown_mult = predictor._get_location_multiplier(unknown_job)
        assert unknown_mult == 1.0

    def test_get_skill_multiplier(self, predictor, sample_resume_data):
        """Test skill multiplier calculation"""
        # Test with premium skills
        job_with_premium = {"description": "Looking for AI/ML expert"}
        mult = predictor._get_skill_multiplier(sample_resume_data, job_with_premium)
        assert mult >= 1.0

        # Test with no premium skills
        job_no_premium = {"description": "General developer position"}
        mult = predictor._get_skill_multiplier(sample_resume_data, job_no_premium)
        assert mult >= 1.0

    def test_get_industry_multiplier(self, predictor):
        """Test industry multiplier calculation"""
        # Test fintech industry
        fintech_job = {
            "title": "Fintech Developer",
            "description": "Working in fintech industry",
            "company": "Fintech Corp",
        }
        mult = predictor._get_industry_multiplier(fintech_job)
        assert mult == 1.15

        # Test startup
        startup_job = {
            "title": "Startup Developer",
            "description": "Working at a startup",
            "company": "Startup Inc",
        }
        mult = predictor._get_industry_multiplier(startup_job)
        assert mult == 0.9

        # Test unknown industry
        unknown_job = {
            "title": "Developer",
            "description": "General position",
            "company": "General Corp",
        }
        mult = predictor._get_industry_multiplier(unknown_job)
        assert mult == 1.0

    def test_get_education_multiplier(self, predictor):
        """Test education multiplier calculation"""
        # Test with PhD
        phd_resume = {"education": [{"degree": "PhD in Computer Science"}]}
        mult = predictor._get_education_multiplier(phd_resume)
        assert mult == 1.15

        # Test with Master's
        masters_resume = {"education": [{"degree": "Master of Science"}]}
        mult = predictor._get_education_multiplier(masters_resume)
        assert mult == 1.1

        # Test with Bachelor's
        bachelors_resume = {"education": [{"degree": "Bachelor of Science"}]}
        mult = predictor._get_education_multiplier(bachelors_resume)
        assert mult == 1.0

    def test_calculate_confidence(self, predictor, sample_resume_data, sample_job_data):
        """Test confidence score calculation"""
        confidence = predictor._calculate_confidence(
            sample_resume_data, sample_job_data
        )

        assert 0 <= confidence <= 1
        assert confidence > 0.5  # Should be good with complete data

    def test_generate_market_comparison_with_data(self, predictor):
        """Test market comparison with data"""
        predicted_salary = {"avg": 100000}
        market_data = [{"salary": 90000}, {"salary": 110000}, {"salary": 95000}]

        comparison = predictor._generate_market_comparison(
            predicted_salary, market_data
        )

        assert comparison["available"] is True
        assert "market_stats" in comparison
        assert "prediction_vs_market" in comparison

        market_stats = comparison["market_stats"]
        assert "min" in market_stats
        assert "max" in market_stats
        assert "avg" in market_stats
        assert "median" in market_stats
        assert "count" in market_stats

    def test_generate_market_comparison_no_data(self, predictor):
        """Test market comparison without data"""
        predicted_salary = {"avg": 100000}

        comparison = predictor._generate_market_comparison(predicted_salary, None)

        assert comparison["available"] is False
        assert "message" in comparison

    def test_calculate_percentile(self, predictor):
        """Test percentile calculation"""
        data = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

        # Test various values
        assert predictor._calculate_percentile(25, data) == 20.0  # 2 out of 10
        assert predictor._calculate_percentile(50, data) == 50.0  # 5 out of 10
        assert predictor._calculate_percentile(75, data) == 80.0  # 8 out of 10

    def test_get_salary_factors(self, predictor, sample_resume_data, sample_job_data):
        """Test salary factors extraction"""
        factors = predictor._get_salary_factors(sample_resume_data, sample_job_data)

        assert "experience_level" in factors
        assert "location_impact" in factors
        assert "skill_impact" in factors
        assert "education_impact" in factors
        assert "industry_impact" in factors

    def test_get_location_impact(self, predictor):
        """Test location impact calculation"""
        job_data = {"location": "San Francisco, CA"}
        impact = predictor._get_location_impact(job_data)

        assert "location" in impact
        assert "multiplier" in impact
        assert "impact" in impact
        assert impact["multiplier"] == 1.5
        assert impact["impact"] == "High"

    def test_get_skill_impact(self, predictor, sample_resume_data):
        """Test skill impact calculation"""
        impact = predictor._get_skill_impact(sample_resume_data)

        assert "premium_skills" in impact
        assert "count" in impact
        assert "impact" in impact

    def test_get_education_impact(self, predictor, sample_resume_data):
        """Test education impact calculation"""
        impact = predictor._get_education_impact(sample_resume_data)

        assert "highest_degree" in impact
        assert "multiplier" in impact
        assert "impact" in impact

    def test_get_industry_impact(self, predictor):
        """Test industry impact calculation"""
        job_data = {"title": "Fintech Developer", "description": "Working in fintech"}
        impact = predictor._get_industry_impact(job_data)

        assert "industry" in impact
        assert "multiplier" in impact
        assert "impact" in impact
        assert impact["industry"] == "Fintech"

    def test_get_salary_insights(self, predictor, sample_resume_data):
        """Test salary insights generation"""
        jobs_data = [
            {
                "id": "job_1",
                "title": "Senior Python Developer",
                "company": "Tech Corp",
                "location": "San Francisco, CA",
            },
            {
                "id": "job_2",
                "title": "Full Stack Developer",
                "company": "Startup Inc",
                "location": "Remote",
            },
        ]

        insights = predictor.get_salary_insights(sample_resume_data, jobs_data)

        assert "total_jobs_analyzed" in insights
        assert "salary_range" in insights
        assert "top_paying_jobs" in insights
        assert "location_analysis" in insights
        assert "company_analysis" in insights
        assert "insights_generated_at" in insights

    def test_analyze_location_salaries(self, predictor):
        """Test location salary analysis"""
        predictions = [
            {"location": "San Francisco, CA", "predicted_salary": {"avg": 120000}},
            {"location": "Remote", "predicted_salary": {"avg": 90000}},
            {"location": "San Francisco, CA", "predicted_salary": {"avg": 130000}},
        ]

        analysis = predictor._analyze_location_salaries(predictions)

        assert "San Francisco, CA" in analysis
        assert "Remote" in analysis

        sf_analysis = analysis["San Francisco, CA"]
        assert "avg_salary" in sf_analysis
        assert "job_count" in sf_analysis
        assert "salary_range" in sf_analysis
        assert sf_analysis["job_count"] == 2

    def test_analyze_company_salaries(self, predictor):
        """Test company salary analysis"""
        predictions = [
            {"company": "Tech Corp", "predicted_salary": {"avg": 120000}},
            {"company": "Startup Inc", "predicted_salary": {"avg": 90000}},
            {"company": "Tech Corp", "predicted_salary": {"avg": 130000}},
        ]

        analysis = predictor._analyze_company_salaries(predictions)

        assert "Tech Corp" in analysis
        assert "Startup Inc" in analysis

        tech_analysis = analysis["Tech Corp"]
        assert "avg_salary" in tech_analysis
        assert "job_count" in tech_analysis
        assert "salary_range" in tech_analysis
        assert tech_analysis["job_count"] == 2

    def test_predict_salary_error_handling(self, predictor):
        """Test error handling in salary prediction"""
        # Test with invalid data
        invalid_resume = {"skills": "invalid"}
        invalid_job = {"description": None}

        result = predictor.predict_salary(invalid_resume, invalid_job)

        assert "error" in result
        assert "predicted_at" in result

    def test_salary_prediction_with_empty_data(self, predictor):
        """Test salary prediction with empty data"""
        empty_resume = {}
        empty_job = {}

        result = predictor.predict_salary(empty_resume, empty_job)

        assert "predicted_salary" in result
        assert "confidence_score" in result
        # Should still return a prediction (even if low confidence)

    def test_base_salary_ranges(self, predictor):
        """Test base salary ranges for different levels"""
        # Test that base salaries are reasonable
        for level, salary_range in predictor.base_salaries.items():
            assert salary_range["min"] > 0
            assert salary_range["max"] > salary_range["min"]
            assert salary_range["avg"] >= salary_range["min"]
            assert salary_range["avg"] <= salary_range["max"]

            # Test that higher levels have higher salaries
            if level != "entry":
                assert salary_range["min"] > 40000  # Minimum reasonable salary

    def test_multiplier_ranges(self, predictor):
        """Test that multipliers are reasonable"""
        # Test location multipliers
        for location, multiplier in predictor.location_multipliers.items():
            assert 0.3 <= multiplier <= 1.5  # Reasonable range

        # Test skill multipliers
        for skill, multiplier in predictor.skill_multipliers.items():
            assert 1.0 <= multiplier <= 1.2  # Reasonable range

        # Test industry multipliers
        for industry, multiplier in predictor.industry_multipliers.items():
            assert 0.9 <= multiplier <= 1.2  # Reasonable range

        # Test education multipliers
        for education, multiplier in predictor.education_multipliers.items():
            assert 0.85 <= multiplier <= 1.15  # Reasonable range

    def test_salary_insights_with_no_predictions(self, predictor, sample_resume_data):
        """Test salary insights with no valid predictions"""
        jobs_data = [
            {
                "id": "job_1",
                "title": "Invalid Job",
                "company": "Invalid Corp",
                "location": "Invalid Location",
            }
        ]

        insights = predictor.get_salary_insights(sample_resume_data, jobs_data)

        assert "error" in insights
        assert "insights_generated_at" in insights
