# Data models
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import uuid4

class UserBase(BaseModel):
    """Base user model with common fields"""
    name: str
    email: EmailStr
    phone: str

class UserCreate(UserBase):
    """Model for creating a new user"""
    pass

class UserUpdate(BaseModel):
    """Model for updating a user"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

class User(UserBase):
    """Complete user model"""
    id: int
    
    class Config:
        from_attributes = True

class UserInDB(UserBase):
    """User model as stored in database"""
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None