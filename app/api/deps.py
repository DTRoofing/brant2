"""
API dependencies for authentication and authorization.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.core import User

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
    
    # For now, we'll create a simple mock user for testing
    # In a real implementation, you would:
    # 1. Decode and validate the JWT token
    # 2. Extract user information from the token
    # 3. Query the database for the user
    
    # Mock implementation - create a default user for testing
    # This should be replaced with proper JWT validation
    try:
        # Try to get the first user from the database
        result = await db.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        
        if not user:
            # Create a default user for testing if none exists
            user = User(
                email="test@example.com",
                username="testuser",
                hashed_password="hashed_password_placeholder",
                is_active=True
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
        return user
    except Exception as e:
        # If there's any error, return None (unauthenticated)
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
