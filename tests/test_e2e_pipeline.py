import time
import uuid
from pathlib import Path

import httpx
import pytest
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

API_BASE_URL = "http://localhost:3001/api/v1"


@pytest.fixture(scope="module")
def sample_pdf_path() -> Path:
    """
    Creates a simple, temporary PDF file for testing and returns its path.
    The file is cleaned up after the test module finishes.
    """
    test_dir = Path("tests/temp")
    test_dir.mkdir(exist_ok=True)
    pdf_path = test_dir / f"test_doc_{uuid.uuid4()}.pdf"

    # Create a simple PDF with some text
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.drawString(72, 800, "Roofing Blueprint Test")
    c.drawString(72, 780, "Total Roof Area: 3500 sq ft")
    c.drawString(72, 760, "Roof Pitch: 6/12")
    c.drawString(72, 740, "Material: Asphalt Shingles")
    c.save()

    yield pdf_path

    # Cleanup
    pdf_path.unlink()


@pytest.mark.e2e
def test_full_document_processing_pipeline(sample_pdf_path: Path):
    """
    Tests the entire document processing pipeline from upload to result retrieval.
    This is an end-to-end test that requires the full application stack to be running.
    """
    document_id = None

    with httpx.Client(base_url=API_BASE_URL, timeout=30.0) as client:
        # 1. Upload the document
        print(f"\nUploading test file: {sample_pdf_path.name}")
        with open(sample_pdf_path, "rb") as f:
            response = client.post("/documents/upload", files={"file": (sample_pdf_path.name, f, "application/pdf")})

        assert response.status_code == 202, f"Upload failed: {response.text}"
        upload_data = response.json()
        document_id = upload_data.get("id")
        assert document_id is not None
        print(f"Document uploaded successfully. ID: {document_id}")

        # 2. Poll for status until completion or timeout
        max_wait_time = 300  # 5 minutes
        start_time = time.time()
        final_status = None

        while time.time() - start_time < max_wait_time:
            print("Checking status...")
            response = client.get(f"/documents/{document_id}/status")
            assert response.status_code == 200, f"Status check failed: {response.text}"
            status_data = response.json()
            current_status = status_data.get("document", {}).get("status")
            print(f"Current status: {current_status}")

            if current_status == "SUCCESS":
                final_status = "SUCCESS"
                break
            elif current_status == "FAILURE":
                pytest.fail(f"Processing failed with details: {status_data}")

            time.sleep(20)

        assert final_status == "SUCCESS", f"Processing timed out after {max_wait_time} seconds."

        # 3. Retrieve and verify the final measurements
        print("Retrieving final measurements...")
        response = client.get(f"/documents/{document_id}/measurements")
        assert response.status_code == 200, f"Failed to get measurements: {response.text}"
        measurements = response.json()
        assert isinstance(measurements, dict)
        assert "total_roof_area_sqft" in measurements
        print(f"Test successful! Retrieved measurements: {measurements}")