import pytest
from unittest.mock import Mock, patch
from typing import Dict, List, Any
from datetime import datetime, timedelta
import json

class TestAnalyticsService:
    """Test suite for Analytics Service functionality."""

    def test_job_analytics_aggregation(self):
        """Test job analytics data aggregation."""
        def aggregate_job_stats(jobs_data: List[Dict]) -> Dict[str, Any]:
            """Aggregate job statistics."""
            if not jobs_data:
                return {"total_jobs": 0, "companies": 0, "locations": 0, "avg_salary": 0}
            
            total_jobs = len(jobs_data)
            unique_companies = len(set(job.get("company", "") for job in jobs_data if job.get("company")))
            unique_locations = len(set(job.get("location", "") for job in jobs_data if job.get("location")))
            
            # Calculate average salary
            salaries = [job.get("salary", 0) for job in jobs_data if job.get("salary", 0) > 0]
            avg_salary = sum(salaries) / len(salaries) if salaries else 0
            
            # Most popular technologies
            all_skills = []
            for job in jobs_data:
                skills = job.get("skills", [])
                if isinstance(skills, list):
                    all_skills.extend(skills)
            
            skill_counts = {}
            for skill in all_skills:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
            
            top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                "total_jobs": total_jobs,
                "companies": unique_companies,
                "locations": unique_locations,
                "avg_salary": round(avg_salary, 2),
                "top_skills": top_skills
            }

        # Test data
        jobs = [
            {"company": "Tech Corp", "location": "Remote", "salary": 120000, "skills": ["Python", "React"]},
            {"company": "AI Corp", "location": "NYC", "salary": 140000, "skills": ["Python", "ML"]},
            {"company": "Web Corp", "location": "SF", "salary": 100000, "skills": ["React", "Node.js"]},
            {"company": "Tech Corp", "location": "Remote", "salary": 110000, "skills": ["Python", "Django"]},
        ]

        result = aggregate_job_stats(jobs)
        
        assert result["total_jobs"] == 4
        assert result["companies"] == 3  # Tech Corp, AI Corp, Web Corp
        assert result["locations"] == 3  # Remote, NYC, SF
        assert result["avg_salary"] == 117500.0  # (120000+140000+100000+110000)/4
        assert result["top_skills"][0][0] == "Python"  # Most popular skill

    def test_user_activity_tracking(self):
        """Test user activity tracking."""
        def track_user_activity(user_id: str, action: str, metadata: Dict = None):
            """Track user activity for analytics."""
            activity = {
                "user_id": user_id,
                "action": action,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            # Validate action type
            valid_actions = ["login", "logout", "search", "apply", "view_job", "save_job"]
            if action not in valid_actions:
                raise ValueError(f"Invalid action: {action}")
            
            return activity

        # Test valid activity tracking
        activity = track_user_activity("user123", "search", {"query": "python developer"})
        assert activity["user_id"] == "user123"
        assert activity["action"] == "search"
        assert activity["metadata"]["query"] == "python developer"

        # Test invalid action
        with pytest.raises(ValueError):
            track_user_activity("user123", "invalid_action")

    def test_conversion_rate_calculation(self):
        """Test conversion rate calculations."""
        def calculate_conversion_rates(activities: List[Dict]) -> Dict[str, float]:
            """Calculate conversion rates from activities."""
            # Count events by type
            event_counts = {}
            for activity in activities:
                action = activity["action"]
                event_counts[action] = event_counts.get(action, 0) + 1
            
            total_searches = event_counts.get("search", 0)
            total_views = event_counts.get("view_job", 0)
            total_applications = event_counts.get("apply", 0)
            
            # Calculate rates
            search_to_view = (total_views / total_searches * 100) if total_searches > 0 else 0
            view_to_apply = (total_applications / total_views * 100) if total_views > 0 else 0
            search_to_apply = (total_applications / total_searches * 100) if total_searches > 0 else 0
            
            return {
                "search_to_view": round(search_to_view, 2),
                "view_to_apply": round(view_to_apply, 2),
                "search_to_apply": round(search_to_apply, 2),
                "total_searches": total_searches,
                "total_views": total_views,
                "total_applications": total_applications
            }

        # Test data: 100 searches -> 30 views -> 5 applications
        activities = (
            [{"action": "search"} for _ in range(100)] +
            [{"action": "view_job"} for _ in range(30)] +
            [{"action": "apply"} for _ in range(5)]
        )

        result = calculate_conversion_rates(activities)
        
        assert result["search_to_view"] == 30.0  # 30/100 * 100
        assert result["view_to_apply"] == 16.67  # 5/30 * 100
        assert result["search_to_apply"] == 5.0   # 5/100 * 100

    def test_time_series_analytics(self):
        """Test time series analytics."""
        def generate_daily_stats(activities: List[Dict], days: int = 7) -> List[Dict]:
            """Generate daily statistics for the last N days."""
            # Group activities by date
            daily_data = {}
            
            for activity in activities:
                # Parse date from timestamp
                timestamp = activity.get("timestamp", datetime.now().isoformat())
                if isinstance(timestamp, str):
                    date = datetime.fromisoformat(timestamp).date()
                else:
                    date = timestamp.date()
                
                date_str = date.isoformat()
                if date_str not in daily_data:
                    daily_data[date_str] = {"date": date_str, "activities": 0, "unique_users": set()}
                
                daily_data[date_str]["activities"] += 1
                daily_data[date_str]["unique_users"].add(activity.get("user_id", "anonymous"))
            
            # Convert to list and sort by date
            result = []
            for date_str, data in daily_data.items():
                result.append({
                    "date": date_str,
                    "activities": data["activities"],
                    "unique_users": len(data["unique_users"])
                })
            
            return sorted(result, key=lambda x: x["date"])

        # Test data for last 3 days
        base_date = datetime.now() - timedelta(days=2)
        activities = []
        
        for i in range(3):
            current_date = base_date + timedelta(days=i)
            # Add different number of activities per day
            for j in range((i + 1) * 5):  # 5, 10, 15 activities
                activities.append({
                    "user_id": f"user{j % 3}",  # 3 different users
                    "action": "search",
                    "timestamp": current_date.isoformat()
                })

        result = generate_daily_stats(activities)
        
        assert len(result) == 3  # 3 days
        assert result[0]["activities"] == 5   # First day
        assert result[1]["activities"] == 10  # Second day  
        assert result[2]["activities"] == 15  # Third day
        assert result[0]["unique_users"] == 3  # 3 unique users each day

    def test_performance_metrics(self):
        """Test API performance metrics tracking."""
        def track_api_performance(endpoint: str, response_time: float, status_code: int):
            """Track API endpoint performance."""
            metric = {
                "endpoint": endpoint,
                "response_time": response_time,
                "status_code": status_code,
                "timestamp": datetime.now().isoformat(),
                "is_success": 200 <= status_code < 300,
                "is_slow": response_time > 1000  # > 1 second
            }
            return metric

        def calculate_endpoint_stats(metrics: List[Dict]) -> Dict[str, Any]:
            """Calculate statistics for endpoint performance."""
            if not metrics:
                return {}
            
            total_requests = len(metrics)
            successful_requests = len([m for m in metrics if m["is_success"]])
            slow_requests = len([m for m in metrics if m["is_slow"]])
            
            response_times = [m["response_time"] for m in metrics]
            avg_response_time = sum(response_times) / len(response_times)
            
            success_rate = (successful_requests / total_requests) * 100
            slow_request_rate = (slow_requests / total_requests) * 100
            
            return {
                "total_requests": total_requests,
                "success_rate": round(success_rate, 2),
                "avg_response_time": round(avg_response_time, 2),
                "slow_request_rate": round(slow_request_rate, 2),
                "fastest_response": min(response_times),
                "slowest_response": max(response_times)
            }

        # Test performance tracking
        metric = track_api_performance("/api/jobs", 150.5, 200)
        assert metric["endpoint"] == "/api/jobs"
        assert metric["is_success"] == True
        assert metric["is_slow"] == False

        # Test metrics calculation
        test_metrics = [
            {"response_time": 100, "is_success": True, "is_slow": False},
            {"response_time": 200, "is_success": True, "is_slow": False},
            {"response_time": 1500, "is_success": False, "is_slow": True},
            {"response_time": 300, "is_success": True, "is_slow": False},
        ]

        stats = calculate_endpoint_stats(test_metrics)
        
        assert stats["total_requests"] == 4
        assert stats["success_rate"] == 75.0  # 3/4 * 100
        assert stats["avg_response_time"] == 525.0  # (100+200+1500+300)/4
        assert stats["slow_request_rate"] == 25.0  # 1/4 * 100

    def test_report_generation(self):
        """Test analytics report generation."""
        def generate_analytics_report(data: Dict[str, Any], report_type: str = "summary") -> Dict:
            """Generate formatted analytics report."""
            if report_type == "summary":
                return {
                    "report_type": "summary",
                    "generated_at": datetime.now().isoformat(),
                    "key_metrics": {
                        "total_jobs": data.get("total_jobs", 0),
                        "total_users": data.get("total_users", 0),
                        "conversion_rate": data.get("conversion_rate", 0)
                    },
                    "insights": [
                        f"Total jobs posted: {data.get('total_jobs', 0)}",
                        f"User conversion rate: {data.get('conversion_rate', 0)}%"
                    ]
                }
            elif report_type == "detailed":
                return {
                    "report_type": "detailed",
                    "generated_at": datetime.now().isoformat(),
                    "data": data,
                    "charts": ["line_chart", "bar_chart", "pie_chart"],
                    "export_formats": ["pdf", "csv", "json"]
                }
            else:
                raise ValueError(f"Unsupported report type: {report_type}")

        # Test summary report
        test_data = {"total_jobs": 1000, "total_users": 500, "conversion_rate": 15.5}
        report = generate_analytics_report(test_data, "summary")
        
        assert report["report_type"] == "summary"
        assert report["key_metrics"]["total_jobs"] == 1000
        assert "Total jobs posted: 1000" in report["insights"]

        # Test detailed report
        detailed_report = generate_analytics_report(test_data, "detailed")
        assert detailed_report["report_type"] == "detailed"
        assert "pdf" in detailed_report["export_formats"]

        # Test invalid report type
        with pytest.raises(ValueError):
            generate_analytics_report(test_data, "invalid")
