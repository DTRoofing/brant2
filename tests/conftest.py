import pytest_asyncio
import pytest
import httpx
import tempfile
import uuid
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
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

@pytest.fixture
def sample_pdf_with_text():
    """Creates a sample PDF with text for testing."""
    temp_dir = Path(tempfile.gettempdir()) / "brant_tests"
    temp_dir.mkdir(exist_ok=True)
    
    pdf_path = temp_dir / f"test_doc_{uuid.uuid4()}.pdf"
    
    # Create a simple PDF with some text
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.drawString(72, 800, "Roofing Blueprint Test")
    c.drawString(72, 780, "Total Roof Area: 3500 sq ft")
    c.drawString(72, 760, "Roof Pitch: 6/12")
    c.drawString(72, 740, "Material: Asphalt Shingles")
    c.save()
    
    yield pdf_path
    
    # Cleanup
    try:
        pdf_path.unlink()
    except FileNotFoundError:
        pass

@pytest.fixture
def temp_dir():
    """Creates a temporary directory for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    
    # Cleanup
    import shutil
    try:
        shutil.rmtree(temp_dir)
    except FileNotFoundError:
        pass

@pytest.fixture
def corrupted_pdf(temp_dir):
    """Creates a corrupted PDF file for testing error handling."""
    corrupted_path = temp_dir / "corrupted.pdf"
    # Write invalid PDF content
    corrupted_path.write_bytes(b"This is not a valid PDF file!")
    return corrupted_path

@pytest.fixture
def test_client():
    """Provides a test client for API testing."""
    from fastapi.testclient import TestClient
    return TestClient(app)

@pytest.fixture
def async_db():
    """Mock async database session for testing."""
    from unittest.mock import AsyncMock
    mock_session = AsyncMock()
    mock_session.add = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.query.return_value.filter.return_value.first.return_value = None
    return mock_session