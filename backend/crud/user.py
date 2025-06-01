from typing import Optional, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from passlib.context import CryptContext
from backend.models.user import UserCreate, UserUpdate, UserResponse, UserInDB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password."""
    return pwd_context.verify(plain_password, hashed_password)

async def create_user(db: AsyncIOMotorDatabase, user: UserCreate) -> str:
    """Create a new user."""
    user_dict = user.dict()
    user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
    user_dict["created_at"] = datetime.utcnow()
    user_dict["updated_at"] = datetime.utcnow()
    
    result = await db.users.insert_one(user_dict)
    return str(result.inserted_id)

async def get_user(db: AsyncIOMotorDatabase, user_id: str) -> Optional[UserResponse]:
    """Get a user by ID."""
    if not ObjectId.is_valid(user_id):
        return None
        
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if user:
        user["_id"] = str(user["_id"])
        return UserResponse(**user)
    return None

async def get_user_by_email(db: AsyncIOMotorDatabase, email: str) -> Optional[UserInDB]:
    """Get a user by email."""
    user = await db.users.find_one({"email": email})
    if user:
        user["_id"] = str(user["_id"])
        return UserInDB(**user)
    return None

async def get_user_by_telegram_id(db: AsyncIOMotorDatabase, telegram_user_id: int) -> Optional[UserResponse]:
    """Get a user by Telegram ID."""
    user = await db.users.find_one({"telegram_user_id": telegram_user_id})
    if user:
        user["_id"] = str(user["_id"])
        return UserResponse(**user)
    return None

async def get_users(
    db: AsyncIOMotorDatabase,
    skip: int = 0,
    limit: int = 10,
    is_active: Optional[bool] = None
) -> List[UserResponse]:
    """Get a list of users with optional filtering."""
    query = {}
    if is_active is not None:
        query["is_active"] = is_active
        
    cursor = db.users.find(query).skip(skip).limit(limit)
    users = await cursor.to_list(length=limit)
    return [UserResponse(**{**user, "_id": str(user["_id"])}) for user in users]

async def update_user(
    db: AsyncIOMotorDatabase,
    user_id: str,
    user: UserUpdate
) -> Optional[UserResponse]:
    """Update a user."""
    if not ObjectId.is_valid(user_id):
        return None
        
    update_data = user.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    
    if result.modified_count:
        return await get_user(db, user_id)
    return None

async def delete_user(db: AsyncIOMotorDatabase, user_id: str) -> bool:
    """Delete a user."""
    if not ObjectId.is_valid(user_id):
        return False
        
    result = await db.users.delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count > 0

async def authenticate_user(
    db: AsyncIOMotorDatabase,
    email: str,
    password: str
) -> Optional[UserInDB]:
    """Authenticate a user."""
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user 