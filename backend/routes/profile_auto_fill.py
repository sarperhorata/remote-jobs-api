import os
import logging
import json
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi.responses import JSONResponse
from datetime import datetime
import openai
from bson import ObjectId

from ..database.db import get_async_db
from ..core.security import get_current_user
from ..models.user import UserResponse as User
from ..utils.premium import is_premium_user
from ..services.cv_parser_service import cv_parser_service
from ..utils.linkedin import LinkedInIntegration

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/profile", tags=["profile-auto-fill"])

# OpenAI configuration
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize LinkedIn integration
linkedin = LinkedInIntegration()

class ProfileAutoFillService:
    """Service for automatically filling user profiles from CV or LinkedIn"""
    
    def __init__(self):
        self.cv_parser = cv_parser_service
        self.linkedin = linkedin

    async def extract_profile_from_cv(self, file_content: bytes, filename: str, user: Dict[str, Any]) -> Dict[str, Any]:
        """Extract profile information from uploaded CV"""
        try:
            # Parse CV using existing service
            parsed_data = self.cv_parser.parse_cv(file_content, filename)
            
            # Enhance with AI if available
            enhanced_data = await self._enhance_with_ai(parsed_data, user)
            
            # Format for profile update
            profile_data = self._format_for_profile(enhanced_data)
            
            return {
                "success": True,
                "message": "Profile data extracted successfully",
                "data": profile_data,
                "extraction_method": "cv_ai_enhanced",
                "extracted_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error extracting profile from CV: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to extract profile from CV"
            )

    async def import_profile_from_linkedin(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """Import profile information from LinkedIn"""
        try:
            # Check if user has LinkedIn connected
            if not user.get("linkedin_connected"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="LinkedIn account not connected"
                )
            
            # Get LinkedIn access token
            linkedin_token = user.get("linkedin_access_token")
            if not linkedin_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="LinkedIn access token not available"
                )
            
            # Fetch comprehensive profile data
            linkedin_data = await self.linkedin.get_user_cv_data(linkedin_token)
            if not linkedin_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to fetch LinkedIn profile data"
                )
            
            # Format for profile update
            profile_data = self._format_linkedin_for_profile(linkedin_data)
            
            return {
                "success": True,
                "message": "Profile data imported from LinkedIn successfully",
                "data": profile_data,
                "extraction_method": "linkedin_api",
                "extracted_at": datetime.now().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error importing profile from LinkedIn: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to import profile from LinkedIn"
            )

    async def _enhance_with_ai(self, parsed_data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance parsed data with AI analysis"""
        if not openai.api_key:
            return parsed_data
            
        try:
            # Create a comprehensive prompt for profile enhancement
            cv_content = self._create_cv_content(parsed_data)
            
            prompt = f"""
            Analyze this CV/resume and extract comprehensive profile information. Return a JSON object with the following structure:
            
            {{
                "name": "Full name",
                "email": "Email address",
                "phone": "Phone number",
                "location": "Location/City, Country",
                "title": "Current or target job title",
                "summary": "Professional summary (2-3 sentences)",
                "skills": ["skill1", "skill2", "skill3"],
                "experience": [
                    {{
                        "title": "Job title",
                        "company": "Company name",
                        "location": "Location",
                        "start_date": "YYYY-MM",
                        "end_date": "YYYY-MM or Present",
                        "current": true/false,
                        "description": "Key responsibilities and achievements"
                    }}
                ],
                "education": [
                    {{
                        "degree": "Degree name",
                        "institution": "School/University name",
                        "field": "Field of study",
                        "start_date": "YYYY-MM",
                        "end_date": "YYYY-MM or Present",
                        "current": true/false,
                        "gpa": "GPA if available"
                    }}
                ],
                "languages": ["Language1", "Language2"],
                "certifications": ["Certification1", "Certification2"],
                "links": {{
                    "linkedin": "LinkedIn URL",
                    "github": "GitHub URL",
                    "portfolio": "Portfolio URL"
                }}
            }}
            
            Guidelines:
            1. Extract information accurately from the text
            2. Normalize dates to YYYY-MM format
            3. Include only relevant and current information
            4. For skills, focus on technical and professional skills
            5. For experience, include key achievements and responsibilities
            6. For education, include degree, institution, and field of study
            7. Extract any social/professional links mentioned
            
            CV Content:
            {cv_content[:3000]}
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional CV parser specializing in profile data extraction. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=1500
            )
            
            ai_result = json.loads(response.choices[0].message.content)
            
            # Merge AI results with parsed data
            enhanced_data = {**parsed_data, **ai_result}
            
            return enhanced_data
            
        except Exception as e:
            logger.error(f"AI enhancement failed: {str(e)}")
            return parsed_data

    def _create_cv_content(self, parsed_data: Dict[str, Any]) -> str:
        """Create CV content string from parsed data"""
        content_parts = []
        
        if parsed_data.get('name'):
            content_parts.append(f"Name: {parsed_data['name']}")
        if parsed_data.get('email'):
            content_parts.append(f"Email: {parsed_data['email']}")
        if parsed_data.get('phone'):
            content_parts.append(f"Phone: {parsed_data['phone']}")
        if parsed_data.get('location'):
            content_parts.append(f"Location: {parsed_data['location']}")
        if parsed_data.get('summary'):
            content_parts.append(f"Summary: {parsed_data['summary']}")
        if parsed_data.get('skills'):
            content_parts.append(f"Skills: {', '.join(parsed_data['skills'])}")
        if parsed_data.get('experience'):
            content_parts.append("Experience:")
            for exp in parsed_data['experience']:
                content_parts.append(f"- {exp.get('title', '')} at {exp.get('company', '')}")
                content_parts.append(f"  {exp.get('description', '')}")
        if parsed_data.get('education'):
            content_parts.append("Education:")
            for edu in parsed_data['education']:
                content_parts.append(f"- {edu.get('degree', '')} from {edu.get('institution', '')}")
        
        return "\n".join(content_parts)

    def _format_for_profile(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format parsed data for profile update"""
        profile_data = {}
        
        # Basic information
        if parsed_data.get('name'):
            profile_data['name'] = parsed_data['name']
        if parsed_data.get('email'):
            profile_data['email'] = parsed_data['email']
        if parsed_data.get('phone'):
            profile_data['phone'] = parsed_data['phone']
        if parsed_data.get('location'):
            profile_data['location'] = parsed_data['location']
        if parsed_data.get('title'):
            profile_data['title'] = parsed_data['title']
        if parsed_data.get('summary'):
            profile_data['summary'] = parsed_data['summary']
        
        # Skills
        if parsed_data.get('skills'):
            profile_data['skills'] = parsed_data['skills']
        
        # Experience
        if parsed_data.get('experience'):
            profile_data['experience'] = parsed_data['experience']
        
        # Education
        if parsed_data.get('education'):
            profile_data['education'] = parsed_data['education']
        
        # Languages
        if parsed_data.get('languages'):
            profile_data['languages'] = parsed_data['languages']
        
        # Certifications
        if parsed_data.get('certifications'):
            profile_data['certifications'] = parsed_data['certifications']
        
        # Links
        if parsed_data.get('links'):
            links = parsed_data['links']
            if links.get('linkedin'):
                profile_data['linkedin_url'] = links['linkedin']
            if links.get('github'):
                profile_data['github_url'] = links['github']
            if links.get('portfolio'):
                profile_data['portfolio_url'] = links['portfolio']
        
        return profile_data

    def _format_linkedin_for_profile(self, linkedin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format LinkedIn data for profile update"""
        profile_data = {}
        
        # Basic information
        if linkedin_data.get('name'):
            profile_data['name'] = linkedin_data['name']
        if linkedin_data.get('email'):
            profile_data['email'] = linkedin_data['email']
        if linkedin_data.get('title'):
            profile_data['title'] = linkedin_data['title']
        if linkedin_data.get('summary'):
            profile_data['summary'] = linkedin_data['summary']
        if linkedin_data.get('location'):
            profile_data['location'] = linkedin_data['location']
        
        # Experience
        if linkedin_data.get('experience'):
            profile_data['experience'] = linkedin_data['experience']
        
        # Education
        if linkedin_data.get('education'):
            profile_data['education'] = linkedin_data['education']
        
        # Skills
        if linkedin_data.get('skills'):
            profile_data['skills'] = linkedin_data['skills']
        
        # LinkedIn URL
        if linkedin_data.get('linkedin_url'):
            profile_data['linkedin_url'] = linkedin_data['linkedin_url']
        
        return profile_data

# Initialize service
profile_service = ProfileAutoFillService()

@router.post("/auto-fill/cv")
async def auto_fill_from_cv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db = Depends(get_async_db)
):
    """
    Extract profile information from uploaded CV and auto-fill profile
    """
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.doc', '.docx']
        file_extension = '.' + file.filename.split('.')[-1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format. Allowed formats: {', '.join(allowed_extensions)}"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Get user data
        user = await db.users.find_one({"_id": ObjectId(current_user.id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Extract profile data
        result = await profile_service.extract_profile_from_cv(file_content, file.filename, user)
        
        return JSONResponse(result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in auto-fill from CV: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the CV"
        )

@router.post("/auto-fill/extract-from-existing-cv")
async def extract_from_existing_cv(
    current_user: User = Depends(get_current_user),
    db = Depends(get_async_db)
):
    """
    Extract profile information from user's existing CV
    """
    try:
        # Get user data
        user = await db.users.find_one({"_id": ObjectId(current_user.id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if user has a CV uploaded
        if not user.get('profile', {}).get('cvUrl'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No CV uploaded. Please upload a CV first."
            )
        
        # Get CV file from storage (you'll need to implement this based on your storage solution)
        # For now, we'll use the existing CV parsing logic
        cv_url = user['profile']['cvUrl']
        
        # Extract profile data using existing CV data
        # This is a simplified approach - you might want to re-parse the actual file
        existing_cv_data = user.get('cv_data', {})
        if not existing_cv_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No CV data available. Please re-upload your CV."
            )
        
        # Format existing CV data for profile
        profile_data = profile_service._format_for_profile(existing_cv_data)
        
        return JSONResponse({
            "success": True,
            "message": "Profile data extracted from existing CV successfully",
            "data": profile_data,
            "extraction_method": "existing_cv",
            "extracted_at": datetime.now().isoformat()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting from existing CV: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while extracting profile data"
        )

@router.post("/auto-fill/linkedin")
async def auto_fill_from_linkedin(
    current_user: User = Depends(get_current_user),
    db = Depends(get_async_db)
):
    """
    Import profile information from LinkedIn and auto-fill profile
    """
    try:
        # Get user data
        user = await db.users.find_one({"_id": ObjectId(current_user.id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Import profile data
        result = await profile_service.import_profile_from_linkedin(user)
        
        return JSONResponse(result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in auto-fill from LinkedIn: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while importing from LinkedIn"
        )

@router.post("/auto-fill/apply")
async def apply_auto_filled_profile(
    profile_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db = Depends(get_async_db)
):
    """
    Apply auto-filled profile data to user profile
    """
    try:
        # Prepare update data
        update_data = {
            "updated_at": datetime.now()
        }
        
        # Map profile data to database fields
        field_mapping = {
            'name': 'profile.name',
            'email': 'profile.email',
            'phone': 'profile.phone',
            'location': 'profile.location',
            'title': 'profile.title',
            'summary': 'profile.summary',
            'skills': 'profile.skills',
            'experience': 'profile.experience',
            'education': 'profile.education',
            'languages': 'profile.languages',
            'certifications': 'profile.certifications',
            'linkedin_url': 'profile.linkedin_url',
            'github_url': 'profile.github_url',
            'portfolio_url': 'profile.portfolio_url'
        }
        
        for field, db_field in field_mapping.items():
            if field in profile_data and profile_data[field] is not None:
                update_data[db_field] = profile_data[field]
        
        # Update user profile
        result = await db.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            logger.warning(f"No changes made to profile for user {current_user.id}")
        
        logger.info(f"Profile auto-filled successfully for user {current_user.id}")
        
        return JSONResponse({
            "success": True,
            "message": "Profile updated successfully",
            "updated_fields": list(profile_data.keys()),
            "updated_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error applying auto-filled profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating profile"
        )

@router.get("/auto-fill/preview")
async def preview_auto_filled_profile(
    source: str,  # 'cv' or 'linkedin'
    current_user: User = Depends(get_current_user),
    db = Depends(get_async_db)
):
    """
    Preview auto-filled profile data without applying it
    """
    try:
        # Get user data
        user = await db.users.find_one({"_id": ObjectId(current_user.id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if source == 'linkedin':
            result = await profile_service.import_profile_from_linkedin(user)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid source. Use 'linkedin' for LinkedIn import"
            )
        
        return JSONResponse({
            "success": True,
            "message": "Profile preview generated successfully",
            "data": result["data"],
            "source": source,
            "preview_at": datetime.now().isoformat()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error previewing auto-filled profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating preview"
        ) 