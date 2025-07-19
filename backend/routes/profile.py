import os
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
from typing import Optional
import aiofiles
from datetime import datetime
import uuid

from ..services.cv_parser_service import cv_parser_service
from ..database.db import get_database
from ..models.user import UserResponse as User
from ..utils.auth import get_current_user
from backend.utils.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/profile", tags=["profile"])

settings = get_settings()

@router.post("/upload-cv")
async def upload_and_parse_cv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and parse CV file to extract profile information
    """
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.doc', '.docx']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file format. Allowed formats: {', '.join(allowed_extensions)}"
            )
        
        # Validate file size (5MB limit)
        max_size = 5 * 1024 * 1024  # 5MB
        if file.size and file.size > max_size:
            raise HTTPException(
                status_code=400,
                detail="File size too large. Maximum size is 5MB."
            )
        
        # Read file content
        file_content = await file.read()
        
        # Parse CV
        parsed_data = cv_parser_service.parse_cv(file_content, file.filename)
        
        # Save file to uploads directory
        upload_dir = "uploads/cv"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        safe_filename = f"{current_user.id}_{timestamp}_{unique_id}{file_extension}"
        file_path = os.path.join(upload_dir, safe_filename)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        # Update user profile with parsed data
        db = get_database()
        
        # Prepare update data
        update_data = {
            "profile.cv_url": file_path,
            "profile.cv_uploaded_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Add parsed data to update
        if parsed_data.get('name'):
            update_data["profile.name"] = parsed_data['name']
        if parsed_data.get('email'):
            update_data["profile.email"] = parsed_data['email']
        if parsed_data.get('phone'):
            update_data["profile.phone"] = parsed_data['phone']
        if parsed_data.get('location'):
            update_data["profile.location"] = parsed_data['location']
        if parsed_data.get('summary'):
            update_data["profile.summary"] = parsed_data['summary']
        if parsed_data.get('skills'):
            update_data["profile.skills"] = parsed_data['skills']
        if parsed_data.get('experience'):
            update_data["profile.experience"] = parsed_data['experience']
        if parsed_data.get('education'):
            update_data["profile.education"] = parsed_data['education']
        if parsed_data.get('languages'):
            update_data["profile.languages"] = parsed_data['languages']
        if parsed_data.get('certifications'):
            update_data["profile.certifications"] = parsed_data['certifications']
        
        # Update user in database
        result = await db.users.update_one(
            {"_id": current_user.id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            logger.warning(f"Failed to update user profile for user {current_user.id}")
        
        logger.info(f"CV uploaded and parsed successfully for user {current_user.id}")
        
        return JSONResponse({
            "success": True,
            "message": "CV uploaded and parsed successfully",
            "data": {
                "parsed_data": parsed_data,
                "file_path": file_path,
                "filename": safe_filename
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading CV: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the CV file"
        )

@router.get("/cv-preview/{user_id}")
async def get_cv_preview(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get CV preview for a user (only for own CV or if admin)
    """
    try:
        # Check if user can access this CV
        if current_user.id != user_id and current_user.role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )
        
        db = get_database()
        user = await db.users.find_one({"_id": user_id})
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        profile = user.get("profile", {})
        
        return JSONResponse({
            "success": True,
            "data": {
                "cv_url": profile.get("cv_url"),
                "cv_uploaded_at": profile.get("cv_uploaded_at"),
                "name": profile.get("name"),
                "email": profile.get("email"),
                "phone": profile.get("phone"),
                "location": profile.get("location"),
                "summary": profile.get("summary"),
                "skills": profile.get("skills", []),
                "experience": profile.get("experience", []),
                "education": profile.get("education", []),
                "languages": profile.get("languages", []),
                "certifications": profile.get("certifications", [])
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting CV preview: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while retrieving CV preview"
        )

@router.delete("/cv")
async def delete_cv(
    current_user: User = Depends(get_current_user)
):
    """
    Delete user's CV file
    """
    try:
        db = get_database()
        
        # Get current user data
        user = await db.users.find_one({"_id": current_user.id})
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        profile = user.get("profile", {})
        cv_url = profile.get("cv_url")
        
        if not cv_url:
            raise HTTPException(
                status_code=404,
                detail="No CV file found"
            )
        
        # Delete file from filesystem
        if os.path.exists(cv_url):
            os.remove(cv_url)
            logger.info(f"CV file deleted: {cv_url}")
        
        # Update user profile to remove CV reference
        result = await db.users.update_one(
            {"_id": current_user.id},
            {
                "$unset": {
                    "profile.cv_url": "",
                    "profile.cv_uploaded_at": ""
                },
                "$set": {
                    "updated_at": datetime.now()
                }
            }
        )
        
        if result.modified_count == 0:
            logger.warning(f"Failed to update user profile for user {current_user.id}")
        
        return JSONResponse({
            "success": True,
            "message": "CV deleted successfully"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting CV: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while deleting the CV"
        ) 