import pytest_asyncio
import pytest
import httpx
import tempfile
import uuid
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from app.main import app
from unittest.mock import MagicMock, patch

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
def empty_pdf(temp_dir):
    """Creates an empty PDF file for testing."""
    empty_path = temp_dir / "empty.pdf"
    # Create a minimal valid PDF with no content
    c = canvas.Canvas(str(empty_path), pagesize=letter)
    c.save()
    return empty_path

@pytest.fixture
def large_pdf(temp_dir):
    """Creates a large PDF file for performance testing."""
    large_path = temp_dir / "large.pdf"
    c = canvas.Canvas(str(large_path), pagesize=letter)
    
    # Create a large PDF with many pages
    for i in range(50):  # 50 pages
        c.drawString(72, 800, f"Page {i+1} - Large Roofing Blueprint")
        c.drawString(72, 780, f"Project: Large Commercial Building {i+1}")
        c.drawString(72, 760, f"Total Area: {10000 + i*100} sq ft")
        c.drawString(72, 740, f"Roof Pitch: {6 + (i % 12)}/12")
        c.drawString(72, 720, f"Material: {'TPO' if i % 2 == 0 else 'EPDM'}")
        c.drawString(72, 700, f"Contractor: ABC Roofing Company")
        c.drawString(72, 680, f"Date: 2024-01-{15 + (i % 15):02d}")
        c.drawString(72, 660, f"Permit Number: PER-2024-{1000 + i:04d}")
        c.drawString(72, 640, f"Estimated Cost: ${500000 + i*10000:,.2f}")
        c.drawString(72, 620, f"Timeline: {8 + (i % 4)} weeks")
        c.drawString(72, 600, f"Notes: This is a detailed blueprint for a large commercial roofing project.")
        
        # Add some technical details
        for j in range(20):
            c.drawString(72, 580 - j*20, f"Detail {j+1}: Technical specification for section {j+1}")
        
        c.showPage()
    
    c.save()
    return large_path

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

@pytest.fixture
def mock_redis(mocker):
    """Mock Redis connection for testing."""
    mock_redis = mocker.patch('redis.from_url')
    mock_redis.return_value.ping.return_value = True
    return mock_redis

@pytest.fixture
def mock_celery_app(mocker):
    """Mock Celery app for testing."""
    mock_app = mocker.patch('app.workers.celery_app.celery_app')
    mock_app.send_task.return_value = mocker.Mock(id='test-task-id')
    return mock_app

@pytest.fixture(autouse=True)
def mock_external_services():
    """Mock all external services for testing."""
    with patch('app.services.google_services.google_service') as mock_google, \
         patch('app.services.claude_service.claude_service') as mock_claude, \
         patch('redis.from_url') as mock_redis, \
         patch('app.workers.celery_app.celery_app') as mock_celery:
        
        # Configure mocks
        mock_google.initialize_clients.return_value = None
        mock_google.process_document.return_value = {
            "text": "Test document text",
            "entities": [],
            "tables": []
        }
        mock_google.analyze_image.return_value = {
            "labels": [{"description": "test", "score": 0.9}],
            "text": "Test image text",
            "confidence": 0.9
        }
        
        mock_claude.analyze_document.return_value = {
            "analysis": "Test analysis",
            "measurements": {"area": 1000, "pitch": 6},
            "confidence": 0.9
        }
        
        mock_redis_client = MagicMock()
        mock_redis_client.ping.return_value = True
        mock_redis.return_value = mock_redis_client
        
        mock_celery.send_task.return_value = MagicMock(id='test-task-id')
        
        yield {
            'google': mock_google,
            'claude': mock_claude,
            'redis': mock_redis_client,
            'celery': mock_celery
        }