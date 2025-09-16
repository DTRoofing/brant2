"""
Pytest configuration and shared fixtures for PDF pipeline testing.
"""
import tempfile
import uuid
import asyncio
from pathlib import Path
from typing import Generator, AsyncGenerator
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
import io

from app.main import app
from app.core.database import get_db
from app.models.base import Base
from app.models.core import Document, ProcessingStatus
from app.core.config import settings


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_engine():
    """Create async database engine for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest_asyncio.fixture
async def async_db(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create async database session for testing."""
    async_session = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
def test_client(async_db):
    """Create FastAPI test client with dependency overrides."""
    def override_get_db():
        yield async_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_pdf_with_text(temp_dir) -> Path:
    """Create a PDF with extractable text for testing."""
    pdf_path = temp_dir / f"text_sample_{uuid.uuid4()}.pdf"
    
    # Create PDF with text content
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.setFont("Helvetica", 12)
    
    # Add roofing-related content
    c.drawString(72, 800, "ROOFING ESTIMATE BLUEPRINT")
    c.drawString(72, 780, "===============================")
    c.drawString(72, 760, "Property Address: 123 Main St, Anytown, ST 12345")
    c.drawString(72, 740, "Total Roof Area: 3,500 sq ft")
    c.drawString(72, 720, "Roof Pitch: 8/12")
    c.drawString(72, 700, "Primary Material: Asphalt Shingles")
    c.drawString(72, 680, "Ridge Length: 120 linear feet")
    c.drawString(72, 660, "Gutter Length: 180 linear feet")
    c.drawString(72, 640, "Estimated Labor: $8,500")
    c.drawString(72, 620, "Material Cost: $4,200")
    c.drawString(72, 600, "Total Estimate: $12,700")
    
    c.showPage()  # New page
    c.drawString(72, 800, "ADDITIONAL MEASUREMENTS")
    c.drawString(72, 780, "========================")
    c.drawString(72, 760, "Dormer Area: 280 sq ft")
    c.drawString(72, 740, "Chimney Flashing: 45 linear feet")
    c.drawString(72, 720, "Skylight Area: 16 sq ft")
    
    c.save()
    return pdf_path


@pytest.fixture
def sample_pdf_image_only(temp_dir) -> Path:
    """Create a PDF that requires OCR for text extraction."""
    pdf_path = temp_dir / f"image_sample_{uuid.uuid4()}.pdf"
    
    # Create an image with text
    img = Image.new('RGB', (800, 600), color='white')
    # Note: In a real scenario, we'd add text to the image using PIL's ImageDraw
    # For testing purposes, this creates a PDF that PyPDF2 can't extract text from
    
    # Save as image first, then convert to PDF
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    # Create PDF with image
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    # This creates a PDF without extractable text, forcing OCR usage
    c.save()
    
    return pdf_path


@pytest.fixture
def corrupted_pdf(temp_dir) -> Path:
    """Create a corrupted PDF file for error testing."""
    pdf_path = temp_dir / f"corrupted_{uuid.uuid4()}.pdf"
    
    # Create a file with PDF header but invalid content
    with open(pdf_path, 'wb') as f:
        f.write(b'%PDF-1.4\n')
        f.write(b'This is not valid PDF content\n')
        f.write(b'%%EOF\n')
    
    return pdf_path


@pytest.fixture
def large_pdf(temp_dir) -> Path:
    """Create a large PDF file for performance testing."""
    pdf_path = temp_dir / f"large_sample_{uuid.uuid4()}.pdf"
    
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.setFont("Helvetica", 10)
    
    # Create 50 pages with content
    for page_num in range(50):
        c.drawString(72, 800, f"Page {page_num + 1} of 50")
        c.drawString(72, 780, "=" * 50)
        
        # Add multiple lines of content per page
        y_position = 760
        for line_num in range(25):
            c.drawString(72, y_position, f"Line {line_num + 1}: Roofing measurement data - {1000 + line_num * 10} sq ft")
            y_position -= 20
            
            if y_position < 100:  # Near bottom of page
                break
        
        c.showPage()
    
    c.save()
    return pdf_path


@pytest.fixture
def oversized_pdf(temp_dir) -> Path:
    """Create a PDF that exceeds typical size limits."""
    pdf_path = temp_dir / f"oversized_{uuid.uuid4()}.pdf"
    
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.setFont("Helvetica", 8)
    
    # Create 200 pages to make it oversized
    for page_num in range(200):
        c.drawString(72, 800, f"Oversized PDF Page {page_num + 1}")
        
        # Fill page with text
        y_position = 780
        for line in range(35):
            text = f"Line {line}: " + "Sample text content " * 10
            c.drawString(72, y_position, text[:100])  # Truncate to fit
            y_position -= 20
        
        c.showPage()
    
    c.save()
    return pdf_path


@pytest.fixture
def empty_pdf(temp_dir) -> Path:
    """Create an empty PDF file."""
    pdf_path = temp_dir / f"empty_{uuid.uuid4()}.pdf"
    
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.save()  # Save without adding any content
    
    return pdf_path


@pytest.fixture
def sample_document_record(async_db) -> Document:
    """Create a sample document database record."""
    document = Document(
        id=uuid.uuid4(),
        filename="test_document.pdf",
        file_path="/tmp/test_document.pdf",
        file_size=1024,
        processing_status=ProcessingStatus.PENDING
    )
    async_db.add(document)
    return document


@pytest.fixture
def mock_google_credentials():
    """Mock Google Cloud credentials for testing."""
    return {
        "type": "service_account",
        "project_id": "test-project",
        "private_key_id": "test-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMOCK_PRIVATE_KEY\n-----END PRIVATE KEY-----\n",
        "client_email": "test@test-project.iam.gserviceaccount.com",
        "client_id": "123456789",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token"
    }