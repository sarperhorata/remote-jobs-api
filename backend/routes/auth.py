from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer, HTTPBearer
from typing import Optional, Dict
import os
from backend.database import get_async_db
from backend.schemas.user import UserCreate, Token
from backend.utils.email import create_password_reset_token, verify_token, send_password_reset_email
import logging
from bson import ObjectId
import jwt
from jwt.exceptions import InvalidTokenError as JWTError
from passlib.context import CryptContext
from datetime import datetime
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorDatabase
import requests
from backend.utils.linkedin import LinkedInIntegration

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Get the current user from the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """Get the current active user."""
    if not current_user.get("is_active", True):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Alias for compatibility with other modules
get_current_user_dependency = get_current_active_user

# Response models
class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    email: str
    name: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

@router.post("/register", response_model=AuthResponse)
async def register_user(
    user: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Register a new user."""
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user (compatible with new onboarding system)
    hashed_password = get_password_hash(user.password)
    user_dict = {
        "email": user.email,
        "name": user.name,  # Updated to match new model
        "full_name": user.name,  # Keep both for backward compatibility
        "hashed_password": hashed_password,
        "is_active": True,
        "email_verified": True,  # Direct register bypasses email verification
        "onboarding_completed": True,  # Direct register is considered complete
        "onboarding_step": 4,  # Completed onboarding
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.users.insert_one(user_dict)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(result.inserted_id)})
    
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=str(result.inserted_id),
        email=user.email,
        name=user.name
    )

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Login to get access token."""
    # Find user
    user = await db.users.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user.get("hashed_password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if email is verified (for new onboarding users)
    if user.get("email_verified") is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your email and verify your account.",
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user["_id"])})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user_dependency)):
    """Get current user information."""
    return {
        "id": str(current_user["_id"]),
        "email": current_user["email"],
        "full_name": current_user.get("full_name", ""),
        "is_active": current_user.get("is_active", True)
    }

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user_dependency)):
    """Logout user and invalidate token."""
    # In a real implementation, you might want to blacklist the token
    # For now, we'll just return a success message
    # The client should remove the token from storage
    return {"message": "Successfully logged out"}

@router.get("/google/auth-url")
async def get_google_auth_url():
    """Get Google OAuth authorization URL"""
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/google/callback")
    
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth not configured"
        )
    
    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={GOOGLE_REDIRECT_URI}&"
        f"scope=openid%20email%20profile&"
        f"response_type=code&"
        f"access_type=offline"
    )
    
    return {"auth_url": auth_url}

@router.post("/google/callback", response_model=AuthResponse)
async def google_callback(
    code: str,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Handle Google OAuth callback and login/register user"""
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No authorization code provided"
        )
    
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/google/callback")
    
    if not all([GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET]):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth not configured"
        )
    
    try:
        import httpx
        
        # Exchange code for access token
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            token_response.raise_for_status()
            token_json = token_response.json()
            access_token = token_json["access_token"]
            
            # Get user info from Google
            user_info_url = f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}"
            user_response = await client.get(user_info_url)
            user_response.raise_for_status()
            user_data = user_response.json()
            
            email = user_data.get("email")
            name = user_data.get("name")
            google_id = user_data.get("id")
            picture = user_data.get("picture")
            
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email not provided by Google"
                )
            
            # Check if user exists
            existing_user = await db.users.find_one({"email": email})
            
            if existing_user:
                # Login existing user
                user_id = existing_user["_id"]
                
                # Update Google info if needed
                await db.users.update_one(
                    {"_id": user_id},
                    {
                        "$set": {
                            "google_id": google_id,
                            "profile_picture": picture,
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
            else:
                # Register new user
                user_dict = {
                    "email": email,
                    "name": name,
                    "full_name": name,
                    "google_id": google_id,
                    "profile_picture": picture,
                    "is_active": True,
                    "email_verified": True,  # Google emails are verified
                    "onboarding_completed": True,
                    "onboarding_step": 4,
                    "auth_provider": "google",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                result = await db.users.insert_one(user_dict)
                user_id = result.inserted_id
            
            # Create access token
            access_token = create_access_token(data={"sub": str(user_id)})
            
            return AuthResponse(
                access_token=access_token,
                token_type="bearer",
                user_id=str(user_id),
                email=email,
                name=name
            )
            
    except httpx.HTTPError as e:
        logger.error(f"Google OAuth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to authenticate with Google"
        )
    except Exception as e:
        logger.error(f"Google callback error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during Google authentication"
        )

@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Send password reset email."""
    # Find user
    user = await db.users.find_one({"email": request.email})
    if not user:
        # For security, don't reveal if email exists or not
        return {"message": "If the email exists, a password reset link has been sent."}
    
    # Create password reset token
    reset_token = create_password_reset_token(request.email)
    
    # Send password reset email
    email_sent = send_password_reset_email(request.email, reset_token)
    
    if not email_sent:
        logger.error(f"Failed to send password reset email to {request.email}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send password reset email"
        )
    
    return {"message": "If the email exists, a password reset link has been sent."}

@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Reset user password with token."""
    # Verify token
    payload = verify_token(request.token)
    if not payload or payload.get("type") != "password_reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token format"
        )
    
    # Find user
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Hash new password and update user
    hashed_password = get_password_hash(request.new_password)
    await db.users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "hashed_password": hashed_password,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return {"message": "Password successfully reset"}

# LinkedIn OAuth endpoints
@router.post("/linkedin/token")
async def linkedin_token_exchange(request: dict):
    """Exchange LinkedIn authorization code for access token"""
    try:
        code = request.get('code')
        state = request.get('state')
        
        if not code:
            raise HTTPException(status_code=400, detail="Authorization code is required")
        
        # Exchange code for access token
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/auth/linkedin/callback",
            'client_id': os.getenv('LINKEDIN_CLIENT_ID'),
            'client_secret': os.getenv('LINKEDIN_CLIENT_SECRET')
        }
        
        token_response = requests.post(token_url, data=token_data, timeout=30)
        
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code for token")
        
        return token_response.json()
        
    except Exception as e:
        logging.error(f"LinkedIn token exchange error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/linkedin/profile")
async def linkedin_profile(request: Request):
    """Fetch LinkedIn profile data using access token"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(status_code=401, detail="Access token is required")
        
        access_token = auth_header.split(' ')[1]
        
        # Fetch basic profile info
        profile_url = "https://api.linkedin.com/v2/people/~?projection=(id,firstName,lastName,emailAddress,profilePicture(displayImage~:playableStreams))"
        profile_headers = {'Authorization': f'Bearer {access_token}'}
        
        profile_response = requests.get(profile_url, headers=profile_headers, timeout=30)
        
        if profile_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch LinkedIn profile")
        
        profile_data = profile_response.json()
        
        # Fetch email address
        email_url = "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))"
        email_response = requests.get(email_url, headers=profile_headers, timeout=30)
        
        email_data = {}
        if email_response.status_code == 200:
            email_data = email_response.json()
        
        # Format profile data
        formatted_profile = {
            'id': profile_data.get('id'),
            'name': f"{profile_data.get('firstName', {}).get('localized', {}).get('en_US', '')} {profile_data.get('lastName', {}).get('localized', {}).get('en_US', '')}".strip(),
            'email': email_data.get('elements', [{}])[0].get('handle~', {}).get('emailAddress', '') if email_data.get('elements') else '',
            'picture': '',
            'profileUrl': f"https://www.linkedin.com/in/{profile_data.get('id', '')}",
            'experience': [],  # Would need additional API calls for full experience data
            'education': []    # Would need additional API calls for full education data
        }
        
        # Extract profile picture if available
        profile_pic = profile_data.get('profilePicture', {}).get('displayImage~', {})
        if profile_pic and 'elements' in profile_pic:
            elements = profile_pic['elements']
            if elements and len(elements) > 0:
                identifiers = elements[0].get('identifiers', [])
                if identifiers:
                    formatted_profile['picture'] = identifiers[0].get('identifier', '')
        
        return formatted_profile
        
    except Exception as e:
        logging.error(f"LinkedIn profile fetch error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 

@router.get("/linkedin/auth-url")
async def linkedin_auth_url():
    """LinkedIn OAuth URL'si döner"""
    linkedin = LinkedInIntegration()
    url = linkedin.get_authorization_url()
    return {"auth_url": url}

@router.post("/linkedin/callback", response_model=AuthResponse)
async def linkedin_callback(
    code: str,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """LinkedIn OAuth callback: code ile access_token al, profil çek, kullanıcıyı kaydet/güncelle, JWT döner"""
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code required")
    
    try:
        # Exchange code for access token
        access_token = await linkedin.exchange_code_for_token(code)
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to exchange code for token")
        
        # Get user profile
        profile_data = await linkedin.get_user_profile(access_token)
        if not profile_data:
            raise HTTPException(status_code=400, detail="Failed to fetch LinkedIn profile")
        
        # Check if user exists
        existing_user = await db.users.find_one({"email": profile_data["email"]})
        
        if existing_user:
            # Update existing user with LinkedIn data
            update_data = {
                "linkedin_url": profile_data.get("linkedin_url", ""),
                "profile_photo_url": profile_data.get("profile_photo_url", ""),
                "title": profile_data.get("title", ""),
                "linkedin_connected": True,
                "linkedin_access_token": access_token,  # Store access token for future CV fetch
                "auth_provider": "linkedin",
                "email_verified": True,  # LinkedIn emails are verified
                "onboarding_completed": True,
                "onboarding_step": 4,
                "updated_at": datetime.utcnow()
            }
            
            await db.users.update_one(
                {"_id": existing_user["_id"]},
                {"$set": update_data}
            )
            user_id = str(existing_user["_id"])
        else:
            # Create new user
            user_data = {
                "email": profile_data["email"],
                "name": profile_data["name"],
                "full_name": profile_data["name"],
                "linkedin_url": profile_data.get("linkedin_url", ""),
                "profile_photo_url": profile_data.get("profile_photo_url", ""),
                "title": profile_data.get("title", ""),
                "linkedin_connected": True,
                "linkedin_access_token": access_token,  # Store access token for future CV fetch
                "auth_provider": "linkedin",
                "email_verified": True,  # LinkedIn emails are verified
                "onboarding_completed": True,
                "onboarding_step": 4,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = await db.users.insert_one(user_data)
            user_id = str(result.inserted_id)
        
        # Generate JWT token
        token_data = {"sub": user_id, "email": profile_data["email"]}
        access_token_jwt = create_access_token(data=token_data)
        
        return AuthResponse(
            access_token=access_token_jwt,
            token_type="bearer",
            user_id=user_id,
            email=profile_data["email"],
            name=profile_data["name"]
        )
        
    except Exception as e:
        logger.error(f"LinkedIn callback error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/linkedin/fetch-cv")
async def linkedin_fetch_cv(
    current_user: Dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """LinkedIn'den kullanıcının CV'sini çeker ve profilini günceller"""
    try:
        # Check if user has LinkedIn connected
        user = await db.users.find_one({"_id": ObjectId(current_user["_id"])})
        if not user or not user.get("linkedin_connected"):
            raise HTTPException(status_code=400, detail="LinkedIn account not connected")
        
        # Get LinkedIn access token from user's stored data or request new one
        # Note: In a real implementation, you'd need to store the access token securely
        # For now, we'll use a placeholder approach
        linkedin_token = user.get("linkedin_access_token")
        if not linkedin_token:
            raise HTTPException(status_code=400, detail="LinkedIn access token not available")
        
        # Fetch comprehensive CV data
        cv_data = await linkedin.get_user_cv_data(linkedin_token)
        if not cv_data:
            raise HTTPException(status_code=400, detail="Failed to fetch LinkedIn CV data")
        
        # Update user profile with CV data
        update_data = {
            "experience": cv_data.get("experience", []),
            "education": cv_data.get("education", []),
            "skills": cv_data.get("skills", []),
            "summary": cv_data.get("summary", ""),
            "location": cv_data.get("location", ""),
            "industry": cv_data.get("industry", ""),
            "cv_source": "linkedin",
            "cv_updated_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.users.update_one(
            {"_id": ObjectId(current_user["_id"])},
            {"$set": update_data}
        )
        
        return {
            "message": "CV data successfully imported from LinkedIn",
            "cv_data": {
                "experience_count": len(cv_data.get("experience", [])),
                "education_count": len(cv_data.get("education", [])),
                "skills_count": len(cv_data.get("skills", [])),
                "updated_at": update_data["cv_updated_at"]
            }
        }
        
    except Exception as e:
        logger.error(f"LinkedIn CV fetch error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 