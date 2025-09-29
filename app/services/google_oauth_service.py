"""
Google OAuth service for handling authentication flow.
"""
import secrets
from typing import Optional, Dict, Any
from urllib.parse import urlencode
from fastapi import HTTPException, status
import httpx
from authlib.integrations.base_client import OAuthError
from authlib.integrations.httpx_client import AsyncOAuth2Client

from app.core.config import settings
from app.models.core import User
from app.core.auth import auth_service
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class GoogleOAuthService:
    """Service for handling Google OAuth authentication."""

    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

    @staticmethod
    def get_oauth_client() -> AsyncOAuth2Client:
        """Create and return OAuth2 client for Google."""
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google OAuth not configured"
            )

        return AsyncOAuth2Client(
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            redirect_uri=settings.google_oauth_redirect_uri,
        )

    @staticmethod
    def get_authorization_url(state: Optional[str] = None) -> tuple[str, str]:
        """
        Generate Google OAuth authorization URL.

        Returns:
            Tuple of (authorization_url, state)
        """
        client = GoogleOAuthService.get_oauth_client()

        if not state:
            state = secrets.token_urlsafe(32)

        authorization_url, _ = client.create_authorization_url(
            GoogleOAuthService.GOOGLE_AUTH_URL,
            scope=["openid", "email", "profile"],
            state=state,
        )

        return authorization_url, state

    @staticmethod
    async def exchange_code_for_token(code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from Google

        Returns:
            Token response containing access_token, etc.
        """
        client = GoogleOAuthService.get_oauth_client()

        try:
            token = await client.fetch_token(
                GoogleOAuthService.GOOGLE_TOKEN_URL,
                code=code
            )
            return token
        except OAuthError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth token exchange failed: {str(e)}"
            )

    @staticmethod
    async def get_user_info(access_token: str) -> Dict[str, Any]:
        """
        Get user information from Google using access token.

        Args:
            access_token: OAuth access token

        Returns:
            User information from Google
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                GoogleOAuthService.GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to fetch user info from Google"
                )

            return response.json()

    @staticmethod
    async def get_or_create_user(db: AsyncSession, google_user_info: Dict[str, Any]) -> User:
        """
        Get existing user or create new user from Google OAuth info.

        Args:
            db: Database session
            google_user_info: User info from Google

        Returns:
            User instance
        """
        google_id = google_user_info.get("id")
        email = google_user_info.get("email")
        name = google_user_info.get("name", "")

        if not google_id or not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user info from Google"
            )

        # Check if user already exists by google_id
        result = await db.execute(select(User).where(User.google_id == google_id))
        user = result.scalar_one_or_none()

        if user:
            # Update user info if needed
            if not user.is_active:
                user.is_active = True
            await db.commit()
            await db.refresh(user)
            return user

        # Check if user exists by email (might have been created with password auth)
        result = await db.execute(select(User).where(User.email == email))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            # Link Google account to existing user
            if existing_user.google_id and existing_user.google_id != google_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already linked to different Google account"
                )
            existing_user.google_id = google_id
            await db.commit()
            await db.refresh(existing_user)
            return existing_user

        # Create new user
        # Generate username from email if name is not available
        username = name.replace(" ", "").lower() if name else email.split("@")[0]

        # Ensure username is unique
        base_username = username
        counter = 1
        while True:
            result = await db.execute(select(User).where(User.username == username))
            if not result.scalar_one_or_none():
                break
            username = f"{base_username}{counter}"
            counter += 1

        new_user = User(
            email=email,
            username=username,
            google_id=google_id,
            is_active=True,
            hashed_password=None  # OAuth users don't have passwords
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return new_user

    @staticmethod
    async def authenticate_with_google(db: AsyncSession, code: str) -> Dict[str, Any]:
        """
        Complete OAuth flow and return authentication tokens.

        Args:
            db: Database session
            code: Authorization code from Google

        Returns:
            Token response with access_token, refresh_token, etc.
        """
        # Exchange code for token
        token_data = await GoogleOAuthService.exchange_code_for_token(code)

        # Get user info
        user_info = await GoogleOAuthService.get_user_info(token_data["access_token"])

        # Get or create user
        user = await GoogleOAuthService.get_or_create_user(db, user_info)

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is inactive"
            )

        # Create JWT tokens
        access_token = auth_service.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        refresh_token = auth_service.create_refresh_token(
            data={"sub": str(user.id), "email": user.email}
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 30 * 60,  # 30 minutes
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser
            }
        }


# Create singleton instance
google_oauth_service = GoogleOAuthService()
