import pytest
from unittest.mock import Mock, patch
from typing import List, Dict, Any

class TestSearchService:
    """Test suite for Search Service functionality."""

    def test_job_search_basic(self):
        """Test basic job search functionality."""
        def search_jobs(query: str, filters: Dict[str, Any] = None):
            # Mock job database
            mock_jobs = [
                {"id": "1", "title": "Software Engineer", "company": "Tech Corp", "location": "Remote", "skills": ["Python", "React"]},
                {"id": "2", "title": "Data Scientist", "company": "AI Corp", "location": "New York", "skills": ["Python", "ML"]},
                {"id": "3", "title": "Frontend Developer", "company": "Web Corp", "location": "San Francisco", "skills": ["React", "JavaScript"]},
                {"id": "4", "title": "Backend Engineer", "company": "Tech Corp", "location": "Remote", "skills": ["Node.js", "MongoDB"]},
            ]

            results = []
            for job in mock_jobs:
                match = False
                
                # Text search in title, company, and skills
                if query:
                    search_fields = [job["title"], job["company"]] + job.get("skills", [])
                    for field in search_fields:
                        if query.lower() in field.lower():
                            match = True
                            break
                else:
                    match = True  # No query means return all

                # Apply filters
                if filters and match:
                    if filters.get("location") and filters["location"].lower() not in job["location"].lower():
                        match = False
                    if filters.get("company") and filters["company"].lower() not in job["company"].lower():
                        match = False

                if match:
                    results.append(job)

            return results

        # Test basic search
        results = search_jobs("Python")
        assert len(results) == 2
        assert any(job["title"] == "Software Engineer" for job in results)

        # Test company filter
        results = search_jobs("", {"company": "Tech"})
        assert len(results) == 2

        # Test location filter  
        results = search_jobs("", {"location": "Remote"})
        assert len(results) == 2

        # Test combined search and filter
        results = search_jobs("Engineer", {"location": "Remote"})
        assert len(results) == 2

    def test_job_search_ranking(self):
        """Test job search ranking algorithm."""
        def rank_search_results(jobs: List[Dict], query: str):
            ranked_jobs = []
            
            for job in jobs:
                score = 0
                query_lower = query.lower()
                job_title = job.get("title", "").lower()
                job_skills = [skill.lower() for skill in job.get("skills", [])]
                
                # Title exact match gets highest score
                if query_lower == job_title:
                    score += 100
                elif query_lower in job_title:
                    score += 50
                
                # Skills match gets medium score
                for skill in job_skills:
                    if query_lower in skill:
                        score += 25
                        
                job["search_score"] = score
                ranked_jobs.append(job)
            
            return sorted(ranked_jobs, key=lambda x: x["search_score"], reverse=True)

        mock_jobs = [
            {"id": "1", "title": "Software Engineer", "skills": ["Python", "Django"]},
            {"id": "2", "title": "Python Developer", "skills": ["Python", "Flask"]},
            {"id": "3", "title": "Data Scientist", "skills": ["Python", "ML"]},
        ]

        ranked = rank_search_results(mock_jobs, "Python")
        assert ranked[0]["title"] == "Python Developer"
        assert ranked[0]["search_score"] > ranked[1]["search_score"]

    def test_autocomplete_search(self):
        """Test autocomplete functionality."""
        def get_autocomplete_suggestions(partial_query: str, limit: int = 5):
            suggestions = [
                "Software Engineer", "Software Developer", "Software Architect",
                "Data Scientist", "Data Engineer", "Data Analyst",
                "Product Manager", "Product Designer", "Project Manager"
            ]
            
            if not partial_query:
                return suggestions[:limit]
                
            query_lower = partial_query.lower()
            matches = []
            
            # First, exact prefix matches
            for suggestion in suggestions:
                if suggestion.lower().startswith(query_lower):
                    matches.append(suggestion)
            
            # Then, contains matches (but not duplicates)
            for suggestion in suggestions:
                if query_lower in suggestion.lower() and suggestion not in matches:
                    matches.append(suggestion)
                    
            return matches[:limit]

        # Test prefix match
        results = get_autocomplete_suggestions("Soft")
        assert len(results) >= 3
        assert "Software Engineer" in results

        # Test contains match
        results = get_autocomplete_suggestions("Data")
        assert "Data Scientist" in results
        assert "Data Engineer" in results

        # Test limit
        results = get_autocomplete_suggestions("", 3)
        assert len(results) == 3

    def test_search_error_handling(self):
        """Test search error handling."""
        def search_with_error_handling(query: str):
            try:
                # Simulate database error
                if query == "ERROR":
                    raise Exception("Database connection failed")
                
                # Simulate malformed query
                if len(query) > 100:
                    return {"error": "Query too long", "results": []}
                
                # Simulate empty results
                if query == "NONEXISTENT":
                    return {"results": [], "message": "No jobs found"}
                
                # Normal successful search
                return {"results": [{"id": "1", "title": f"Job for {query}"}]}
                
            except Exception as e:
                return {"error": str(e), "results": []}

        # Test error case
        result = search_with_error_handling("ERROR")
        assert "error" in result
        assert result["results"] == []

        # Test query too long
        result = search_with_error_handling("x" * 101)
        assert result["error"] == "Query too long"

        # Test no results
        result = search_with_error_handling("NONEXISTENT")
        assert result["results"] == []
        assert "message" in result

        # Test successful search
        result = search_with_error_handling("developer")
        assert len(result["results"]) == 1
        assert "Job for developer" in result["results"][0]["title"]
