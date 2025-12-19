from typing import Optional
from supabase import Client
from app.models.user import User
from app.core.exceptions import ConflictException, NotFoundException
from datetime import date


class UserRepository:
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.table = "users"
    
    async def create_user(
        self, 
        email: str, 
        password_hash: str,
        first_name: str,
        last_name: str,
        birth_date: date
    ) -> User:
        """Create a new user in the database"""
        try:
            response = self.supabase.table(self.table).insert({
                "email": email,
                "password_hash": password_hash,
                "first_name": first_name,
                "last_name": last_name,
                "birth_date": birth_date.isoformat()
            }).execute()
            
            if not response.data:
                raise Exception("Failed to create user")
            
            return User(**response.data[0])
        except Exception as e:
            error_msg = str(e).lower()
            if "duplicate key" in error_msg or "unique" in error_msg:
                raise ConflictException(detail="Email already registered")
            if "check_age_18" in error_msg:
                raise ConflictException(detail="You must be at least 18 years old")
            raise e
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        response = self.supabase.table(self.table).select("*").eq("email", email).execute()
        
        if not response.data:
            return None
        
        return User(**response.data[0])
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        response = self.supabase.table(self.table).select("*").eq("id", user_id).execute()
        
        if not response.data:
            return None
        
        return User(**response.data[0])
    
    async def user_exists(self, email: str) -> bool:
        """Check if user exists by email"""
        response = self.supabase.table(self.table).select("id").eq("email", email).execute()
        return len(response.data) > 0
    async def update_user(
        self,
        user_id: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        birth_date: Optional[date] = None
    ) -> User:
        """Update user profile"""
        # Build update data (only include fields that are not None)
        update_data = {}
        if first_name is not None:
            update_data["first_name"] = first_name
        if last_name is not None:
            update_data["last_name"] = last_name
        if birth_date is not None:
            update_data["birth_date"] = birth_date.isoformat()
        
        if not update_data:
            # Nothing to update, just return current user
            return await self.get_user_by_id(user_id)
        
        try:
            response = self.supabase.table(self.table).update(
                update_data
            ).eq("id", user_id).execute()
            
            if not response.data:
                raise NotFoundException(detail="User not found")
            
            return User(**response.data[0])
        except Exception as e:
            error_msg = str(e).lower()
            if "check_age_18" in error_msg:
                raise ConflictException(detail="You must be at least 18 years old")
            raise e
    
    async def update_password(self, user_id: str, new_password_hash: str) -> bool:
        """Update user password"""
        response = self.supabase.table(self.table).update({
            "password_hash": new_password_hash
        }).eq("id", user_id).execute()
        
        if not response.data:
            raise NotFoundException(detail="User not found")
        
        return True
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user account (soft delete or hard delete)"""
        response = self.supabase.table(self.table).delete().eq("id", user_id).execute()
        
        if not response.data:
            raise NotFoundException(detail="User not found")
        
        return True
    async def get_all_users(self, limit: int = 100, offset: int = 0) -> list[User]:
        """Get all users (for admin purposes)"""
        response = self.supabase.table(self.table).select("*").range(offset, offset + limit - 1).execute()
        
        if not response.data:
            return []
        
        return [User(**user_data) for user_data in response.data]
    
    async def get_user_count(self) -> int:
        """Get total number of users"""
        response = self.supabase.table(self.table).select("id", count="exact").execute()
        return response.count if response.count else 0