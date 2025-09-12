from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check():
    """
    Checks if the service is running.
    """
    return {"status": "healthy", "service": "brant-roofing-api"}