from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import Dict, Any
from pydantic import BaseModel, HttpUrl
import logging

from services.auto_apply_service import auto_apply_service
from utils.auth import get_current_user
from schemas.user import User

router = APIRouter()
logger = logging.getLogger(__name__)
security = HTTPBearer()

class AutoApplyRequest(BaseModel):
    job_url: HttpUrl
    job_id: str
    
class FormAnalysisRequest(BaseModel):
    job_url: HttpUrl

@router.post("/analyze-form")
async def analyze_job_form(
    request: FormAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """Analyze a job application form to check if auto-apply is possible"""
    try:
        analysis = await auto_apply_service.analyze_job_application_form(str(request.job_url))
        
        return {
            "success": True,
            "analysis": analysis,
            "auto_apply_supported": analysis.get("auto_apply_supported", False),
            "message": "Form analysis completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error analyzing job form: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze job application form"
        )

@router.post("/auto-apply")
async def auto_apply_to_job(
    request: AutoApplyRequest,
    current_user: User = Depends(get_current_user)
):
    """Automatically apply to a job using AI-generated responses"""
    try:
        # First, analyze the form
        form_analysis = await auto_apply_service.analyze_job_application_form(str(request.job_url))
        
        if not form_analysis.get("auto_apply_supported", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Auto-apply is not supported for this job posting. Please apply manually."
            )
        
        # Get user profile for generating responses
        user_profile = {
            "email": current_user.email,
            "full_name": getattr(current_user, 'full_name', ''),
            "phone": getattr(current_user, 'phone', ''),
            "linkedin_url": getattr(current_user, 'linkedin_url', ''),
            "portfolio_url": getattr(current_user, 'portfolio_url', ''),
            "location": getattr(current_user, 'location', ''),
            "experience_level": getattr(current_user, 'experience_level', 'mid'),
            "skills": getattr(current_user, 'skills', []),
        }
        
        # Generate field responses
        form_fields = form_analysis.get("form_data", {}).get("fields", [])
        field_responses = await auto_apply_service.generate_field_responses(user_profile, form_fields)
        
        # Submit the application
        submission_result = await auto_apply_service.submit_application(
            job_url=str(request.job_url),
            form_data=form_analysis.get("form_data", {}),
            field_responses=field_responses,
            user_id=str(current_user.id)
        )
        
        return {
            "success": submission_result.get("success", False),
            "message": submission_result.get("message", "Auto-apply completed"),
            "application_id": submission_result.get("application_id"),
            "form_analysis": form_analysis,
            "field_responses_generated": len(field_responses),
            "submitted_at": submission_result.get("submitted_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during auto-apply: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Auto-apply failed: {str(e)}"
        )

@router.post("/preview-responses")
async def preview_auto_apply_responses(
    request: FormAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """Preview what responses would be generated for a job application form"""
    try:
        # Analyze the form
        form_analysis = await auto_apply_service.analyze_job_application_form(str(request.job_url))
        
        if not form_analysis.get("form_found", False):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No application form found on this job posting"
            )
        
        # Get user profile
        user_profile = {
            "email": current_user.email,
            "full_name": getattr(current_user, 'full_name', ''),
            "phone": getattr(current_user, 'phone', ''),
            "linkedin_url": getattr(current_user, 'linkedin_url', ''),
            "portfolio_url": getattr(current_user, 'portfolio_url', ''),
            "location": getattr(current_user, 'location', ''),
            "experience_level": getattr(current_user, 'experience_level', 'mid'),
            "skills": getattr(current_user, 'skills', []),
        }
        
        # Generate preview responses
        form_fields = form_analysis.get("form_data", {}).get("fields", [])
        field_responses = await auto_apply_service.generate_field_responses(user_profile, form_fields)
        
        # Format response with field details and generated values
        field_previews = []
        for field in form_fields:
            field_name = field.get("name")
            preview = {
                "field_name": field_name,
                "field_label": field.get("label", ""),
                "field_type": field.get("type", ""),
                "category": field.get("category", "other"),
                "required": field.get("required", False),
                "generated_value": field_responses.get(field_name, ""),
                "placeholder": field.get("placeholder", "")
            }
            field_previews.append(preview)
        
        return {
            "success": True,
            "auto_apply_supported": form_analysis.get("auto_apply_supported", False),
            "form_found": True,
            "total_fields": len(form_fields),
            "fields_with_responses": len(field_responses),
            "field_previews": field_previews,
            "user_profile_completeness": calculate_profile_completeness(user_profile)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error previewing auto-apply responses: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate response preview"
        )

def calculate_profile_completeness(user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate how complete the user's profile is for auto-apply"""
    required_fields = ['email', 'full_name']
    optional_fields = ['phone', 'linkedin_url', 'portfolio_url', 'location', 'skills']
    
    required_complete = sum(1 for field in required_fields if user_profile.get(field))
    optional_complete = sum(1 for field in optional_fields if user_profile.get(field))
    
    return {
        "required_complete": required_complete,
        "required_total": len(required_fields),
        "optional_complete": optional_complete,
        "optional_total": len(optional_fields),
        "overall_percentage": int(((required_complete + optional_complete) / (len(required_fields) + len(optional_fields))) * 100),
        "ready_for_auto_apply": required_complete == len(required_fields)
    } 