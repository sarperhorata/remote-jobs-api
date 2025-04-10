from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional
import os
import shutil
from ..database import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserResponse, Token, UserLogin
from ..utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_active_user,
    get_current_user
)
from ..utils.linkedin import fetch_linkedin_data
from ..utils.cv_parser import parse_cv_file
from ..utils.email import (
    create_email_verification_token,
    create_password_reset_token,
    verify_token,
    send_verification_email,
    send_password_reset_email
)
from ..utils.security import SecurityUtils
from ..utils.captcha import CaptchaVerifier
import logging

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT ayarları
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

logger = logging.getLogger(__name__)

# CV dosyaları için geçici dizin
UPLOAD_DIR = "uploads/cv"
# CV dosyalarının saklanma süresi (saat)
CV_RETENTION_HOURS = 24

# Dizin yoksa oluştur
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # CAPTCHA doğrulaması
    if user_data.recaptcha_response:
        if not CaptchaVerifier.verify_recaptcha(user_data.recaptcha_response):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CAPTCHA verification failed"
            )
    
    # E-posta doğrulaması
    if not SecurityUtils.validate_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    # Şifre güvenlik kontrolü
    if not SecurityUtils.validate_password(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character"
        )
    
    # E-posta ve telefon benzersizlik kontrolü
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Telefon kontrolü
    if user_data.phone and db.query(User).filter(User.phone == user_data.phone).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )
    
    # LinkedIn verilerini çek
    linkedin_data = {}
    if user_data.linkedin_url:
        try:
            linkedin_data = fetch_linkedin_data(user_data.linkedin_url)
            if linkedin_data and "name" in linkedin_data:
                user_data.name = user_data.name or linkedin_data["name"]
                user_data.title = linkedin_data.get('title', user_data.title)
        except Exception as e:
            logger.error(f"Error fetching LinkedIn data: {str(e)}")
    
    # Kullanıcı oluştur
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        name=user_data.name,
        phone=user_data.phone,
        linkedin_url=user_data.linkedin_url,
        title=user_data.title,
        subscription_type="free",  # Varsayılan olarak free
        is_email_verified=False  # E-posta doğrulanmamış
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # E-posta doğrulama token'ı oluştur ve gönder
    verification_token = create_email_verification_token(user_data.email)
    send_verification_email(user_data.email, verification_token)
    
    return db_user

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # CAPTCHA doğrulaması
    if form_data.recaptcha_response:
        if not CaptchaVerifier.verify_recaptcha(form_data.recaptcha_response):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CAPTCHA verification failed"
            )
    
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # E-posta doğrulanmamışsa uyarı ver
    if not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your email for verification link."
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.post("/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db)):
    """
    E-posta doğrulama endpoint'i.
    
    Args:
        token: Doğrulama token'ı
        db: Veritabanı oturumu
        
    Returns:
        Dict[str, str]: Başarı mesajı
    """
    payload = verify_token(token)
    if not payload or payload.get("type") != "email_verification":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_email_verified = True
    db.commit()
    
    return {"message": "Email verified successfully"}

@router.post("/resend-verification")
async def resend_verification_email(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """
    E-posta doğrulama bağlantısını yeniden gönderir.
    
    Args:
        current_user: Mevcut kullanıcı
        db: Veritabanı oturumu
        
    Returns:
        Dict[str, str]: Başarı mesajı
    """
    if current_user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    verification_token = create_email_verification_token(current_user.email)
    send_verification_email(current_user.email, verification_token)
    
    return {"message": "Verification email sent"}

@router.post("/forgot-password")
async def forgot_password(email: str, db: Session = Depends(get_db)):
    """
    Şifre sıfırlama e-postası gönderir.
    
    Args:
        email: E-posta adresi
        db: Veritabanı oturumu
        
    Returns:
        Dict[str, str]: Başarı mesajı
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Şifre sıfırlama token'ı oluştur
    reset_token = create_password_reset_token(email)
    
    # Şifre sıfırlama e-postası gönder
    send_password_reset_email(email, reset_token)
    
    return {"message": "Password reset email sent"}

@router.post("/reset-password")
async def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    """
    Şifreyi sıfırlar.
    
    Args:
        token: Şifre sıfırlama token'ı
        new_password: Yeni şifre
        db: Veritabanı oturumu
        
    Returns:
        Dict[str, str]: Başarı mesajı
    """
    # Token'ı doğrula
    payload = verify_token(token)
    if not payload or payload.get("type") != "password_reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    return {"message": "Password reset successful"}

@router.post("/upload-cv")
async def upload_cv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Dosya uzantısını kontrol et
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ['.pdf', '.doc', '.docx']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and Word documents are allowed"
        )
    
    # Dosya adını oluştur
    file_name = f"{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    
    # Dosyayı kaydet
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # CV'yi parse et
    cv_data = parse_cv_file(file_path)
    
    # Kullanıcı bilgilerini güncelle
    if cv_data:
        if cv_data.get('name'):
            current_user.name = cv_data['name']
        if cv_data.get('email'):
            current_user.email = cv_data['email']
        if cv_data.get('phone'):
            current_user.phone = cv_data['phone']
        if cv_data.get('title'):
            current_user.title = cv_data['title']
        if cv_data.get('experience'):
            current_user.experience = cv_data['experience']
        if cv_data.get('education'):
            current_user.education = cv_data['education']
        if cv_data.get('skills'):
            current_user.skills = cv_data['skills']
        
        db.commit()
    
    # Dosyayı 24 saat sonra silmek için zamanlayıcı ayarla
    # TODO: Zamanlayıcı ayarla
    
    return {"message": "CV uploaded and parsed successfully", "data": cv_data}

@router.post("/link-social-account")
async def link_social_account(
    platform: str,
    account_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if platform == "linkedin":
        current_user.linkedin_url = account_id
    elif platform == "github":
        current_user.github_url = account_id
    elif platform == "twitter":
        current_user.twitter_url = account_id
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported platform"
        )
    
    db.commit()
    return {"message": f"{platform} account linked successfully"}

@router.delete("/unlink-social-account")
async def unlink_social_account(
    platform: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if platform == "linkedin":
        current_user.linkedin_url = None
    elif platform == "github":
        current_user.github_url = None
    elif platform == "twitter":
        current_user.twitter_url = None
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported platform"
        )
    
    db.commit()
    return {"message": f"{platform} account unlinked successfully"} 