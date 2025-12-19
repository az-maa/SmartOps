from fastapi import Depends, Header
from typing import Optional
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedException
from app.database.supabase import get_supabase
from supabase import Client


async def get_current_user_id(
    authorization: Optional[str] = Header(None),
    supabase: Client = Depends(get_supabase)
) -> str:
    """
    Extract and verify JWT token from Authorization header.
    Returns user_id if valid, raises exception otherwise.
    """
    if not authorization:
        raise UnauthorizedException(detail="Authorization header missing")
    
    # Expected format: "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedException(detail="Invalid authorization header format")
    
    token = parts[1]
    
    # Decode token
    payload = decode_access_token(token)
    if not payload:
        raise UnauthorizedException(detail="Invalid or expired token")
    
    user_id: str = payload.get("sub")
    if not user_id:
        raise UnauthorizedException(detail="Invalid token payload")
    
    return user_id


async def get_optional_user_id(
    authorization: Optional[str] = Header(None)
) -> Optional[str]:
    """
    Optional authentication - returns user_id if token present and valid,
    None otherwise (doesn't raise exception)
    """
    if not authorization:
        return None
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    
    token = parts[1]
    payload = decode_access_token(token)
    
    if not payload:
        return None
    
    return payload.get("sub")