import logging
import re
import statistics
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import math

logger = logging.getLogger(__name__)

class SalaryPredictionService:
    """
    Salary prediction service that estimates salary ranges based on resume and job data
    """
    
    def __init__(self):
        # Base salary ranges by experience level (USD)
        self.base_salaries = {
            'entry': {'min': 40000, 'max': 60000, 'avg': 50000},
            'junior': {'min': 50000, 'max': 80000, 'avg': 65000},
            'mid': {'min': 70000, 'max': 120000, 'avg': 95000},
            'senior': {'min': 100000, 'max': 180000, 'avg': 140000},
            'lead': {'min': 130000, 'max': 220000, 'avg': 175000},
            'manager': {'min': 150000, 'max': 300000, 'avg': 225000},
            'director': {'min': 200000, 'max': 400000, 'avg': 300000},
            'executive': {'min': 300000, 'max': 1000000, 'avg': 650000}
        }
        
        # Location multipliers (cost of living adjustments)
        self.location_multipliers = {
            'san francisco': 1.5,
            'new york': 1.4,
            'seattle': 1.3,
            'boston': 1.3,
            'los angeles': 1.2,
            'chicago': 1.1,
            'austin': 1.0,
            'denver': 1.0,
            'atlanta': 0.9,
            'dallas': 0.9,
            'phoenix': 0.8,
            'miami': 0.8,
            'remote': 0.9,
            'istanbul': 0.4,
            'ankara': 0.35,
            'izmir': 0.35,
            'berlin': 0.8,
            'munich': 0.9,
            'london': 1.1,
            'paris': 0.9,
            'amsterdam': 0.8
        }
        
        # Skill multipliers (premium skills that increase salary)
        self.skill_multipliers = {
            'machine learning': 1.2,
            'ai': 1.2,
            'data science': 1.15,
            'blockchain': 1.1,
            'cybersecurity': 1.1,
            'devops': 1.05,
            'cloud': 1.05,
            'kubernetes': 1.05,
            'docker': 1.03,
            'aws': 1.03,
            'azure': 1.03,
            'gcp': 1.03,
            'react': 1.02,
            'python': 1.02,
            'javascript': 1.01
        }
        
        # Industry multipliers
        self.industry_multipliers = {
            'fintech': 1.15,
            'healthcare': 1.1,
            'ai/ml': 1.2,
            'cybersecurity': 1.1,
            'gaming': 1.05,
            'ecommerce': 1.0,
            'saas': 1.05,
            'consulting': 1.1,
            'startup': 0.9,
            'enterprise': 1.1
        }
        
        # Education multipliers
        self.education_multipliers = {
            'phd': 1.15,
            'master': 1.1,
            'bachelor': 1.0,
            'associate': 0.9,
            'diploma': 0.85
        }

    def predict_salary(self, resume_data: Dict[str, Any], job_data: Dict[str, Any], 
                      market_data: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Predict salary range based on resume and job data
        
        Args:
            resume_data: Parsed resume data
            job_data: Job posting data
            market_data: Optional market data for comparison
            
        Returns:
            Dictionary containing salary prediction and analysis
        """
        try:
            # Calculate base salary
            base_salary = self._calculate_base_salary(resume_data, job_data)
            
            # Apply multipliers
            adjusted_salary = self._apply_multipliers(base_salary, resume_data, job_data)
            
            # Calculate confidence score
            confidence = self._calculate_confidence(resume_data, job_data)
            
            # Generate market comparison if data available
            market_comparison = self._generate_market_comparison(adjusted_salary, market_data)
            
            return {
                'predicted_salary': adjusted_salary,
                'confidence_score': confidence,
                'market_comparison': market_comparison,
                'factors': self._get_salary_factors(resume_data, job_data),
                'predicted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error predicting salary: {str(e)}")
            return {
                'error': str(e),
                'predicted_at': datetime.now().isoformat()
            }

    def _calculate_base_salary(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate base salary based on experience level"""
        # Determine experience level
        experience_level = self._determine_experience_level(resume_data, job_data)
        
        # Get base salary for the level
        base_salary = self.base_salaries.get(experience_level, self.base_salaries['mid'])
        
        return {
            'min': base_salary['min'],
            'max': base_salary['max'],
            'avg': base_salary['avg'],
            'level': experience_level
        }

    def _determine_experience_level(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> str:
        """Determine experience level from resume and job data"""
        # Check job requirements first
        job_level = self._extract_job_level(job_data)
        
        # Check resume experience
        resume_experience = resume_data.get('experience', [])
        if resume_experience:
            total_years = self._calculate_total_experience_years(resume_experience)
            resume_level = self._map_years_to_level(total_years)
            
            # Use the higher level between job requirements and resume experience
            level_weights = {
                'entry': 1, 'junior': 2, 'mid': 3, 'senior': 4, 
                'lead': 5, 'manager': 6, 'director': 7, 'executive': 8
            }
            
            job_weight = level_weights.get(job_level, 3)
            resume_weight = level_weights.get(resume_level, 3)
            
            return job_level if job_weight >= resume_weight else resume_level
        
        return job_level

    def _extract_job_level(self, job_data: Dict[str, Any]) -> str:
        """Extract job level from job data"""
        title = job_data.get('title', '').lower()
        description = job_data.get('description', '').lower()
        
        level_keywords = {
            'entry': ['entry', 'junior', 'graduate', 'intern', 'trainee', '0-1', '0-2'],
            'junior': ['junior', 'entry', '1-2', '1-3', '2-3'],
            'mid': ['mid', 'middle', 'intermediate', '3-5', '4-6', '5-7'],
            'senior': ['senior', '5+', '6+', '7+', '8+'],
            'lead': ['lead', 'team lead', 'technical lead'],
            'manager': ['manager', 'management', 'team manager'],
            'director': ['director', 'head of', 'vp'],
            'executive': ['executive', 'ceo', 'cto', 'cfo', 'president']
        }
        
        for level, keywords in level_keywords.items():
            for keyword in keywords:
                if keyword in title or keyword in description:
                    return level
        
        return 'mid'

    def _calculate_total_experience_years(self, experience: List[Dict[str, str]]) -> float:
        """Calculate total years of experience"""
        total_years = 0
        
        for exp in experience:
            start_date = exp.get('start_date')
            end_date = exp.get('end_date')
            duration = exp.get('duration')
            
            if duration:
                duration_match = re.search(r'(\d+)', duration)
                if duration_match:
                    total_years += float(duration_match.group(1))
            elif start_date and end_date:
                try:
                    start_year = int(start_date)
                    if end_date.lower() in ['present', 'current', 'now']:
                        end_year = datetime.now().year
                    else:
                        end_year = int(end_date)
                    total_years += (end_year - start_year)
                except (ValueError, TypeError):
                    continue
        
        return total_years

    def _map_years_to_level(self, years: float) -> str:
        """Map years of experience to level"""
        if years < 1:
            return 'entry'
        elif years < 3:
            return 'junior'
        elif years < 5:
            return 'mid'
        elif years < 8:
            return 'senior'
        elif years < 12:
            return 'lead'
        else:
            return 'manager'

    def _apply_multipliers(self, base_salary: Dict[str, float], resume_data: Dict[str, Any], 
                          job_data: Dict[str, Any]) -> Dict[str, float]:
        """Apply various multipliers to base salary"""
        multiplier = 1.0
        factors = []
        
        # Location multiplier
        location_mult = self._get_location_multiplier(job_data)
        multiplier *= location_mult
        factors.append(f"Location: {location_mult:.2f}x")
        
        # Skill multiplier
        skill_mult = self._get_skill_multiplier(resume_data, job_data)
        multiplier *= skill_mult
        factors.append(f"Skills: {skill_mult:.2f}x")
        
        # Industry multiplier
        industry_mult = self._get_industry_multiplier(job_data)
        multiplier *= industry_mult
        factors.append(f"Industry: {industry_mult:.2f}x")
        
        # Education multiplier
        education_mult = self._get_education_multiplier(resume_data)
        multiplier *= education_mult
        factors.append(f"Education: {education_mult:.2f}x")
        
        # Apply multiplier to salary range
        adjusted_salary = {
            'min': int(base_salary['min'] * multiplier),
            'max': int(base_salary['max'] * multiplier),
            'avg': int(base_salary['avg'] * multiplier),
            'multiplier': multiplier,
            'factors': factors,
            'level': base_salary['level']
        }
        
        return adjusted_salary

    def _get_location_multiplier(self, job_data: Dict[str, Any]) -> float:
        """Get location-based salary multiplier"""
        location = job_data.get('location', '').lower()
        
        # Check for remote work
        if 'remote' in location or 'work from home' in location:
            return self.location_multipliers.get('remote', 0.9)
        
        # Check for specific cities
        for city, multiplier in self.location_multipliers.items():
            if city in location:
                return multiplier
        
        # Default multiplier for unknown locations
        return 1.0

    def _get_skill_multiplier(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> float:
        """Get skill-based salary multiplier"""
        resume_skills = resume_data.get('skills', {})
        job_description = job_data.get('description', '').lower()
        
        # Collect all skills from resume
        all_skills = []
        for category, skills in resume_skills.items():
            all_skills.extend(skills)
        
        # Check for premium skills
        premium_skill_count = 0
        for skill in all_skills:
            if skill.lower() in self.skill_multipliers:
                premium_skill_count += 1
        
        # Calculate multiplier based on premium skills
        if premium_skill_count == 0:
            return 1.0
        elif premium_skill_count == 1:
            return 1.02
        elif premium_skill_count == 2:
            return 1.05
        elif premium_skill_count == 3:
            return 1.08
        else:
            return 1.1

    def _get_industry_multiplier(self, job_data: Dict[str, Any]) -> float:
        """Get industry-based salary multiplier"""
        title = job_data.get('title', '').lower()
        description = job_data.get('description', '').lower()
        company = job_data.get('company', '').lower()
        
        # Check for industry keywords
        for industry, multiplier in self.industry_multipliers.items():
            if (industry in title or industry in description or 
                industry in company):
                return multiplier
        
        return 1.0

    def _get_education_multiplier(self, resume_data: Dict[str, Any]) -> float:
        """Get education-based salary multiplier"""
        education = resume_data.get('education', [])
        
        highest_degree = 'bachelor'  # Default
        
        for edu in education:
            degree = edu.get('degree', '').lower()
            if 'phd' in degree or 'doctorate' in degree:
                highest_degree = 'phd'
                break
            elif 'master' in degree or 'ms' in degree or 'ma' in degree:
                highest_degree = 'master'
            elif 'bachelor' in degree or 'bs' in degree or 'ba' in degree:
                highest_degree = 'bachelor'
            elif 'associate' in degree:
                highest_degree = 'associate'
            elif 'diploma' in degree:
                highest_degree = 'diploma'
        
        return self.education_multipliers.get(highest_degree, 1.0)

    def _calculate_confidence(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> float:
        """Calculate confidence score for the prediction"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on data quality
        if resume_data.get('experience'):
            confidence += 0.2
        
        if resume_data.get('education'):
            confidence += 0.1
        
        if resume_data.get('skills'):
            confidence += 0.1
        
        if job_data.get('description'):
            confidence += 0.1
        
        # Decrease confidence for missing data
        if not resume_data.get('experience'):
            confidence -= 0.2
        
        if not job_data.get('location'):
            confidence -= 0.1
        
        return max(0.1, min(1.0, confidence))

    def _generate_market_comparison(self, predicted_salary: Dict[str, float], 
                                  market_data: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Generate market comparison data"""
        if not market_data:
            return {
                'available': False,
                'message': 'No market data available for comparison'
            }
        
        # Extract salary data from market data
        salaries = []
        for job in market_data:
            salary = job.get('salary')
            if salary and isinstance(salary, (int, float)):
                salaries.append(salary)
        
        if not salaries:
            return {
                'available': False,
                'message': 'No salary data found in market data'
            }
        
        # Calculate market statistics
        market_stats = {
            'min': min(salaries),
            'max': max(salaries),
            'avg': statistics.mean(salaries),
            'median': statistics.median(salaries),
            'count': len(salaries)
        }
        
        # Compare with prediction
        predicted_avg = predicted_salary['avg']
        market_avg = market_stats['avg']
        
        comparison = {
            'available': True,
            'market_stats': market_stats,
            'prediction_vs_market': {
                'difference': predicted_avg - market_avg,
                'percentage_diff': ((predicted_avg - market_avg) / market_avg) * 100 if market_avg > 0 else 0,
                'prediction_rank': self._calculate_percentile(predicted_avg, salaries)
            }
        }
        
        return comparison

    def _calculate_percentile(self, value: float, data: List[float]) -> float:
        """Calculate percentile rank of a value in a dataset"""
        if not data:
            return 50.0
        
        sorted_data = sorted(data)
        rank = 0
        for item in sorted_data:
            if item <= value:
                rank += 1
        
        return (rank / len(sorted_data)) * 100

    def _get_salary_factors(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed factors affecting salary prediction"""
        factors = {
            'experience_level': self._determine_experience_level(resume_data, job_data),
            'location_impact': self._get_location_impact(job_data),
            'skill_impact': self._get_skill_impact(resume_data),
            'education_impact': self._get_education_impact(resume_data),
            'industry_impact': self._get_industry_impact(job_data)
        }
        
        return factors

    def _get_location_impact(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get location impact on salary"""
        location = job_data.get('location', '').lower()
        multiplier = self._get_location_multiplier(job_data)
        
        return {
            'location': location,
            'multiplier': multiplier,
            'impact': 'High' if multiplier > 1.2 else 'Medium' if multiplier > 0.8 else 'Low'
        }

    def _get_skill_impact(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get skill impact on salary"""
        resume_skills = resume_data.get('skills', {})
        premium_skills = []
        
        for category, skills in resume_skills.items():
            for skill in skills:
                if skill.lower() in self.skill_multipliers:
                    premium_skills.append(skill)
        
        return {
            'premium_skills': premium_skills,
            'count': len(premium_skills),
            'impact': 'High' if len(premium_skills) > 3 else 'Medium' if len(premium_skills) > 1 else 'Low'
        }

    def _get_education_impact(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get education impact on salary"""
        education = resume_data.get('education', [])
        highest_degree = 'None'
        multiplier = 1.0
        
        for edu in education:
            degree = edu.get('degree', '').lower()
            if 'phd' in degree:
                highest_degree = 'PhD'
                multiplier = self.education_multipliers['phd']
                break
            elif 'master' in degree:
                highest_degree = 'Master'
                multiplier = self.education_multipliers['master']
            elif 'bachelor' in degree:
                highest_degree = 'Bachelor'
                multiplier = self.education_multipliers['bachelor']
        
        return {
            'highest_degree': highest_degree,
            'multiplier': multiplier,
            'impact': 'High' if multiplier > 1.1 else 'Medium' if multiplier > 0.9 else 'Low'
        }

    def _get_industry_impact(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get industry impact on salary"""
        title = job_data.get('title', '').lower()
        description = job_data.get('description', '').lower()
        multiplier = self._get_industry_multiplier(job_data)
        
        industry = 'General'
        for ind, mult in self.industry_multipliers.items():
            if ind in title or ind in description:
                industry = ind.title()
                break
        
        return {
            'industry': industry,
            'multiplier': multiplier,
            'impact': 'High' if multiplier > 1.1 else 'Medium' if multiplier > 0.9 else 'Low'
        }

    def get_salary_insights(self, resume_data: Dict[str, Any], jobs_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get salary insights and trends for a resume across multiple jobs
        
        Args:
            resume_data: Parsed resume data
            jobs_data: List of job postings
            
        Returns:
            Dictionary containing salary insights
        """
        predictions = []
        
        for job in jobs_data:
            prediction = self.predict_salary(resume_data, job)
            if 'error' not in prediction:
                predictions.append({
                    'job_id': job.get('id'),
                    'job_title': job.get('title'),
                    'company': job.get('company'),
                    'location': job.get('location'),
                    'predicted_salary': prediction['predicted_salary'],
                    'confidence': prediction['confidence_score']
                })
        
        if not predictions:
            return {
                'error': 'No valid predictions generated',
                'insights_generated_at': datetime.now().isoformat()
            }
        
        # Calculate insights
        salaries = [p['predicted_salary']['avg'] for p in predictions]
        
        insights = {
            'total_jobs_analyzed': len(predictions),
            'salary_range': {
                'min': min(salaries),
                'max': max(salaries),
                'avg': statistics.mean(salaries),
                'median': statistics.median(salaries)
            },
            'top_paying_jobs': sorted(predictions, key=lambda x: x['predicted_salary']['avg'], reverse=True)[:5],
            'location_analysis': self._analyze_location_salaries(predictions),
            'company_analysis': self._analyze_company_salaries(predictions),
            'insights_generated_at': datetime.now().isoformat()
        }
        
        return insights

    def _analyze_location_salaries(self, predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze salary differences by location"""
        location_salaries = {}
        
        for pred in predictions:
            location = pred['location']
            salary = pred['predicted_salary']['avg']
            
            if location not in location_salaries:
                location_salaries[location] = []
            location_salaries[location].append(salary)
        
        location_analysis = {}
        for location, salaries in location_salaries.items():
            location_analysis[location] = {
                'avg_salary': statistics.mean(salaries),
                'job_count': len(salaries),
                'salary_range': {
                    'min': min(salaries),
                    'max': max(salaries)
                }
            }
        
        return location_analysis

    def _analyze_company_salaries(self, predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze salary differences by company"""
        company_salaries = {}
        
        for pred in predictions:
            company = pred['company']
            salary = pred['predicted_salary']['avg']
            
            if company not in company_salaries:
                company_salaries[company] = []
            company_salaries[company].append(salary)
        
        company_analysis = {}
        for company, salaries in company_salaries.items():
            company_analysis[company] = {
                'avg_salary': statistics.mean(salaries),
                'job_count': len(salaries),
                'salary_range': {
                    'min': min(salaries),
                    'max': max(salaries)
                }
            }
        
        return company_analysis