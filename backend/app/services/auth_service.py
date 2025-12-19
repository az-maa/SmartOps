from datetime import timedelta
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserLogin, TokenResponse, UserResponse, UserUpdate, PasswordChange
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.exceptions import UnauthorizedException, ConflictException, NotFoundException
from app.config import get_settings

settings = get_settings()


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    async def register_user(self, user_data: UserCreate) -> TokenResponse:
        """Register a new user and return access token"""
        # Check if user already exists
        if await self.user_repo.user_exists(user_data.email):
            raise ConflictException(detail="Email already registered")
        
        # Hash password
        password_hash = get_password_hash(user_data.password)
        
        # Create user
        user = await self.user_repo.create_user(
            email=user_data.email,
            password_hash=password_hash,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            birth_date=user_data.birth_date
        )
        
        # Generate token
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return TokenResponse(
            access_token=access_token,
            user=UserResponse.model_validate(user)
        )
    
    async def login_user(self, login_data: UserLogin) -> TokenResponse:
        """Authenticate user and return access token"""
        # Get user by email
        user = await self.user_repo.get_user_by_email(login_data.email)
        
        if not user:
            raise UnauthorizedException(detail="Invalid email or password")
        
        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            raise UnauthorizedException(detail="Invalid email or password")
        
        # Generate token
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return TokenResponse(
            access_token=access_token,
            user=UserResponse.model_validate(user)
        )
    
    async def get_current_user(self, user_id: str) -> UserResponse:
        """Get current user information"""
        user = await self.user_repo.get_user_by_id(user_id)
        
        if not user:
            raise UnauthorizedException(detail="User not found")
        
        return UserResponse.model_validate(user)
    async def update_user_profile(self, user_id: str, update_data: 'UserUpdate') -> UserResponse:
        """Update user profile information"""
        # Get current user to verify they exist
        current_user = await self.user_repo.get_user_by_id(user_id)
        if not current_user:
            raise UnauthorizedException(detail="User not found")
        
        # Update user
        updated_user = await self.user_repo.update_user(
            user_id=user_id,
            first_name=update_data.first_name,
            last_name=update_data.last_name,
            birth_date=update_data.birth_date
        )
        
        return UserResponse.model_validate(updated_user)
    
    async def change_password(self, user_id: str, password_change: 'PasswordChange') -> bool:
        """Change user password"""
        # Get current user
        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            raise UnauthorizedException(detail="User not found")
        
        # Verify current password
        if not verify_password(password_change.current_password, user.password_hash):
            raise UnauthorizedException(detail="Current password is incorrect")
        
        # Check new password is different
        if verify_password(password_change.new_password, user.password_hash):
            raise ConflictException(detail="New password must be different from current password")
        
        # Hash new password
        new_password_hash = get_password_hash(password_change.new_password)
        
        # Update password
        return await self.user_repo.update_password(user_id, new_password_hash)
    
    async def delete_account(self, user_id: str, password: str) -> bool:
        """Delete user account (requires password confirmation)"""
        # Get current user
        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            raise UnauthorizedException(detail="User not found")
        
        # Verify password before deletion
        if not verify_password(password, user.password_hash):
            raise UnauthorizedException(detail="Password is incorrect")
        
        # Delete user
        return await self.user_repo.delete_user(user_id)
    async def get_all_users(self, limit: int = 100, offset: int = 0) -> dict:
        """Get all users with pagination"""
        users = await self.user_repo.get_all_users(limit=limit, offset=offset)
        total = await self.user_repo.get_user_count()
        
        return {
            "users": [UserResponse.model_validate(user) for user in users],
            "total": total,
            "limit": limit,
            "offset": offset
        }
    
    async def get_user_by_id(self, user_id: str) -> UserResponse:
        """Get any user by ID (for admin purposes)"""
        user = await self.user_repo.get_user_by_id(user_id)
        
        if not user:
            raise NotFoundException(detail="User not found")
        
        return UserResponse.model_validate(user)