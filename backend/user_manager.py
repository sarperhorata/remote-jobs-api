from datetime import datetime, timedelta
import redis
from typing import Optional
import jwt
from passlib.context import CryptContext
from models import User, UserCreate
import uuid

class UserManager:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=2)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = "your-secret-key-here"  # Güvenli bir yerde saklanmalı
        self.token_expire_minutes = 60 * 24  # 24 saat
        
    def create_user(self, user: UserCreate) -> Optional[User]:
        # Kullanıcı adı kontrolü
        if self.redis_client.get(f"username:{user.username}"):
            return None
            
        # Yeni kullanıcı oluştur
        user_id = str(uuid.uuid4())
        new_user = User(
            id=user_id,
            email=user.email,
            username=user.username,
            hashed_password=self.pwd_context.hash(user.password)
        )
        
        # Redis'e kaydet
        self.redis_client.set(f"user:{user_id}", new_user.json())
        self.redis_client.set(f"username:{user.username}", user_id)
        
        return new_user
        
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user_id = self.redis_client.get(f"username:{username}")
        if not user_id:
            return None
            
        user_data = self.redis_client.get(f"user:{user_id.decode()}")
        if not user_data:
            return None
            
        user = User.parse_raw(user_data)
        if not self.pwd_context.verify(password, user.hashed_password):
            return None
            
        return user
        
    def create_access_token(self, user: User) -> str:
        expire = datetime.utcnow() + timedelta(minutes=self.token_expire_minutes)
        data = {
            "sub": user.username,
            "exp": expire,
            "user_id": user.id
        }
        return jwt.encode(data, self.secret_key, algorithm="HS256")
        
    def verify_token(self, token: str) -> Optional[User]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            user_id = payload.get("user_id")
            if not user_id:
                return None
                
            user_data = self.redis_client.get(f"user:{user_id}")
            if not user_data:
                return None
                
            return User.parse_raw(user_data)
            
        except jwt.PyJWTError:
            return None 