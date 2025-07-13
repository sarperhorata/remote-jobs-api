from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import base64
import logging
from datetime import datetime

from services.resume_parser_service import ResumeParserService
from services.job_matching_service import JobMatchingService
from services.salary_prediction_service import SalaryPredictionService
from core.auth import get_current_user
from models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Services"])

# Initialize services
resume_parser = ResumeParserService()
job_matcher = JobMatchingService()
salary_predictor = SalaryPredictionService()

@router.post("/parse-resume")
async def parse_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Parse resume file and extract structured information
    Supports PDF, DOCX, and TXT formats
    """
    try:
        # Validate file type
        allowed_types = ['pdf', 'docx', 'txt']
        file_extension = file.filename.split('.')[-1].lower()
        
        if file_extension not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Parse resume
        parsed_data = resume_parser.parse_resume(file_content, file_extension)
        
        if 'error' in parsed_data:
            raise HTTPException(status_code=400, detail=parsed_data['error'])
        
        # Get summary
        summary = resume_parser.get_parsed_resume_summary(parsed_data)
        
        return {
            "success": True,
            "data": parsed_data,
            "summary": summary,
            "message": "Resume parsed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error parsing resume: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/parse-resume-base64")
async def parse_resume_base64(
    base64_content: str = Form(...),
    file_type: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """
    Parse resume from base64 encoded content
    """
    try:
        # Validate file type
        allowed_types = ['pdf', 'docx', 'txt']
        if file_type.lower() not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Parse resume
        parsed_data = resume_parser.parse_resume_from_base64(base64_content, file_type)
        
        if 'error' in parsed_data:
            raise HTTPException(status_code=400, detail=parsed_data['error'])
        
        # Get summary
        summary = resume_parser.get_parsed_resume_summary(parsed_data)
        
        return {
            "success": True,
            "data": parsed_data,
            "summary": summary,
            "message": "Resume parsed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error parsing resume from base64: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/calculate-matching")
async def calculate_job_matching(
    resume_data: Dict[str, Any],
    job_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """
    Calculate matching score between resume and job
    """
    try:
        # Validate input data
        if not resume_data:
            raise HTTPException(status_code=400, detail="Resume data is required")
        
        if not job_data:
            raise HTTPException(status_code=400, detail="Job data is required")
        
        # Calculate matching score
        matching_result = job_matcher.calculate_matching_score(resume_data, job_data)
        
        if 'error' in matching_result:
            raise HTTPException(status_code=400, detail=matching_result['error'])
        
        return {
            "success": True,
            "data": matching_result,
            "message": "Matching score calculated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating matching score: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/get-top-matches")
async def get_top_job_matches(
    resume_data: Dict[str, Any],
    jobs_data: List[Dict[str, Any]],
    limit: int = 10,
    min_score: float = 0.3,
    current_user: User = Depends(get_current_user)
):
    """
    Get top matching jobs for a resume
    """
    try:
        # Validate input data
        if not resume_data:
            raise HTTPException(status_code=400, detail="Resume data is required")
        
        if not jobs_data:
            raise HTTPException(status_code=400, detail="Jobs data is required")
        
        # Get top matches
        top_matches = job_matcher.get_top_matches(resume_data, jobs_data, limit, min_score)
        
        return {
            "success": True,
            "data": {
                "matches": top_matches,
                "total_jobs_analyzed": len(jobs_data),
                "matches_found": len(top_matches)
            },
            "message": f"Found {len(top_matches)} matching jobs"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting top matches: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/get-recommendations")
async def get_job_recommendations(
    resume_data: Dict[str, Any],
    jobs_data: List[Dict[str, Any]],
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """
    Get personalized job recommendations with insights
    """
    try:
        # Validate input data
        if not resume_data:
            raise HTTPException(status_code=400, detail="Resume data is required")
        
        if not jobs_data:
            raise HTTPException(status_code=400, detail="Jobs data is required")
        
        # Get recommendations
        recommendations = job_matcher.get_resume_recommendations(resume_data, jobs_data, limit)
        
        return {
            "success": True,
            "data": recommendations,
            "message": "Job recommendations generated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/predict-salary")
async def predict_salary(
    resume_data: Dict[str, Any],
    job_data: Dict[str, Any],
    market_data: Optional[List[Dict[str, Any]]] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Predict salary range for a resume-job combination
    """
    try:
        # Validate input data
        if not resume_data:
            raise HTTPException(status_code=400, detail="Resume data is required")
        
        if not job_data:
            raise HTTPException(status_code=400, detail="Job data is required")
        
        # Predict salary
        prediction = salary_predictor.predict_salary(resume_data, job_data, market_data)
        
        if 'error' in prediction:
            raise HTTPException(status_code=400, detail=prediction['error'])
        
        return {
            "success": True,
            "data": prediction,
            "message": "Salary prediction generated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error predicting salary: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/get-salary-insights")
async def get_salary_insights(
    resume_data: Dict[str, Any],
    jobs_data: List[Dict[str, Any]],
    current_user: User = Depends(get_current_user)
):
    """
    Get salary insights across multiple jobs
    """
    try:
        # Validate input data
        if not resume_data:
            raise HTTPException(status_code=400, detail="Resume data is required")
        
        if not jobs_data:
            raise HTTPException(status_code=400, detail="Jobs data is required")
        
        # Get salary insights
        insights = salary_predictor.get_salary_insights(resume_data, jobs_data)
        
        if 'error' in insights:
            raise HTTPException(status_code=400, detail=insights['error'])
        
        return {
            "success": True,
            "data": insights,
            "message": "Salary insights generated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting salary insights: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/comprehensive-analysis")
async def comprehensive_analysis(
    resume_data: Dict[str, Any],
    jobs_data: List[Dict[str, Any]],
    market_data: Optional[List[Dict[str, Any]]] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Perform comprehensive analysis including parsing, matching, and salary prediction
    """
    try:
        # Validate input data
        if not resume_data:
            raise HTTPException(status_code=400, detail="Resume data is required")
        
        if not jobs_data:
            raise HTTPException(status_code=400, detail="Jobs data is required")
        
        # Get job recommendations
        recommendations = job_matcher.get_resume_recommendations(resume_data, jobs_data, limit=10)
        
        # Get salary insights
        salary_insights = salary_predictor.get_salary_insights(resume_data, jobs_data)
        
        # Calculate matching scores for top recommendations
        top_matches = recommendations.get('top_recommendations', [])
        detailed_matches = []
        
        for match in top_matches[:5]:  # Top 5 matches
            job = next((j for j in jobs_data if j.get('id') == match.get('job_id')), None)
            if job:
                matching_score = job_matcher.calculate_matching_score(resume_data, job)
                salary_prediction = salary_predictor.predict_salary(resume_data, job, market_data)
                
                detailed_matches.append({
                    'job_info': match,
                    'matching_details': matching_score,
                    'salary_prediction': salary_prediction
                })
        
        comprehensive_result = {
            'resume_summary': resume_parser.get_parsed_resume_summary(resume_data),
            'job_recommendations': recommendations,
            'salary_insights': salary_insights,
            'detailed_analysis': detailed_matches,
            'analysis_generated_at': datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "data": comprehensive_result,
            "message": "Comprehensive analysis completed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error performing comprehensive analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health")
async def ai_services_health():
    """
    Health check for AI services
    """
    try:
        return {
            "success": True,
            "status": "healthy",
            "services": {
                "resume_parser": "available",
                "job_matching": "available",
                "salary_prediction": "available"
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Service unhealthy")