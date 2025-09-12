"""
Integration tests for PDF upload and processing workflow.
"""
import pytest
import uuid
import asyncio
from unittest.mock import patch, Mock, AsyncMock
from pathlib import Path
from fastapi import status
import io

from app.models.core import Document, ProcessingStatus, Measurement


class TestPDFUploadAPI:
    """Test cases for PDF upload API endpoints."""
    
    def test_upload_valid_pdf(self, test_client, sample_pdf_with_text):
        """Test uploading a valid PDF file."""
        with open(sample_pdf_with_text, "rb") as f:
            response = test_client.post(
                "/api/v1/documents/upload",
                files={"file": ("test.pdf", f, "application/pdf")}
            )
        
        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        
        assert "id" in data
        assert data["filename"] == "test.pdf"
        assert data["processing_status"] == "pending"
        assert data["file_size"] > 0
    
    def test_upload_non_pdf_file(self, test_client, temp_dir):
        """Test uploading a non-PDF file is rejected."""
        # Create a text file
        text_file = temp_dir / "test.txt"
        text_file.write_text("This is not a PDF")
        
        with open(text_file, "rb") as f:
            response = test_client.post(
                "/api/v1/documents/upload",
                files={"file": ("test.txt", f, "text/plain")}
            )
        
        assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        assert "Only PDF files are supported" in response.json()["detail"]
    
    def test_upload_missing_file(self, test_client):
        """Test upload request without file."""
        response = test_client.post("/api/v1/documents/upload")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_upload_empty_file(self, test_client, temp_dir):
        """Test uploading an empty PDF file."""
        empty_file = temp_dir / "empty.pdf"
        empty_file.touch()
        
        with open(empty_file, "rb") as f:
            response = test_client.post(
                "/api/v1/documents/upload",
                files={"file": ("empty.pdf", f, "application/pdf")}
            )
        
        # Should accept the file but processing might fail later
        assert response.status_code == status.HTTP_202_ACCEPTED
    
    @patch('app.api.v1.endpoints.uploads.settings')
    def test_upload_creates_upload_directory(self, mock_settings, test_client, sample_pdf_with_text, temp_dir):
        """Test that upload directory is created if it doesn't exist."""
        upload_dir = temp_dir / "uploads"
        mock_settings.UPLOAD_DIR = str(upload_dir)
        
        # Ensure directory doesn't exist initially
        assert not upload_dir.exists()
        
        with open(sample_pdf_with_text, "rb") as f:
            response = test_client.post(
                "/api/v1/documents/upload",
                files={"file": ("test.pdf", f, "application/pdf")}
            )
        
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert upload_dir.exists()
    
    def test_upload_generates_unique_filename(self, test_client, sample_pdf_with_text):
        """Test that uploaded files get unique filenames."""
        filenames = []
        
        for _ in range(3):
            with open(sample_pdf_with_text, "rb") as f:
                response = test_client.post(
                    "/api/v1/documents/upload",
                    files={"file": ("same_name.pdf", f, "application/pdf")}
                )
            
            assert response.status_code == status.HTTP_202_ACCEPTED
            data = response.json()
            # Extract filename from file_path
            file_path = Path(data["file_path"])
            filenames.append(file_path.name)
        
        # All filenames should be unique
        assert len(set(filenames)) == 3
        
        # All should be valid UUIDs with .pdf extension
        for filename in filenames:
            name_part = filename.replace(".pdf", "")
            uuid.UUID(name_part)  # Should not raise exception


class TestPDFDocumentRetrieval:
    """Test cases for document retrieval endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_document_details(self, test_client, async_db, sample_pdf_with_text):
        """Test retrieving document details."""
        # Create document record
        document = Document(
            id=uuid.uuid4(),
            filename="test.pdf",
            file_path=str(sample_pdf_with_text),
            file_size=1024,
            processing_status=ProcessingStatus.COMPLETED
        )
        async_db.add(document)
        await async_db.commit()
        await async_db.refresh(document)
        
        response = test_client.get(f"/api/v1/documents/{document.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == str(document.id)
        assert data["filename"] == "test.pdf"
        assert data["processing_status"] == "completed"
        assert data["file_size"] == 1024
    
    def test_get_document_not_found(self, test_client):
        """Test retrieving non-existent document."""
        fake_id = uuid.uuid4()
        response = test_client.get(f"/api/v1/documents/{fake_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Document not found" in response.json()["detail"]
    
    def test_get_document_invalid_uuid(self, test_client):
        """Test retrieving document with invalid UUID."""
        response = test_client.get("/api/v1/documents/invalid-uuid")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestPDFProcessingWorkflow:
    """Test cases for the complete PDF processing workflow."""
    
    @pytest.mark.asyncio
    @patch('app.workers.tasks.pdf_processing.process_pdf_document.delay')
    async def test_upload_triggers_processing(self, mock_celery_task, test_client, async_db, sample_pdf_with_text):
        """Test that uploading a document triggers background processing."""
        with open(sample_pdf_with_text, "rb") as f:
            response = test_client.post(
                "/api/v1/documents/upload",
                files={"file": ("test.pdf", f, "application/pdf")}
            )
        
        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        document_id = data["id"]
        
        # Verify Celery task was called
        mock_celery_task.assert_called_once_with(document_id=document_id)
    
    @pytest.mark.asyncio
    async def test_processing_status_progression(self, async_db, sample_pdf_with_text):
        """Test that document status progresses correctly during processing."""
        from app.core.pdf_processing import async_process_pdf_document
        
        # Create document record
        document = Document(
            id=uuid.uuid4(),
            filename="test.pdf",
            file_path=str(sample_pdf_with_text),
            file_size=1024,
            processing_status=ProcessingStatus.PENDING
        )
        async_db.add(document)
        await async_db.commit()
        await async_db.refresh(document)
        
        # Verify initial status
        assert document.processing_status == ProcessingStatus.PENDING
        
        # Process document
        result = await async_process_pdf_document(str(document.id))
        
        # Verify final status
        await async_db.refresh(document)
        assert document.processing_status == ProcessingStatus.COMPLETED
        assert document.processing_error is None
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_processing_failure_updates_status(self, async_db, temp_dir):
        """Test that processing failures update document status correctly."""
        from app.core.pdf_processing import async_process_pdf_document
        
        # Create document with non-existent file
        document = Document(
            id=uuid.uuid4(),
            filename="missing.pdf",
            file_path=str(temp_dir / "nonexistent.pdf"),
            file_size=1024,
            processing_status=ProcessingStatus.PENDING
        )
        async_db.add(document)
        await async_db.commit()
        await async_db.refresh(document)
        
        # Process document (should fail)
        result = await async_process_pdf_document(str(document.id))
        
        # Verify error status
        await async_db.refresh(document)
        assert document.processing_status == ProcessingStatus.FAILED
        assert document.processing_error is not None
        assert result["status"] == "error"
    
    @pytest.mark.asyncio
    @patch('app.workers.tasks.pdf_processing.google_service')
    async def test_workflow_with_google_ai_success(self, mock_google_service, async_db, sample_pdf_with_text):
        """Test processing workflow with successful Google AI integration."""
        from app.workers.tasks.pdf_processing import process_pdf_document
        
        # Mock Google service responses
        mock_google_service.upload_to_gcs = AsyncMock(return_value="gs://bucket/file.pdf")
        mock_google_service.process_document_with_ai = AsyncMock(return_value={
            "text": "Extracted text from Google AI",
            "measurements": [
                {"text": "3500 sq ft", "confidence": 0.95},
                {"text": "2800 square feet", "confidence": 0.87}
            ]
        })
        
        # Create document record
        document = Document(
            id=uuid.uuid4(),
            filename="test.pdf",
            file_path=str(sample_pdf_with_text),
            file_size=1024,
            processing_status=ProcessingStatus.PENDING
        )
        async_db.add(document)
        await async_db.commit()
        await async_db.refresh(document)
        
        # Process document synchronously for testing
        with patch('app.core.config.settings') as mock_settings:
            mock_settings.GOOGLE_CLOUD_PROJECT_ID = "test-project"
            
            # Call the synchronous Celery task wrapper
            result = process_pdf_document(str(document.id))
        
        assert result["status"] == "completed"
        assert result["analysis_performed"] is True
        
        # Verify measurements were stored
        await async_db.refresh(document)
        assert document.processing_status == ProcessingStatus.COMPLETED
    
    @pytest.mark.asyncio
    @patch('app.workers.tasks.pdf_processing.claude_service')
    async def test_workflow_with_claude_analysis(self, mock_claude_service, async_db, sample_pdf_with_text):
        """Test processing workflow with Claude AI analysis."""
        from app.workers.tasks.pdf_processing import process_pdf_document
        
        # Mock Claude service response
        mock_claude_service.analyze_text_for_estimate.return_value = {
            "total_roof_area_sqft": 3500,
            "measurements": [
                {"value": "3500", "label": "roof_area"},
                {"value": "280", "label": "dormer_area"}
            ]
        }
        
        # Create document record
        document = Document(
            id=uuid.uuid4(),
            filename="test.pdf",
            file_path=str(sample_pdf_with_text),
            file_size=1024,
            processing_status=ProcessingStatus.PENDING
        )
        async_db.add(document)
        await async_db.commit()
        await async_db.refresh(document)
        
        # Process document
        with patch('app.core.config.settings') as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = "test-key"
            mock_settings.GOOGLE_CLOUD_PROJECT_ID = None  # Disable Google AI
            
            result = process_pdf_document(str(document.id))
        
        assert result["status"] == "completed"
        assert result["analysis_performed"] is True
        
        # Verify document status
        await async_db.refresh(document)
        assert document.processing_status == ProcessingStatus.COMPLETED


class TestPDFValidationAndSecurity:
    """Test cases for PDF validation and security measures."""
    
    def test_upload_validates_pdf_content_type(self, test_client, temp_dir):
        """Test that content type validation works correctly."""
        # Create a text file with PDF extension
        fake_pdf = temp_dir / "fake.pdf"
        fake_pdf.write_text("This is not a PDF")
        
        # Try to upload with correct PDF content type
        with open(fake_pdf, "rb") as f:
            response = test_client.post(
                "/api/v1/documents/upload",
                files={"file": ("fake.pdf", f, "application/pdf")}
            )
        
        # Should be accepted based on content type header
        assert response.status_code == status.HTTP_202_ACCEPTED
        
        # Try with incorrect content type
        with open(fake_pdf, "rb") as f:
            response = test_client.post(
                "/api/v1/documents/upload",
                files={"file": ("fake.pdf", f, "text/plain")}
            )
        
        assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    
    def test_upload_file_size_calculation(self, test_client, sample_pdf_with_text):
        """Test that file size is correctly calculated and stored."""
        actual_size = Path(sample_pdf_with_text).stat().st_size
        
        with open(sample_pdf_with_text, "rb") as f:
            response = test_client.post(
                "/api/v1/documents/upload",
                files={"file": ("test.pdf", f, "application/pdf")}
            )
        
        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        
        assert data["file_size"] == actual_size
    
    @patch('app.api.v1.endpoints.uploads.aiofiles.open')
    def test_upload_handles_file_write_errors(self, mock_aiofiles, test_client, sample_pdf_with_text):
        """Test handling of file system errors during upload."""
        # Mock file write to fail
        mock_file = AsyncMock()
        mock_file.__aenter__.return_value = mock_file
        mock_file.write.side_effect = OSError("Disk full")
        mock_aiofiles.return_value = mock_file
        
        with open(sample_pdf_with_text, "rb") as f:
            response = test_client.post(
                "/api/v1/documents/upload",
                files={"file": ("test.pdf", f, "application/pdf")}
            )
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "error uploading" in response.json()["detail"].lower()


class TestPDFProcessingConcurrency:
    """Test cases for concurrent PDF processing scenarios."""
    
    @pytest.mark.asyncio
    async def test_concurrent_document_processing(self, async_db, sample_pdf_with_text):
        """Test processing multiple documents concurrently."""
        from app.core.pdf_processing import async_process_pdf_document
        
        # Create multiple document records
        documents = []
        for i in range(3):
            document = Document(
                id=uuid.uuid4(),
                filename=f"test_{i}.pdf",
                file_path=str(sample_pdf_with_text),
                file_size=1024,
                processing_status=ProcessingStatus.PENDING
            )
            async_db.add(document)
            documents.append(document)
        
        await async_db.commit()
        for doc in documents:
            await async_db.refresh(doc)
        
        # Process all documents concurrently
        tasks = [
            async_process_pdf_document(str(doc.id))
            for doc in documents
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Verify all processed successfully
        for result in results:
            assert result["status"] == "success"
        
        # Verify all documents updated
        for doc in documents:
            await async_db.refresh(doc)
            assert doc.processing_status == ProcessingStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_processing_database_isolation(self, async_db, sample_pdf_with_text):
        """Test that concurrent processing maintains database isolation."""
        from app.core.pdf_processing import async_process_pdf_document
        
        # Create shared document
        document = Document(
            id=uuid.uuid4(),
            filename="shared.pdf",
            file_path=str(sample_pdf_with_text),
            file_size=1024,
            processing_status=ProcessingStatus.PENDING
        )
        async_db.add(document)
        await async_db.commit()
        await async_db.refresh(document)
        
        # Simulate race condition by processing same document twice
        task1 = async_process_pdf_document(str(document.id))
        task2 = async_process_pdf_document(str(document.id))
        
        results = await asyncio.gather(task1, task2, return_exceptions=True)
        
        # At least one should succeed
        success_count = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "success")
        assert success_count >= 1