import pytest_asyncio
import pytest
import httpx
from app.main import app
from unittest.mock import MagicMock

class MockProcessingError(Exception):
    pass

@pytest.fixture
def mock_claude_service(mocker):
    """
    A refined mock factory for the Claude service.
    Allows tests to configure success and failure scenarios.
    """
    mock_service = MagicMock()
    mocker.patch("app.services.claude_service.ClaudeService", return_value=mock_service)
    return mock_service

@pytest.fixture
def mock_document_ai_service(mocker) -> MagicMock:
    """Mocks the Google Document AI service."""
    mock_service = MagicMock()
    mocker.patch("app.services.google_services.DocumentAIService", return_value=mock_service)
    return mock_service

@pytest.fixture
def mock_vision_service(mocker) -> MagicMock:
    """Mocks the Google Vision AI service."""
    mock_service = MagicMock()
    mocker.patch("app.services.google_services.GoogleVisionService", return_value=mock_service)
    return mock_service

@pytest_asyncio.fixture
async def async_client() -> httpx.AsyncClient:
    """Provides an async client for making API requests to the app."""
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client