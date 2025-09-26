"""
Legacy dependencies file - use app.api.deps instead.
This file is kept for backward compatibility.
"""
from app.api.deps import get_db, get_current_user, get_current_active_user, get_current_superuser

__all__ = ["get_db", "get_current_user", "get_current_active_user", "get_current_superuser"]