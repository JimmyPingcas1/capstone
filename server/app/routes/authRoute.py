from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..db import user_collection
from datetime import datetime, timedelta
import jwt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter()

# Secret key for JWT (load from environment variable)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    token: str
    user: dict

def create_access_token(user_id: str, expires_delta: timedelta = None):
    """Create JWT token"""
    if expires_delta is None:
        expires_delta = timedelta(days=7)
    
    expire = datetime.utcnow() + expires_delta
    to_encode = {"user_id": user_id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/api/v1/login")
async def login(credentials: LoginRequest):
    """Login with email and password"""
    email = credentials.email
    password = credentials.password

    # Hardcoded admin credentials
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "admin123"
    
    # Check hardcoded admin credentials first
    if email == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        # Create JWT token for admin
        token = create_access_token("admin_user_id")
        return {
            "token": token,
            "user": {
                "id": "admin_user_id",
                "email": ADMIN_USERNAME,
                "name": "System Administrator"
            }
        }

    # Check if user exists in database (if user_collection is available)
    if user_collection is not None:
        user = await user_collection.find_one({"email": email})
        
        if user:
            # For now, compare passwords directly (in production, use bcrypt)
            if user.get("password") == password:
                # Create JWT token
                token = create_access_token(str(user["_id"]))
                
                return {
                    "token": token,
                    "user": {
                        "id": str(user["_id"]),
                        "email": user.get("email"),
                        "name": user.get("name", "")
                    }
                }
    
    # If no match found
    raise HTTPException(status_code=401, detail="Invalid email or password")

@router.post("/api/v1/register")
async def register(credentials: LoginRequest):
    """Register a new user"""
    email = credentials.email
    password = credentials.password
    
    # Check if user already exists
    existing_user = await user_collection.find_one({"email": email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user (in production, hash the password!)
    user_doc = {
        "email": email,
        "password": password,
        "created_at": datetime.utcnow()
    }
    
    result = await user_collection.insert_one(user_doc)
    
    # Create token
    token = create_access_token(str(result.inserted_id))
    
    return {
        "token": token,
        "user": {
            "id": str(result.inserted_id),
            "email": email
        }
    }
