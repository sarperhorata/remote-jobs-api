import json
from datetime import datetime

import pytest


class TestDataProcessingService:
    """Test suite for Data Processing Service functionality."""

    def test_json_data_validation(self):
        """Test JSON data validation and parsing."""

        def validate_json_data(json_string):
            try:
                data = json.loads(json_string)
                return {"valid": True, "data": data}
            except json.JSONDecodeError as e:
                return {"valid": False, "error": str(e)}

        # Test valid JSON
        valid_json = '{"name": "John", "age": 30, "active": true}'
        result = validate_json_data(valid_json)
        assert result["valid"] is True
        assert result["data"]["name"] == "John"

        # Test invalid JSON
        invalid_json = '{"name": "John", "age": 30,'
        result = validate_json_data(invalid_json)
        assert result["valid"] is False
        assert "error" in result

    def test_data_transformation(self):
        """Test data transformation and normalization."""

        def transform_user_data(raw_data):
            transformed = {}

            if "email" in raw_data:
                transformed["email"] = raw_data["email"].lower().strip()

            if "phone" in raw_data:
                phone = raw_data["phone"]
                normalized_phone = "".join(c for c in phone if c.isdigit() or c == "+")
                transformed["phone"] = normalized_phone

            if "name" in raw_data:
                transformed["name"] = raw_data["name"].strip().title()

            transformed["processed_at"] = datetime.now().isoformat()

            return transformed

        raw_data = {
            "email": "  JOHN.DOE@EXAMPLE.COM  ",
            "phone": "(555) 123-4567",
            "name": "john doe",
        }

        result = transform_user_data(raw_data)

        assert result["email"] == "john.doe@example.com"
        assert result["phone"] == "5551234567"
        assert result["name"] == "John Doe"
        assert "processed_at" in result

    def test_data_filtering(self):
        """Test data filtering functionality."""

        def filter_jobs(jobs, filters):
            filtered = []

            for job in jobs:
                include = True

                if (
                    filters.get("location")
                    and filters["location"].lower()
                    not in job.get("location", "").lower()
                ):
                    include = False

                if (
                    filters.get("company")
                    and filters["company"].lower() not in job.get("company", "").lower()
                ):
                    include = False

                if filters.get("min_salary"):
                    job_salary = job.get("salary", 0)
                    if job_salary < filters["min_salary"]:
                        include = False

                if include:
                    filtered.append(job)

            return filtered

        jobs = [
            {
                "title": "Software Engineer",
                "company": "Tech Corp",
                "location": "Remote",
                "salary": 80000,
            },
            {
                "title": "Data Scientist",
                "company": "DataCorp",
                "location": "New York",
                "salary": 90000,
            },
            {
                "title": "Frontend Developer",
                "company": "WebCorp",
                "location": "Remote",
                "salary": 70000,
            },
        ]

        remote_jobs = filter_jobs(jobs, {"location": "remote"})
        assert len(remote_jobs) == 2

        high_salary_jobs = filter_jobs(jobs, {"min_salary": 75000})
        assert len(high_salary_jobs) == 2

    def test_data_sorting(self):
        """Test data sorting functionality."""

        def sort_jobs(jobs, sort_by="title", reverse=False):
            if sort_by == "salary":
                return sorted(jobs, key=lambda x: x.get("salary", 0), reverse=reverse)
            elif sort_by == "company":
                return sorted(jobs, key=lambda x: x.get("company", ""), reverse=reverse)
            else:
                return sorted(jobs, key=lambda x: x.get("title", ""), reverse=reverse)

        jobs = [
            {"title": "Zebra Developer", "company": "Alpha Corp", "salary": 70000},
            {"title": "Alpha Engineer", "company": "Zebra Corp", "salary": 90000},
            {"title": "Beta Analyst", "company": "Beta Corp", "salary": 80000},
        ]

        sorted_by_title = sort_jobs(jobs, "title")
        assert sorted_by_title[0]["title"] == "Alpha Engineer"

        sorted_by_salary = sort_jobs(jobs, "salary", reverse=True)
        assert sorted_by_salary[0]["salary"] == 90000

    def test_data_pagination(self):
        """Test data pagination functionality."""

        def paginate_data(data, page=1, per_page=10):
            total_items = len(data)
            total_pages = (total_items + per_page - 1) // per_page

            start_index = (page - 1) * per_page
            end_index = start_index + per_page

            paginated_data = data[start_index:end_index]

            return {
                "data": paginated_data,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total_items": total_items,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1,
                },
            }

        test_data = [{"id": i, "name": f"Item {i}"} for i in range(1, 26)]

        result = paginate_data(test_data, page=1, per_page=10)
        assert len(result["data"]) == 10
        assert result["pagination"]["page"] == 1
        assert result["pagination"]["total_pages"] == 3
        assert result["pagination"]["has_next"] is True
        assert result["pagination"]["has_prev"] is False

    def test_duplicate_detection(self):
        """Test duplicate data detection."""

        def find_duplicates(data, key_field):
            seen = {}
            duplicates = []

            for item in data:
                key_value = item.get(key_field)
                if key_value in seen:
                    duplicates.append({"duplicate": item, "original": seen[key_value]})
                else:
                    seen[key_value] = item

            return duplicates

        test_data = [
            {"id": 1, "email": "john@example.com", "name": "John Doe"},
            {"id": 2, "email": "jane@example.com", "name": "Jane Smith"},
            {"id": 3, "email": "john@example.com", "name": "John Doe"},
            {"id": 4, "email": "bob@example.com", "name": "Bob Johnson"},
        ]

        duplicates = find_duplicates(test_data, "email")

        assert len(duplicates) == 1
        assert duplicates[0]["duplicate"]["id"] == 3
        assert duplicates[0]["original"]["id"] == 1

    def test_data_validation_rules(self):
        """Test data validation against business rules."""

        def validate_job_posting(job_data):
            errors = []

            required_fields = ["title", "company", "description"]
            for field in required_fields:
                if not job_data.get(field):
                    errors.append(f"Missing required field: {field}")

            title = job_data.get("title", "")
            if title and len(title) < 5:
                errors.append("Title must be at least 5 characters long")

            salary = job_data.get("salary")
            if salary is not None:
                if not isinstance(salary, (int, float)) or salary < 0:
                    errors.append("Salary must be a positive number")

            return {"valid": len(errors) == 0, "errors": errors}

        valid_job = {
            "title": "Software Engineer",
            "company": "Tech Corp",
            "description": "Exciting opportunity for a software engineer",
            "salary": 75000,
        }

        result = validate_job_posting(valid_job)
        assert result["valid"] is True
        assert len(result["errors"]) == 0

        invalid_job = {
            "title": "SE",
            "company": "",
            "description": "Good job",
            "salary": -1000,
        }

        result = validate_job_posting(invalid_job)
        assert result["valid"] is False
        assert len(result["errors"]) > 0
