"""
API dependencies for authentication and authorization.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.core import User
from app.core.auth import auth_service

# Security scheme for JWT tokens
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Get the current user from the database based on the JWT token.
    Returns None if no valid token is provided (for optional authentication).
    """
    if not credentials:
        return None
    
    try:
        # Verify and decode the JWT token
        payload = auth_service.verify_token(credentials.credentials)
        
        # Extract user ID from token
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        # Get user from database
        user = await auth_service.get_user_by_id(db, user_id)
        return user
        
    except HTTPException:
        # Re-raise HTTP exceptions (like expired token)
        raise
    except Exception:
        # For any other error, return None (unauthenticated)
        return None


async def get_current_active_user(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    """
    Get the current active user, raising an exception if not authenticated.
    This is used for endpoints that require authentication.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get the current superuser, raising an exception if not a superuser.
    This is used for admin-only endpoints.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser privileges required"
        )
    
    return current_user
