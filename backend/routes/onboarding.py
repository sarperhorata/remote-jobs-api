from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from typing import Optional
import os
import aiofiles
import uuid
from backend.database import get_async_db
from backend.schemas.user import (
    EmailOnlyRegister, EmailVerification, SetPassword, 
    LinkedInProfile, ProfileCompletion
)
from backend.utils.email import (
    create_email_verification_token, 
    verify_token, 
    send_verification_email
)
import logging
from bson import ObjectId
import jwt
from jwt.exceptions import InvalidTokenError as JWTError
from passlib.context import CryptContext
from datetime import datetime
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase
import httpx
import json

router = APIRouter(prefix="/onboarding", tags=["onboarding"])

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)

# LinkedIn OAuth Configuration
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
LINKEDIN_REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:3000/onboarding/linkedin-callback")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

class OnboardingResponse(BaseModel):
    message: str
    user_id: Optional[str] = None
    onboarding_step: int
    next_step: str
    access_token: Optional[str] = None

@router.post("/register-email", response_model=OnboardingResponse)
async def register_with_email_only(
    user_data: EmailOnlyRegister,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Step 1: Register with email only and send verification email."""
    try:
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            if existing_user.get("email_verified", False):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Bu email adresi zaten kayıtlı ve doğrulanmış"
                )
            else:
                # Resend verification email for unverified user
                user_id = str(existing_user["_id"])
                verification_token = create_email_verification_token(user_data.email)
                send_verification_email(user_data.email, verification_token)
                
                return OnboardingResponse(
                    message="Doğrulama emaili tekrar gönderildi",
                    user_id=user_id,
                    onboarding_step=0,
                    next_step="email_verification"
                )
        
        # Create new user with minimal info
        user_dict = {
            "email": user_data.email,
            "name": None,
            "password": None,
            "is_active": False,  # Not active until email verified
            "email_verified": False,
            "onboarding_completed": False,
            "onboarding_step": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.users.insert_one(user_dict)
        user_id = str(result.inserted_id)
        
        # Create and send verification email
        verification_token = create_email_verification_token(user_data.email)
        email_sent = send_verification_email(user_data.email, verification_token)
        
        if not email_sent:
            logger.error(f"Failed to send verification email to {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Email gönderiminde hata oluştu"
            )
        
        return OnboardingResponse(
            message="Kayıt başarılı! Email adresinizi kontrol edin",
            user_id=user_id,
            onboarding_step=0,
            next_step="email_verification"
        )
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Kayıt sırasında hata oluştu"
        )

@router.post("/verify-email", response_model=OnboardingResponse)
async def verify_email(
    verification_data: EmailVerification,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Step 2: Verify email and activate user."""
    try:
        # Verify token
        payload = verify_token(verification_data.token)
        if not payload or payload.get("type") != "email_verification":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Geçersiz veya süresi dolmuş token"
            )
        
        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token'da email bilgisi bulunamadı"
            )
        
        # Find and update user
        user = await db.users.find_one({"email": email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kullanıcı bulunamadı"
            )
        
        if user.get("email_verified", False):
            return OnboardingResponse(
                message="Email zaten doğrulanmış",
                user_id=str(user["_id"]),
                onboarding_step=1,
                next_step="set_password"
            )
        
        # Update user
        await db.users.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "email_verified": True,
                    "is_active": True,
                    "onboarding_step": 1,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return OnboardingResponse(
            message="Email başarıyla doğrulandı!",
            user_id=str(user["_id"]),
            onboarding_step=1,
            next_step="set_password"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email doğrulama sırasında hata oluştu"
        )

@router.post("/set-password", response_model=OnboardingResponse)
async def set_password(
    password_data: SetPassword,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Step 3: Set user password."""
    try:
        # Verify token
        payload = verify_token(password_data.token)
        if not payload or payload.get("type") != "email_verification":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Geçersiz veya süresi dolmuş token"
            )
        
        # Check password confirmation
        if password_data.password != password_data.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Şifreler eşleşmiyor"
            )
        
        email = payload.get("sub")
        user = await db.users.find_one({"email": email, "email_verified": True})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doğrulanmış kullanıcı bulunamadı"
            )
        
        # Hash password and update user
        hashed_password = get_password_hash(password_data.password)
        await db.users.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "hashed_password": hashed_password,
                    "onboarding_step": 2,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return OnboardingResponse(
            message="Şifre başarıyla belirlendi!",
            user_id=str(user["_id"]),
            onboarding_step=2,
            next_step="profile_setup"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Set password error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Şifre belirlenirken hata oluştu"
        )

@router.get("/linkedin-auth-url")
async def get_linkedin_auth_url():
    """Get LinkedIn OAuth URL."""
    if not LINKEDIN_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="LinkedIn OAuth konfigürasyonu eksik"
        )
    
    # Generate state for security
    state = str(uuid.uuid4())
    
    auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization?"
        f"response_type=code&"
        f"client_id={LINKEDIN_CLIENT_ID}&"
        f"redirect_uri={LINKEDIN_REDIRECT_URI}&"
        f"state={state}&"
        f"scope=r_liteprofile%20r_emailaddress"
    )
    
    return {"auth_url": auth_url, "state": state}

@router.post("/linkedin-callback")
async def linkedin_callback(
    code: str,
    state: str,
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Handle LinkedIn OAuth callback."""
    try:
        if not code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authorization code gerekli"
            )
        
        # Exchange code for access token
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": LINKEDIN_REDIRECT_URI,
            "client_id": LINKEDIN_CLIENT_ID,
            "client_secret": LINKEDIN_CLIENT_SECRET,
        }
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            token_response.raise_for_status()
            token_json = token_response.json()
            access_token = token_json["access_token"]
            
            # Get LinkedIn profile
            profile_url = "https://api.linkedin.com/v2/people/~"
            headers = {"Authorization": f"Bearer {access_token}"}
            
            profile_response = await client.get(profile_url, headers=headers)
            profile_response.raise_for_status()
            profile_data = profile_response.json()
            
            # Get LinkedIn email
            email_url = "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))"
            email_response = await client.get(email_url, headers=headers)
            email_response.raise_for_status()
            email_data = email_response.json()
            
            linkedin_email = None
            if email_data.get("elements"):
                linkedin_email = email_data["elements"][0]["handle~"]["emailAddress"]
        
        # Update user with LinkedIn data
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kullanıcı bulunamadı"
            )
        
        linkedin_profile = {
            "id": profile_data.get("id"),
            "firstName": profile_data.get("firstName", {}).get("localized", {}),
            "lastName": profile_data.get("lastName", {}).get("localized", {}),
            "email": linkedin_email,
            "profilePicture": profile_data.get("profilePicture"),
            "raw_data": profile_data
        }
        
        await db.users.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "linkedin_id": profile_data.get("id"),
                    "linkedin_profile": linkedin_profile,
                    "onboarding_step": 3,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return OnboardingResponse(
            message="LinkedIn profili başarıyla bağlandı!",
            user_id=user_id,
            onboarding_step=3,
            next_step="complete_profile"
        )
        
    except httpx.HTTPError as e:
        logger.error(f"LinkedIn API error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="LinkedIn bağlantısında hata oluştu"
        )
    except Exception as e:
        logger.error(f"LinkedIn callback error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="LinkedIn işleminde hata oluştu"
        )

@router.post("/upload-cv")
async def upload_cv(
    user_id: str,
    file: UploadFile = File(...),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Upload CV file."""
    try:
        # Validate file
        if file.content_type not in ["application/pdf", "application/msword", 
                                   "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sadece PDF, DOC ve DOCX dosyaları kabul edilir"
            )
        
        # Check file size (max 5MB)
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > 5 * 1024 * 1024:  # 5MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dosya boyutu 5MB'dan küçük olmalıdır"
            )
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1]
        unique_filename = f"{user_id}_{uuid.uuid4()}.{file_extension}"
        file_path = f"backend/uploads/cv/{unique_filename}"
        
        # Save file
        os.makedirs("backend/uploads/cv", exist_ok=True)
        async with aiofiles.open(file_path, "wb") as buffer:
            await buffer.write(content)
        
        # Update user
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "resume_url": f"/uploads/cv/{unique_filename}",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "message": "CV başarıyla yüklendi!",
            "file_url": f"/uploads/cv/{unique_filename}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"CV upload error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="CV yüklenirken hata oluştu"
        )

@router.post("/complete-profile", response_model=OnboardingResponse)
async def complete_profile(
    profile_data: dict,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Complete user profile and finish onboarding."""
    try:
        user_id = profile_data.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID is required"
            )
        
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kullanıcı bulunamadı"
            )
        
        # Update profile data
        update_data = {
            "onboarding_completed": True,
            "onboarding_step": 4,
            "updated_at": datetime.utcnow()
        }
        
        # Map frontend data to backend fields
        if profile_data.get("location"):
            update_data["location"] = profile_data["location"]
        if profile_data.get("job_titles"):
            update_data["job_titles"] = profile_data["job_titles"]
        if profile_data.get("experience_levels"):
            update_data["experience_levels"] = profile_data["experience_levels"]
        if profile_data.get("skills"):
            update_data["skills"] = profile_data["skills"]
        if profile_data.get("salary_ranges"):
            update_data["salary_ranges"] = profile_data["salary_ranges"]
        if profile_data.get("work_types"):
            update_data["work_types"] = profile_data["work_types"]
        if "email_notifications" in profile_data:
            update_data["email_notifications"] = profile_data["email_notifications"]
        if "browser_notifications" in profile_data:
            update_data["browser_notifications"] = profile_data["browser_notifications"]
        
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": update_data}
        )
        
        # Create access token for user
        access_token = create_access_token(data={"sub": user_id})
        
        return OnboardingResponse(
            message="Profile completed successfully!",
            user_id=user_id,
            onboarding_step=4,
            next_step="dashboard",
            access_token=access_token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Complete profile error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profil tamamlanırken hata oluştu"
        )

@router.get("/status/{user_id}")
async def get_onboarding_status(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Get current onboarding status."""
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kullanıcı bulunamadı"
            )
        
        steps = {
            0: "email_verification",
            1: "set_password", 
            2: "profile_setup",
            3: "complete_profile",
            4: "completed"
        }
        
        return {
            "user_id": user_id,
            "onboarding_step": user.get("onboarding_step", 0),
            "next_step": steps.get(user.get("onboarding_step", 0), "email_verification"),
            "email_verified": user.get("email_verified", False),
            "onboarding_completed": user.get("onboarding_completed", False),
            "has_linkedin": user.get("linkedin_id") is not None,
            "has_resume": user.get("resume_url") is not None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get onboarding status error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Onboarding durumu alınırken hata oluştu"
        ) 