"""
Comprehensive Analysis Service

This service provides comprehensive analysis including job market analysis,
skill demand analysis, and career insights.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import Counter
import json

logger = logging.getLogger(__name__)

class ComprehensiveAnalysisService:
    """
    Comprehensive analysis service for job market insights and career guidance
    """
    
    def __init__(self, db=None):
        self.db = db
        
    def comprehensive_analysis(self, resume_data: Dict[str, Any], jobs_data: List[Dict[str, Any]], 
                             market_data: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Perform comprehensive analysis including parsing, matching, and salary prediction
        """
        try:
            # Validate input data
            if not resume_data:
                raise ValueError("Resume data is required")
            
            if not jobs_data:
                raise ValueError("Jobs data is required")
            
            # Analyze resume
            resume_summary = self._analyze_resume(resume_data)
            
            # Analyze job market
            market_analysis = self._analyze_job_market(jobs_data, market_data)
            
            # Get job recommendations
            job_recommendations = self._get_job_recommendations(resume_data, jobs_data)
            
            # Get salary insights
            salary_insights = self._get_salary_insights(resume_data, jobs_data)
            
            # Generate career recommendations
            career_recommendations = self._generate_career_recommendations(resume_data, jobs_data)
            
            return {
                'resume_summary': resume_summary,
                'job_recommendations': job_recommendations,
                'salary_insights': salary_insights,
                'market_analysis': market_analysis,
                'career_recommendations': career_recommendations,
                'analysis_generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error performing comprehensive analysis: {str(e)}")
            raise
    
    def analyze_job_market(self, jobs_data: List[Dict[str, Any]], 
                          filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze job market trends and insights
        """
        try:
            if not jobs_data:
                return {
                    "total_jobs": 0,
                    "remote_jobs_percentage": 0,
                    "top_companies": [],
                    "salary_trends": {"average_salary": 0, "salary_range": {"min": 0, "max": 0}},
                    "job_categories": [],
                    "analysis_date": datetime.now().isoformat()
                }
            
            # Apply filters if provided
            filtered_jobs = self._apply_filters(jobs_data, filters)
            
            # Calculate basic statistics
            total_jobs = len(filtered_jobs)
            remote_jobs = [job for job in filtered_jobs if job.get('remote', False)]
            remote_percentage = (len(remote_jobs) / total_jobs * 100) if total_jobs > 0 else 0
            
            # Top companies
            companies = [job.get('company', 'Unknown') for job in filtered_jobs]
            company_counts = Counter(companies)
            top_companies = [{"company": company, "job_count": count} 
                           for company, count in company_counts.most_common(10)]
            
            # Salary analysis
            salaries = [job.get('salary', {}).get('max', 0) for job in filtered_jobs 
                       if job.get('salary', {}).get('max', 0) > 0]
            avg_salary = sum(salaries) / len(salaries) if salaries else 0
            salary_range = {"min": min(salaries) if salaries else 0, 
                          "max": max(salaries) if salaries else 0}
            
            # Job categories
            categories = [job.get('category', 'Other') for job in filtered_jobs]
            category_counts = Counter(categories)
            job_categories = [{"category": category, "count": count} 
                            for category, count in category_counts.most_common(10)]
            
            return {
                "total_jobs": total_jobs,
                "remote_jobs_percentage": round(remote_percentage, 2),
                "top_companies": top_companies,
                "salary_trends": {
                    "average_salary": round(avg_salary, 2),
                    "salary_range": salary_range
                },
                "job_categories": job_categories,
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing job market: {str(e)}")
            raise
    
    def analyze_skills_demand(self, jobs_data: List[Dict[str, Any]], 
                            filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze skills demand in the job market
        """
        try:
            if not jobs_data:
                return {
                    "most_demanded_skills": [],
                    "emerging_skills": [],
                    "skill_categories": {},
                    "analysis_date": datetime.now().isoformat()
                }
            
            # Apply filters
            filtered_jobs = self._apply_filters(jobs_data, filters)
            
            # Extract skills from job descriptions
            all_skills = []
            for job in filtered_jobs:
                skills = job.get('skills', [])
                if isinstance(skills, list):
                    all_skills.extend(skills)
                elif isinstance(skills, str):
                    all_skills.extend([s.strip() for s in skills.split(',')])
            
            # Count skill occurrences
            skill_counts = Counter(all_skills)
            
            # Most demanded skills
            most_demanded = [
                {"skill": skill, "demand_score": count / len(filtered_jobs), "job_count": count}
                for skill, count in skill_counts.most_common(20)
            ]
            
            # Emerging skills (skills with recent mentions)
            emerging_skills = [
                {"skill": skill, "growth_rate": count / len(filtered_jobs), "job_count": count}
                for skill, count in skill_counts.most_common(10)
                if count / len(filtered_jobs) > 0.1  # At least 10% of jobs mention this skill
            ]
            
            # Categorize skills
            skill_categories = self._categorize_skills(list(skill_counts.keys()))
            
            return {
                "most_demanded_skills": most_demanded,
                "emerging_skills": emerging_skills,
                "skill_categories": skill_categories,
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing skills demand: {str(e)}")
            raise
    
    def _analyze_resume(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze resume data and extract insights"""
        skills = resume_data.get('skills', [])
        experience = resume_data.get('experience', [])
        
        # Calculate total experience
        total_experience = 0
        for exp in experience:
            if isinstance(exp, dict):
                duration = exp.get('duration', '')
                if duration:
                    # Simple duration parsing
                    if 'year' in duration.lower():
                        total_experience += 1
        
        return {
            "total_skills": len(skills),
            "experience_years": total_experience,
            "skill_match_percentage": 0,  # Will be calculated later
            "top_skills": skills[:5] if skills else []
        }
    
    def _get_job_recommendations(self, resume_data: Dict[str, Any], 
                                jobs_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get job recommendations based on resume"""
        skills = resume_data.get('skills', [])
        recommendations = []
        
        for job in jobs_data[:10]:  # Top 10 jobs
            job_skills = job.get('skills', [])
            if isinstance(job_skills, str):
                job_skills = [s.strip() for s in job_skills.split(',')]
            
            # Calculate match score
            common_skills = set(skills) & set(job_skills)
            match_score = len(common_skills) / max(len(skills), 1) if skills else 0
            
            recommendations.append({
                "job_id": job.get('id', ''),
                "title": job.get('title', ''),
                "match_score": round(match_score, 2),
                "company": job.get('company', ''),
                "salary_range": job.get('salary', {}).get('range', ''),
                "common_skills": list(common_skills)
            })
        
        # Sort by match score
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        return recommendations[:5]
    
    def _get_salary_insights(self, resume_data: Dict[str, Any], 
                           jobs_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get salary insights based on resume and job data"""
        salaries = []
        for job in jobs_data:
            salary = job.get('salary', {})
            if salary.get('max', 0) > 0:
                salaries.append(salary['max'])
        
        if not salaries:
            return {
                "predicted_salary": 0,
                "market_average": 0,
                "percentile": 0
            }
        
        avg_salary = sum(salaries) / len(salaries)
        predicted_salary = avg_salary * 1.1  # 10% premium for good candidates
        
        return {
            "predicted_salary": round(predicted_salary, 2),
            "market_average": round(avg_salary, 2),
            "percentile": 75  # Estimated percentile
        }
    
    def _generate_career_recommendations(self, resume_data: Dict[str, Any], 
                                       jobs_data: List[Dict[str, Any]]) -> List[str]:
        """Generate career recommendations"""
        recommendations = []
        
        # Basic recommendations
        recommendations.append("Consider learning cloud technologies")
        recommendations.append("Focus on system design skills")
        recommendations.append("Network with remote-first companies")
        
        # Skill-based recommendations
        skills = resume_data.get('skills', [])
        if 'python' in [s.lower() for s in skills]:
            recommendations.append("Consider specializing in data science or AI")
        
        if len(skills) < 5:
            recommendations.append("Expand your technical skill set")
        
        return recommendations[:5]
    
    def _apply_filters(self, jobs_data: List[Dict[str, Any]], 
                      filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Apply filters to job data"""
        if not filters:
            return jobs_data
        
        filtered_jobs = jobs_data
        
        # Location filter
        if 'location' in filters:
            location = filters['location'].lower()
            filtered_jobs = [job for job in filtered_jobs 
                           if location in job.get('location', '').lower()]
        
        # Job type filter
        if 'job_type' in filters:
            job_type = filters['job_type'].lower()
            filtered_jobs = [job for job in filtered_jobs 
                           if job_type in job.get('type', '').lower()]
        
        # Experience level filter
        if 'experience_level' in filters:
            level = filters['experience_level'].lower()
            filtered_jobs = [job for job in filtered_jobs 
                           if level in job.get('experience_level', '').lower()]
        
        return filtered_jobs
    
    def _categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize skills into different groups"""
        categories = {
            "programming_languages": [],
            "frameworks": [],
            "databases": [],
            "cloud_platforms": [],
            "tools": []
        }
        
        for skill in skills:
            skill_lower = skill.lower()
            
            # Programming languages
            if skill_lower in ['python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust']:
                categories["programming_languages"].append(skill)
            
            # Frameworks
            elif skill_lower in ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'express']:
                categories["frameworks"].append(skill)
            
            # Databases
            elif skill_lower in ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch']:
                categories["databases"].append(skill)
            
            # Cloud platforms
            elif skill_lower in ['aws', 'azure', 'gcp', 'docker', 'kubernetes']:
                categories["cloud_platforms"].append(skill)
            
            # Tools
            else:
                categories["tools"].append(skill)
        
        return categories 