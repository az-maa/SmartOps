from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime, date
from uuid import UUID
from typing import Optional
import re


class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    birth_date: date
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Validate password has:
        - At least 8 characters
        - At least 1 uppercase letter
        - At least 1 lowercase letter
        - At least 1 number
        - At least 1 special character
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character (!@#$%^&*(),.?":{}|<>)')
        
        return v
    
    @field_validator('birth_date')
    @classmethod
    def validate_age(cls, v: date) -> date:
        """Validate user is at least 18 years old"""
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        
        if age < 18:
            raise ValueError('You must be at least 18 years old to register')
        
        if age > 120:
            raise ValueError('Invalid birth date')
        
        return v
    
    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name contains only letters and spaces"""
        if not re.match(r'^[a-zA-Z\s]+$', v):
            raise ValueError('Name must contain only letters and spaces')
        return v.strip()


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user data in responses (no password)"""
    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    birth_date: date
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for authentication token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
class UserUpdate(BaseModel):
    """Schema for updating user profile (all fields optional)"""
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    birth_date: Optional[date] = None
    
    @field_validator('birth_date')
    @classmethod
    def validate_age(cls, v: Optional[date]) -> Optional[date]:
        """Validate user is at least 18 years old"""
        if v is None:
            return v
        
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        
        if age < 18:
            raise ValueError('You must be at least 18 years old')
        
        if age > 120:
            raise ValueError('Invalid birth date')
        
        return v
    
    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate name contains only letters and spaces"""
        if v is None:
            return v
        
        if not re.match(r'^[a-zA-Z\s]+$', v):
            raise ValueError('Name must contain only letters and spaces')
        return v.strip()


class PasswordChange(BaseModel):
    """Schema for changing password"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Same validation as UserCreate password"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v
    
class UserListResponse(BaseModel):
    """Schema for paginated list of users"""
    users: list[UserResponse]
    total: int
    limit: int
    offset: int


class DeleteAccountRequest(BaseModel):
    """Schema for account deletion request"""
    password: str = Field(..., description="Password confirmation for account deletion")