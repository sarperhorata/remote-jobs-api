import os
import logging
import openai
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class FakeJobRiskLevel(str, Enum):
    """Risk levels for fake job detection"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class FakeJobAnalysis:
    """Result of fake job analysis"""
    job_id: str
    risk_level: FakeJobRiskLevel
    confidence_score: float  # 0-1
    red_flags: List[str]
    suspicious_patterns: List[str]
    ai_analysis: Optional[str]
    recommendation: str
    analyzed_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "risk_level": self.risk_level.value,
            "confidence_score": self.confidence_score,
            "red_flags": self.red_flags,
            "suspicious_patterns": self.suspicious_patterns,
            "ai_analysis": self.ai_analysis,
            "recommendation": self.recommendation,
            "analyzed_at": self.analyzed_at.isoformat()
        }

class FakeJobDetector:
    """AI-powered fake job post detection service"""
    
    def __init__(self):
        self.client = None
        self._initialize_openai()
        
        # Rule-based patterns for quick detection
        self.red_flag_patterns = {
            "unrealistic_salary": [
                r"\$\d{4,6}\+?\s*per\s*week",
                r"\$\d{3,5}\s*per\s*day",
                r"earn\s*\$\d{4,6}\+?\s*weekly",
                r"\$\d{4,6}\+?\s*weekly"
            ],
            "vague_job_description": [
                r"work\s*from\s*home",
                r"easy\s*money",
                r"no\s*experience\s*(required|needed)",
                r"flexible\s*hours",
                r"part\s*time\s*full\s*time"
            ],
            "suspicious_contact": [
                r"contact\s*via\s*whatsapp",
                r"text\s*us\s*at",
                r"call\s*\+\d+",
                r"telegram\s*@\w+"
            ],
            "urgency_pressure": [
                r"urgent\s*hiring",
                r"immediate\s*start",
                r"apply\s*now",
                r"limited\s*positions",
                r"act\s*fast"
            ],
            "personal_info_request": [
                r"send\s*photo",
                r"provide\s*id",
                r"bank\s*details",
                r"social\s*security",
                r"credit\s*card"
            ]
        }
    
    def _initialize_openai(self):
        """Initialize OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.info("OpenAI API key not configured - AI fake job detection disabled (rule-based detection still active)")
            return
        
        try:
            self.client = openai.OpenAI(api_key=api_key)
            logger.info("✅ OpenAI fake job detection enabled")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
    
    async def analyze_job(self, job_data: Dict[str, Any]) -> FakeJobAnalysis:
        """Analyze a job post for fake indicators"""
        try:
            job_id = str(job_data.get("_id", "unknown"))
            
            # Step 1: Rule-based analysis
            rule_results = self._analyze_with_rules(job_data)
            
            # Step 2: AI-powered analysis (if available)
            ai_results = await self._analyze_with_ai(job_data)
            
            # Step 3: Combine results
            final_analysis = self._combine_analysis(
                job_id, job_data, rule_results, ai_results
            )
            
            # Step 4: Log analysis for learning
            await self._log_analysis(final_analysis)
            
            return final_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing job {job_data.get('_id')}: {str(e)}")
            return self._create_error_analysis(job_data.get("_id", "unknown"), str(e))
    
    def _analyze_with_rules(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze job using rule-based patterns"""
        red_flags = []
        suspicious_patterns = []
        risk_score = 0.0
        
        # Combine all text fields for analysis
        text_content = self._extract_text_content(job_data)
        text_lower = text_content.lower()
        
        # Check each pattern category
        for category, patterns in self.red_flag_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    red_flags.append(f"{category}: {pattern}")
                    risk_score += self._get_risk_weight(category)
        
        # Additional heuristic checks
        risk_score += self._check_company_legitimacy(job_data)
        risk_score += self._check_job_requirements(job_data)
        risk_score += self._check_application_process(job_data)
        risk_score += self._check_salary_claims(job_data)
        
        return {
            "red_flags": red_flags,
            "suspicious_patterns": suspicious_patterns,
            "risk_score": min(risk_score, 1.0)  # Cap at 1.0
        }
    
    async def _analyze_with_ai(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze job using OpenAI GPT"""
        if not self.client:
            return {"ai_analysis": None, "ai_risk_score": 0.0}
        
        try:
            # Prepare job content for AI analysis
            job_content = self._prepare_ai_prompt(job_data)
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Cost-effective model
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert at detecting fake, fraudulent, or suspicious job postings. 
                        Analyze the job posting and provide:
                        1. Risk assessment (LOW/MEDIUM/HIGH/CRITICAL)
                        2. Confidence score (0-1)
                        3. List of specific red flags found
                        4. Brief explanation of concerns
                        5. Recommendation (APPROVE/REVIEW/REJECT)
                        
                        Respond in JSON format with keys: risk_level, confidence, red_flags, analysis, recommendation"""
                    },
                    {
                        "role": "user", 
                        "content": f"Analyze this job posting for authenticity:\n\n{job_content}"
                    }
                ],
                max_tokens=500,
                temperature=0.1  # Low temperature for consistent analysis
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content
            try:
                ai_data = json.loads(ai_response)
                return {
                    "ai_analysis": ai_data.get("analysis", ""),
                    "ai_risk_level": ai_data.get("risk_level", "LOW"),
                    "ai_confidence": ai_data.get("confidence", 0.5),
                    "ai_red_flags": ai_data.get("red_flags", []),
                    "ai_recommendation": ai_data.get("recommendation", "REVIEW")
                }
            except json.JSONDecodeError:
                # Fallback if AI doesn't return valid JSON
                return {
                    "ai_analysis": ai_response,
                    "ai_risk_level": "MEDIUM",
                    "ai_confidence": 0.5,
                    "ai_red_flags": [],
                    "ai_recommendation": "REVIEW"
                }
            
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {str(e)}")
            return {"ai_analysis": f"AI analysis failed: {str(e)}", "ai_risk_score": 0.0}
    
    def _extract_text_content(self, job_data: Dict[str, Any]) -> str:
        """Extract all text content from job data"""
        text_fields = [
            job_data.get("title", ""),
            job_data.get("company", ""),
            job_data.get("description", ""),
            job_data.get("requirements", ""),
            job_data.get("benefits", ""),
            job_data.get("location", ""),
            " ".join(job_data.get("skills", []))
        ]
        
        return " ".join(filter(None, text_fields))
    
    def _prepare_ai_prompt(self, job_data: Dict[str, Any]) -> str:
        """Prepare job data for AI analysis"""
        content = f"""
Job Title: {job_data.get('title', 'N/A')}
Company: {job_data.get('company', 'N/A')}
Location: {job_data.get('location', 'N/A')}
Job Type: {job_data.get('jobType', 'N/A')}
Experience Level: {job_data.get('experienceLevel', 'N/A')}
Salary: {job_data.get('salary', 'N/A')}
Is Remote: {job_data.get('isRemote', 'N/A')}
Skills Required: {', '.join(job_data.get('skills', []))}

Description:
{job_data.get('description', 'N/A')}

Requirements:
{job_data.get('requirements', 'N/A')}

Benefits:
{job_data.get('benefits', 'N/A')}

Application URL: {job_data.get('url', 'N/A')}
Company URL: {job_data.get('companyUrl', 'N/A')}
"""
        return content.strip()
    
    def _get_risk_weight(self, category: str) -> float:
        """Get risk weight for different categories"""
        weights = {
            "unrealistic_salary": 0.3,
            "vague_job_description": 0.2,
            "suspicious_contact": 0.25,
            "urgency_pressure": 0.15,
            "personal_info_request": 0.4
        }
        return weights.get(category, 0.1)
    
    def _check_company_legitimacy(self, job_data: Dict[str, Any]) -> float:
        """Check company legitimacy indicators"""
        risk = 0.0
        company = job_data.get("company", "").lower()
        
        # Generic company names
        generic_names = ["company", "corporation", "ltd", "llc", "inc", "hiring", "recruiter"]
        if any(generic in company for generic in generic_names):
            risk += 0.1
        
        # Missing company URL
        if not job_data.get("companyUrl"):
            risk += 0.1
        
        # Suspicious domain patterns
        company_url = job_data.get("companyUrl", "")
        if company_url:
            suspicious_domains = [".tk", ".ml", ".ga", ".cf", "blogspot", "wordpress"]
            if any(domain in company_url for domain in suspicious_domains):
                risk += 0.2
        
        return risk
    
    def _check_job_requirements(self, job_data: Dict[str, Any]) -> float:
        """Check job requirements for red flags"""
        risk = 0.0
        requirements = job_data.get("requirements", "").lower()
        
        # No experience but high pay
        if ("no experience" in requirements and 
            self._has_high_salary_claim(job_data)):
            risk += 0.2
        
        # Vague requirements
        vague_indicators = ["flexible", "easy", "simple", "anyone can do"]
        if any(indicator in requirements for indicator in vague_indicators):
            risk += 0.1
        
        return risk
    
    def _check_application_process(self, job_data: Dict[str, Any]) -> float:
        """Check application process for red flags"""
        risk = 0.0
        
        # Missing proper application URL
        url = job_data.get("url", "")
        if not url or not url.startswith(("http://", "https://")):
            risk += 0.1
        
        # Suspicious URL patterns
        if url:
            suspicious_patterns = ["bit.ly", "tinyurl", "shortlink", "apply-now"]
            if any(pattern in url for pattern in suspicious_patterns):
                risk += 0.15
        
        return risk
    
    def _check_salary_claims(self, job_data: Dict[str, Any]) -> float:
        """Check for unrealistic salary claims"""
        risk = 0.0
        salary_text = str(job_data.get("salary", "")).lower()
        description = job_data.get("description", "").lower()
        
        # Unrealistic hourly rates
        hourly_matches = re.findall(r'\$(\d+)\s*per\s*hour', salary_text + " " + description)
        for match in hourly_matches:
            hourly_rate = int(match)
            if hourly_rate > 100:  # $100+/hour is suspicious for most remote jobs
                risk += 0.2
        
        # Weekly salary claims
        if re.search(r'\$\d{4,6}\+?\s*weekly', salary_text + " " + description):
            risk += 0.25
        
        return risk
    
    def _has_high_salary_claim(self, job_data: Dict[str, Any]) -> bool:
        """Check if job has suspiciously high salary claims"""
        salary_text = str(job_data.get("salary", "")).lower()
        description = job_data.get("description", "").lower()
        
        high_salary_patterns = [
            r'\$\d{4,6}\+?\s*weekly',
            r'\$\d{3,5}\s*per\s*day',
            r'\$[1-9]\d{2,}\s*per\s*hour'
        ]
        
        for pattern in high_salary_patterns:
            if re.search(pattern, salary_text + " " + description):
                return True
        
        return False
    
    def _combine_analysis(self, job_id: str, job_data: Dict[str, Any], 
                         rule_results: Dict[str, Any], 
                         ai_results: Dict[str, Any]) -> FakeJobAnalysis:
        """Combine rule-based and AI analysis results"""
        
        # Calculate final risk score
        rule_score = rule_results.get("risk_score", 0.0)
        ai_confidence = ai_results.get("ai_confidence", 0.0)
        
        # Weight the scores (60% rules, 40% AI)
        final_score = (rule_score * 0.6) + (ai_confidence * 0.4)
        
        # Determine risk level
        if final_score >= 0.8:
            risk_level = FakeJobRiskLevel.CRITICAL
        elif final_score >= 0.6:
            risk_level = FakeJobRiskLevel.HIGH
        elif final_score >= 0.4:
            risk_level = FakeJobRiskLevel.MEDIUM
        else:
            risk_level = FakeJobRiskLevel.LOW
        
        # Combine red flags
        all_red_flags = rule_results.get("red_flags", [])
        ai_red_flags = ai_results.get("ai_red_flags", [])
        if ai_red_flags:
            all_red_flags.extend([f"AI detected: {flag}" for flag in ai_red_flags])
        
        # Generate recommendation
        recommendation = self._generate_recommendation(risk_level, final_score, ai_results)
        
        return FakeJobAnalysis(
            job_id=job_id,
            risk_level=risk_level,
            confidence_score=final_score,
            red_flags=all_red_flags,
            suspicious_patterns=rule_results.get("suspicious_patterns", []),
            ai_analysis=ai_results.get("ai_analysis"),
            recommendation=recommendation,
            analyzed_at=datetime.utcnow()
        )
    
    def _generate_recommendation(self, risk_level: FakeJobRiskLevel, 
                               score: float, ai_results: Dict[str, Any]) -> str:
        """Generate action recommendation based on analysis"""
        ai_recommendation = ai_results.get("ai_recommendation", "").upper()
        
        if risk_level == FakeJobRiskLevel.CRITICAL:
            return "REJECT - High probability of fraud. Do not display to users."
        elif risk_level == FakeJobRiskLevel.HIGH:
            return "MANUAL_REVIEW - Requires human verification before approval."
        elif risk_level == FakeJobRiskLevel.MEDIUM:
            return "FLAG - Display with warning or require additional verification."
        else:
            return "APPROVE - Appears legitimate but monitor for user reports."
    
    def _create_error_analysis(self, job_id: str, error_msg: str) -> FakeJobAnalysis:
        """Create analysis result for error cases"""
        return FakeJobAnalysis(
            job_id=job_id,
            risk_level=FakeJobRiskLevel.MEDIUM,
            confidence_score=0.5,
            red_flags=[f"Analysis error: {error_msg}"],
            suspicious_patterns=[],
            ai_analysis=None,
            recommendation="MANUAL_REVIEW - Analysis failed, requires human review.",
            analyzed_at=datetime.utcnow()
        )
    
    async def _log_analysis(self, analysis: FakeJobAnalysis):
        """Log analysis results for learning and improvement"""
        try:
            from backend.database import get_async_db
            db = await get_async_db()
            
            await db.fake_job_analyses.insert_one(analysis.to_dict())
            
        except Exception as e:
            logger.error(f"Failed to log fake job analysis: {str(e)}")
    
    async def batch_analyze_jobs(self, jobs: List[Dict[str, Any]]) -> List[FakeJobAnalysis]:
        """Analyze multiple jobs in batch"""
        results = []
        
        for job in jobs:
            analysis = await self.analyze_job(job)
            results.append(analysis)
        
        return results
    
    async def get_analysis_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get fake job detection statistics"""
        try:
            from backend.database import get_async_db
            from datetime import timedelta
            
            db = await get_async_db()
            
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Aggregate statistics
            pipeline = [
                {
                    "$match": {
                        "analyzed_at": {
                            "$gte": start_date.isoformat(),
                            "$lte": end_date.isoformat()
                        }
                    }
                },
                {
                    "$group": {
                        "_id": "$risk_level",
                        "count": {"$sum": 1},
                        "avg_confidence": {"$avg": "$confidence_score"}
                    }
                }
            ]
            
            results = await db.fake_job_analyses.aggregate(pipeline).to_list(length=None)
            
            # Format results
            stats = {
                "total_analyzed": sum(result["count"] for result in results),
                "risk_distribution": {result["_id"]: result["count"] for result in results},
                "avg_confidence_by_risk": {
                    result["_id"]: result["avg_confidence"] for result in results
                },
                "period_days": days
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get analysis statistics: {str(e)}")
            return {}

# Global detector instance
fake_job_detector = FakeJobDetector() 