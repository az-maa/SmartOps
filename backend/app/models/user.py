from datetime import datetime, date
from pydantic import BaseModel, EmailStr
from uuid import UUID


class User(BaseModel):
    """Domain model for User"""
    id: UUID
    email: EmailStr
    password_hash: str
    first_name: str
    last_name: str
    birth_date: date
    created_at: datetime
    
    class Config:
        from_attributes = True
