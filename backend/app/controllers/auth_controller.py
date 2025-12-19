from fastapi import APIRouter, Depends, Query
from supabase import Client
from app.schemas.user import (
    UserCreate, 
    UserLogin, 
    TokenResponse, 
    UserResponse,
    UserUpdate,
    PasswordChange,
    UserListResponse,
    DeleteAccountRequest
)
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.database.supabase import get_supabase
from app.core.dependencies import get_current_user_id
from app.core.exceptions import BadRequestException

router = APIRouter()


def get_auth_service(supabase: Client = Depends(get_supabase)) -> AuthService:
    """Dependency to get AuthService instance"""
    user_repo = UserRepository(supabase)
    return AuthService(user_repo)


# ==================== AUTHENTICATION ====================

@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    **Register a new user**
    
    Requirements:
    - **email**: Valid email address with @
    - **password**: Min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special char
    - **first_name**: Letters only, 2-50 characters
    - **last_name**: Letters only, 2-50 characters
    - **birth_date**: Must be 18+ years old (format: YYYY-MM-DD)
    
    Returns access token immediately after registration
    """
    return await auth_service.register_user(user_data)


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    **Login with email and password**
    
    Returns JWT access token for authentication
    """
    return await auth_service.login_user(login_data)


# ==================== CURRENT USER ====================

@router.get("/me", response_model=UserResponse)
async def get_me(
    user_id: str = Depends(get_current_user_id),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    **Get current user information**
    
    Requires authentication token in header:
```
    Authorization: Bearer <token>
```
    """
    return await auth_service.get_current_user(user_id)


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    update_data: UserUpdate,
    user_id: str = Depends(get_current_user_id),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    **Update current user profile**
    
    All fields are optional:
    - **first_name**: Updated first name (letters only)
    - **last_name**: Updated last name (letters only)
    - **birth_date**: Updated birth date (must still be 18+)
    
    Requires authentication token
    """
    return await auth_service.update_user_profile(user_id, update_data)


@router.delete("/me")
async def delete_my_account(
    delete_request: DeleteAccountRequest,
    user_id: str = Depends(get_current_user_id),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    **Delete your own account (PERMANENT)**
    
    Send: `{"password": "your_password"}`
    
    This action cannot be undone! All your data will be permanently deleted.
    
    Requires authentication token
    """
    await auth_service.delete_account(user_id, delete_request.password)
    return {"message": "Account deleted successfully"}


# ==================== PASSWORD MANAGEMENT ====================

@router.put("/password")
async def change_my_password(
    password_data: PasswordChange,
    user_id: str = Depends(get_current_user_id),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    **Change your password**
    
    Requirements:
    - **current_password**: Your current password
    - **new_password**: New strong password (same rules as registration)
    
    New password must be different from current password
    
    Requires authentication token
    """
    await auth_service.change_password(user_id, password_data)
    return {"message": "Password changed successfully"}


# ==================== USER MANAGEMENT (Admin/List) ====================

@router.get("/users", response_model=UserListResponse)
async def get_all_users(
    limit: int = Query(default=100, ge=1, le=1000, description="Number of users per page"),
    offset: int = Query(default=0, ge=0, description="Number of users to skip"),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    **Get all users (paginated)**
    
    Query parameters:
    - **limit**: Number of users to return (default: 100, max: 1000)
    - **offset**: Number of users to skip (default: 0)
    
    Returns paginated list of all users with total count
    
    Note: In production, this should be admin-only!
    """
    return await auth_service.get_all_users(limit=limit, offset=offset)


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    **Get specific user by ID**
    
    Returns user information for the given user ID
    
    Note: In production, this should be admin-only or restricted!
    """
    return await auth_service.get_user_by_id(user_id)
