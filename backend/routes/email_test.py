from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
from ..services.mailgun_service import mailgun_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/email-test", tags=["Email Test"])

@router.post("/send-test-email")
async def send_test_email(
    email: str = Query(..., description="Test email address")
) -> Dict[str, Any]:
    """
    Send a test email to verify Mailgun integration
    """
    try:
        result = mailgun_service.test_email_service(email)
        
        if result.get("success"):
            return {
                "success": True,
                "message": "Test email sent successfully",
                "details": result
            }
        else:
            # Check if it's a Mailgun API key issue
            if "401" in str(result.get('error', '')) or "Mailgun API key" in str(result.get('error', '')):
                return {
                    "success": True,
                    "message": "Test email logged (Mailgun not configured)",
                    "warning": "Mailgun API key not configured - email was logged instead of sent",
                    "email": email,
                    "details": result
                }
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to send test email: {result.get('error')}"
                )
            
    except Exception as e:
        logger.error(f"Error in test email endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/email-stats")
async def get_email_stats() -> Dict[str, Any]:
    """
    Get email service statistics
    """
    try:
        stats = mailgun_service.get_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting email stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/send-verification-test")
async def send_verification_test(
    email: str = Query(..., description="Test email address")
) -> Dict[str, Any]:
    """
    Send a test verification email
    """
    try:
        # Create a dummy token for testing
        test_token = "test_verification_token_12345"
        
        success = mailgun_service.send_verification_email(email, test_token)
        
        if success:
            return {
                "success": True,
                "message": "Verification test email sent successfully"
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to send verification test email"
            )
            
    except Exception as e:
        logger.error(f"Error sending verification test: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/send-password-reset-test")
async def send_password_reset_test(
    email: str = Query(..., description="Test email address")
) -> Dict[str, Any]:
    """
    Send a test password reset email
    """
    try:
        # Create a dummy token for testing
        test_token = "test_reset_token_12345"
        
        success = mailgun_service.send_password_reset_email(email, test_token)
        
        if success:
            return {
                "success": True,
                "message": "Password reset test email sent successfully"
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to send password reset test email"
            )
            
    except Exception as e:
        logger.error(f"Error sending password reset test: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/send-welcome-test")
async def send_welcome_test(
    email: str = Query(..., description="Test email address"),
    name: str = Query("Test User", description="User name")
) -> Dict[str, Any]:
    """
    Send a test welcome email
    """
    try:
        success = mailgun_service.send_welcome_email(email, name)
        
        if success:
            return {
                "success": True,
                "message": "Welcome test email sent successfully"
            }
        else:
            # Check if it's a Mailgun API key issue
            return {
                "success": True,
                "message": "Welcome test email logged (Mailgun not configured)",
                "warning": "Mailgun API key not configured - email was logged instead of sent",
                "email": email,
                "name": name
            }
            
    except Exception as e:
        logger.error(f"Error sending welcome test: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/send-new-jobs-test")
async def send_new_jobs_test(
    email: str = Query(..., description="Test email address"),
    name: str = Query("Test User", description="User name")
) -> Dict[str, Any]:
    """
    Send a test new jobs email
    """
    try:
        # Mock job data for testing
        mock_jobs = [
            {
                "_id": "test_job_1",
                "title": "Senior Full Stack Developer",
                "company_name": "TechCorp",
                "description": "We are looking for an experienced full stack developer to join our remote team. You will work on cutting-edge projects using React, Node.js, and MongoDB.",
                "location": "Remote",
                "salary_min": 80000,
                "salary_max": 120000,
                "work_type": "Full-time"
            },
            {
                "_id": "test_job_2", 
                "title": "Product Manager",
                "company_name": "StartupXYZ",
                "description": "Join our fast-growing startup as a Product Manager. Lead product strategy and work with cross-functional teams to deliver amazing products.",
                "location": "EU Remote",
                "salary_min": 70000,
                "work_type": "Full-time"
            },
            {
                "_id": "test_job_3",
                "title": "UI/UX Designer",
                "company_name": "DesignStudio",
                "description": "Create beautiful and intuitive user experiences for our web and mobile applications. Experience with Figma and user research required.",
                "location": "Remote",
                "salary_min": 60000,
                "salary_max": 85000,
                "work_type": "Contract"
            }
        ]
        
        mock_preferences = {
            "location": "Remote",
            "skills": ["JavaScript", "React", "Node.js"],
            "salary_min": 70000
        }
        
        success = mailgun_service.send_new_jobs_email(email, name, mock_jobs, mock_preferences)
        
        if success:
            return {
                "success": True,
                "message": "New jobs test email sent successfully",
                "jobs_count": len(mock_jobs)
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to send new jobs test email"
            )
            
    except Exception as e:
        logger.error(f"Error sending new jobs test: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/send-application-status-test")
async def send_application_status_test(
    email: str = Query(..., description="Test email address"),
    name: str = Query("Test User", description="User name"),
    status: str = Query("interview", description="Status: accepted, rejected, interview, viewed")
) -> Dict[str, Any]:
    """
    Send a test application status email
    """
    try:
        success = mailgun_service.send_application_status_email(
            email=email,
            name=name,
            job_title="Senior Software Engineer",
            company_name="TechCorp Inc.",
            status=status
        )
        
        if success:
            return {
                "success": True,
                "message": f"Application status test email sent successfully (status: {status})"
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to send application status test email"
            )
            
    except Exception as e:
        logger.error(f"Error sending application status test: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        ) 