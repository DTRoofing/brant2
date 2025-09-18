from fastapi import APIRouter
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify API connectivity
    """
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "1.0.0",
            "services": {
                "api": "healthy"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "1.0.0",
            "services": {
                "api": "unhealthy"
            },
            "error": str(e)
        }
