"""
Comprehensive error handling tests for PDF processing pipeline.
"""
import pytest
import uuid
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock, AsyncMock
import io

from app.core.pdf_processing import extract_text_from_pdf, async_process_pdf_document
from app.models.core import Document, ProcessingStatus
from app.services.google_services import GoogleCloudService


class TestPDFExtractionErrorHandling:
    """Test error handling in PDF text extraction."""
    
    def test_extract_text_file_not_found(self):
        """Test handling of non-existent PDF files."""
        with pytest.raises(FileNotFoundError):
            extract_text_from_pdf("/nonexistent/path/file.pdf")
    
    def test_extract_text_invalid_path(self):
        """Test handling of invalid file paths."""
        invalid_paths = [
            "",  # Empty path
            "/",  # Root directory
            "con",  # Windows reserved name
            "\x00invalid",  # Null character
        ]
        
        for invalid_path in invalid_paths:
            with pytest.raises((FileNotFoundError, PermissionError, OSError, ValueError)):
                extract_text_from_pdf(invalid_path)
    
    def test_extract_text_directory_instead_of_file(self, temp_dir):
        """Test handling when a directory path is provided instead of file."""
        with pytest.raises((IsADirectoryError, PermissionError)):
            extract_text_from_pdf(str(temp_dir))
    
    def test_extract_text_permission_denied(self):
        """Test handling of permission denied errors."""
        if Path("/etc/shadow").exists():  # Unix-like system
            with pytest.raises(PermissionError):
                extract_text_from_pdf("/etc/shadow")
    
    def test_extract_text_corrupted_pdf(self, corrupted_pdf):
        """Test handling of corrupted PDF files."""
        with pytest.raises(Exception):  # Should raise some kind of PDF parsing error
            extract_text_from_pdf(str(corrupted_pdf))
    
    def test_extract_text_invalid_pdf_content(self, temp_dir):
        """Test handling of files with PDF extension but invalid content."""
        fake_pdf = temp_dir / "fake.pdf"
        fake_pdf.write_bytes(b"This is not a PDF file at all!")
        
        with pytest.raises(Exception):  # Should fail to parse
            extract_text_from_pdf(str(fake_pdf))
    
    def test_extract_text_empty_file(self, temp_dir):
        """Test handling of completely empty files."""
        empty_file = temp_dir / "empty.pdf"
        empty_file.touch()  # Create empty file
        
        with pytest.raises(Exception):  # Should fail to parse empty file
            extract_text_from_pdf(str(empty_file))
    
    @patch('app.core.pdf_processing.PyPDF2.PdfReader')
    def test_extract_text_pypdf2_error(self, mock_pdf_reader, sample_pdf_with_text):
        """Test handling of PyPDF2 parsing errors."""
        mock_pdf_reader.side_effect = Exception("PyPDF2 parsing failed")
        
        with pytest.raises(Exception):
            extract_text_from_pdf(str(sample_pdf_with_text))
    
    @patch('app.core.pdf_processing.PyPDF2.PdfReader')
    @patch('app.core.pdf_processing.convert_from_path')
    def test_extract_text_both_extraction_methods_fail(self, mock_convert, mock_pdf_reader, sample_pdf_with_text):
        """Test handling when both PyPDF2 and OCR fail."""
        # Mock PyPDF2 to return empty text
        mock_reader = Mock()
        mock_reader.pages = []
        mock_pdf_reader.return_value = mock_reader
        
        # Mock OCR to fail
        mock_convert.side_effect = Exception("OCR conversion failed")
        
        # Should not raise exception but return empty text
        result = extract_text_from_pdf(str(sample_pdf_with_text))
        assert isinstance(result, str)
        assert len(result.strip()) == 0
    
    @patch('app.core.pdf_processing.pytesseract.image_to_string')
    @patch('app.core.pdf_processing.convert_from_path')
    @patch('app.core.pdf_processing.PyPDF2.PdfReader')
    def test_extract_text_ocr_specific_errors(self, mock_pdf_reader, mock_convert, mock_tesseract, sample_pdf_with_text):
        """Test handling of specific OCR errors."""
        # Mock PyPDF2 to return minimal text
        mock_reader = Mock()
        mock_reader.pages = []
        mock_pdf_reader.return_value = mock_reader
        
        # Mock image conversion success but OCR failure
        mock_image = Mock()
        mock_convert.return_value = [mock_image]
        mock_tesseract.side_effect = Exception("Tesseract not found")
        
        result = extract_text_from_pdf(str(sample_pdf_with_text))
        assert isinstance(result, str)


class TestAsyncProcessingErrorHandling:
    """Test error handling in async PDF processing."""
    
    @pytest.mark.asyncio
    async def test_async_process_invalid_document_id(self):
        """Test processing with invalid document ID format."""
        invalid_ids = [
            "not-a-uuid",
            "",
            "12345",
            None
        ]
        
        for invalid_id in invalid_ids:
            with pytest.raises((ValueError, TypeError)):
                await async_process_pdf_document(str(invalid_id) if invalid_id else invalid_id)
    
    @pytest.mark.asyncio
    async def test_async_process_nonexistent_document(self):
        """Test processing with non-existent document ID."""
        fake_id = str(uuid.uuid4())
        
        result = await async_process_pdf_document(fake_id)
        
        assert result["status"] == "error"
        assert "Document not found" in result["detail"]
    
    @pytest.mark.asyncio
    async def test_async_process_missing_file(self, async_db):
        """Test processing when PDF file is missing from disk."""
        # Create document record with non-existent file
        document = Document(
            id=uuid.uuid4(),
            filename="missing.pdf",
            file_path="/path/to/missing/file.pdf",
            file_size=1024,
            processing_status=ProcessingStatus.PENDING
        )
        async_db.add(document)
        await async_db.commit()
        await async_db.refresh(document)
        
        result = await async_process_pdf_document(str(document.id))
        
        assert result["status"] == "error"
        assert "not found" in result["error"].lower()
        
        # Verify document status updated
        await async_db.refresh(document)
        assert document.processing_status == ProcessingStatus.FAILED
        assert document.processing_error is not None
    
    @pytest.mark.asyncio
    @patch('app.core.pdf_processing.extract_text_from_pdf')
    async def test_async_process_extraction_failure(self, mock_extract, async_db, sample_pdf_with_text):
        """Test handling of text extraction failures during async processing."""
        mock_extract.side_effect = Exception("Text extraction failed")
        
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
        
        result = await async_process_pdf_document(str(document.id))
        
        assert result["status"] == "error"
        assert "Text extraction failed" in result["error"]
        
        # Verify document status updated
        await async_db.refresh(document)
        assert document.processing_status == ProcessingStatus.FAILED
        assert "Text extraction failed" in document.processing_error
    
    @pytest.mark.asyncio
    async def test_async_process_database_connection_failure(self, sample_pdf_with_text):
        """Test handling of database connection failures."""
        # Test with invalid document ID that would cause DB lookup to fail
        with patch('app.core.pdf_processing.AsyncSessionFactory') as mock_session_factory:
            mock_session_factory.side_effect = Exception("Database connection failed")
            
            with pytest.raises(Exception):
                await async_process_pdf_document(str(uuid.uuid4()))


class TestPDFUploadErrorHandling:
    """Test error handling in PDF upload endpoints."""
    
    def test_upload_missing_file_parameter(self, test_client):
        """Test upload without file parameter."""
        response = test_client.post("/api/v1/documents/upload")
        
        assert response.status_code == 422  # Unprocessable Entity
        error_detail = response.json()
        assert "field required" in str(error_detail).lower()
    
    def test_upload_invalid_content_type(self, test_client, temp_dir):
        """Test upload with invalid content type."""
        text_file = temp_dir / "test.txt"
        text_file.write_text("Not a PDF")
        
        with open(text_file, "rb") as f:
            response = test_client.post(
                "/api/v1/documents/upload",
                files={"file": ("test.txt", f, "text/plain")}
            )
        
        assert response.status_code == 415  # Unsupported Media Type
        assert "Only PDF files are supported" in response.json()["detail"]
    
    def test_upload_malformed_content_type(self, test_client, sample_pdf_with_text):
        """Test upload with malformed content type header."""
        with open(sample_pdf_with_text, "rb") as f:
            response = test_client.post(
                "/api/v1/documents/upload",
                files={"file": ("test.pdf", f, "application/invalid")}
            )
        
        assert response.status_code == 415
    
    @patch('app.api.v1.endpoints.uploads.aiofiles.open')
    async def test_upload_disk_write_failure(self, mock_aiofiles, test_client, sample_pdf_with_text):
        """Test handling of disk write failures during upload."""
        # Mock aiofiles to raise an error
        mock_file = AsyncMock()
        mock_file.__aenter__.return_value = mock_file
        mock_file.write.side_effect = OSError("No space left on device")
        mock_aiofiles.return_value = mock_file
        
        with open(sample_pdf_with_text, "rb") as f:
            response = test_client.post(
                "/api/v1/documents/upload",
                files={"file": ("test.pdf", f, "application/pdf")}
            )
        
        assert response.status_code == 500  # Internal Server Error
        assert "error uploading" in response.json()["detail"].lower()
    
    @patch('app.api.v1.endpoints.uploads.Path.stat')
    async def test_upload_file_stat_failure(self, mock_stat, test_client, sample_pdf_with_text):
        """Test handling of file stat failures during upload."""
        mock_stat.side_effect = OSError("Cannot stat file")
        
        with open(sample_pdf_with_text, "rb") as f:
            response = test_client.post(
                "/api/v1/documents/upload",
                files={"file": ("test.pdf", f, "application/pdf")}
            )
        
        assert response.status_code == 500


class TestGoogleServicesErrorHandling:
    """Test error handling in Google Cloud services integration."""
    
    @pytest.mark.asyncio
    async def test_upload_to_gcs_client_not_configured(self):
        """Test GCS upload when client is not configured."""
        service = GoogleCloudService()
        service._storage_client = None
        
        result = await service.upload_to_gcs("test.pdf", "dest.pdf")
        
        assert result == ""
    
    @pytest.mark.asyncio
    async def test_upload_to_gcs_bucket_not_configured(self):
        """Test GCS upload when bucket is not configured."""
        service = GoogleCloudService()
        service._storage_client = Mock()
        service.bucket_name = None
        
        result = await service.upload_to_gcs("test.pdf", "dest.pdf")
        
        assert result == ""
    
    @pytest.mark.asyncio
    async def test_upload_to_gcs_network_failure(self, sample_pdf_with_text):
        """Test GCS upload with network failure."""
        mock_storage_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        mock_storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.upload_from_filename.side_effect = Exception("Network timeout")
        
        service = GoogleCloudService()
        service._storage_client = mock_storage_client
        service.bucket_name = "test-bucket"
        
        result = await service.upload_to_gcs(str(sample_pdf_with_text), "test.pdf")
        
        assert result == ""
    
    @pytest.mark.asyncio
    async def test_document_ai_processing_client_not_configured(self, sample_pdf_with_text):
        """Test Document AI processing when client is not configured."""
        service = GoogleCloudService()
        service._document_ai_client = None
        
        result = await service.process_document_with_ai(str(sample_pdf_with_text))
        
        assert result == {}
    
    @pytest.mark.asyncio
    async def test_document_ai_processing_missing_config(self, sample_pdf_with_text):
        """Test Document AI processing with missing configuration."""
        service = GoogleCloudService()
        service._document_ai_client = Mock()
        service.project_id = None  # Missing project ID
        
        result = await service.process_document_with_ai(str(sample_pdf_with_text))
        
        assert result == {}
    
    @pytest.mark.asyncio
    async def test_document_ai_api_failure(self, sample_pdf_with_text):
        """Test Document AI processing with API failure."""
        mock_client = Mock()
        mock_client.process_document.side_effect = Exception("API quota exceeded")
        
        service = GoogleCloudService()
        service._document_ai_client = mock_client
        service.project_id = "test-project"
        service.processor_id = "processor-id"
        service.location = "us"
        
        result = await service.process_document_with_ai(str(sample_pdf_with_text))
        
        assert result == {}
    
    @pytest.mark.asyncio
    async def test_vision_api_client_not_configured(self, sample_pdf_with_text):
        """Test Vision API when client is not configured."""
        service = GoogleCloudService()
        service._vision_client = None
        
        result = await service.analyze_image_with_vision(str(sample_pdf_with_text))
        
        assert result == {}
    
    @pytest.mark.asyncio
    async def test_vision_api_file_not_found(self):
        """Test Vision API with non-existent file."""
        mock_client = Mock()
        
        service = GoogleCloudService()
        service._vision_client = mock_client
        
        with pytest.raises(FileNotFoundError):
            await service.analyze_image_with_vision("/nonexistent/file.jpg")
    
    @pytest.mark.asyncio
    async def test_vision_api_processing_failure(self, sample_pdf_with_text):
        """Test Vision API processing failure."""
        mock_client = Mock()
        mock_client.text_detection.side_effect = Exception("Vision API error")
        
        service = GoogleCloudService()
        service._vision_client = mock_client
        
        result = await service.analyze_image_with_vision(str(sample_pdf_with_text))
        
        assert result == {}


class TestCeleryTaskErrorHandling:
    """Test error handling in Celery task processing."""
    
    @patch('app.workers.tasks.pdf_processing.SessionLocal')
    def test_celery_task_database_connection_failure(self, mock_session_local):
        """Test Celery task handling of database connection failures."""
        from app.workers.tasks.pdf_processing import process_pdf_document
        
        mock_session_local.side_effect = Exception("Database connection failed")
        
        # Task should handle the exception and not crash
        result = process_pdf_document(str(uuid.uuid4()))
        
        # Should indicate failure
        assert isinstance(result, dict) or result is None
    
    @patch('app.workers.tasks.pdf_processing.SessionLocal')
    def test_celery_task_document_not_found(self, mock_session_local):
        """Test Celery task with non-existent document."""
        from app.workers.tasks.pdf_processing import process_pdf_document
        
        mock_session = Mock()
        mock_session.__enter__.return_value = mock_session
        mock_session.__exit__.return_value = None
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_session_local.return_value = mock_session
        
        result = process_pdf_document(str(uuid.uuid4()))
        
        # Should handle gracefully
        assert isinstance(result, dict) or result is None
    
    def test_celery_task_invalid_document_id_format(self):
        """Test Celery task with invalid document ID format."""
        from app.workers.tasks.pdf_processing import process_pdf_document
        
        # Should handle invalid UUID format
        result = process_pdf_document("invalid-uuid-format")
        
        # Should not crash
        assert isinstance(result, dict) or result is None


class TestEdgeCaseErrorHandling:
    """Test handling of various edge cases and boundary conditions."""
    
    def test_extract_text_symbolic_links(self, temp_dir, sample_pdf_with_text):
        """Test handling of symbolic links."""
        if hasattr(Path, 'symlink_to'):  # Unix-like systems
            link_path = temp_dir / "link.pdf"
            try:
                link_path.symlink_to(sample_pdf_with_text)
                
                # Should handle symbolic links properly
                extracted_text = extract_text_from_pdf(str(link_path))
                assert len(extracted_text) > 0
            except OSError:
                # Symlink creation might fail on some systems
                pytest.skip("Cannot create symbolic links on this system")
    
    def test_extract_text_very_long_path(self, temp_dir):
        """Test handling of very long file paths."""
        # Create nested directory structure
        long_path = temp_dir
        for i in range(20):  # Create deep nesting
            long_path = long_path / f"very_long_directory_name_{i}"
        
        try:
            long_path.mkdir(parents=True, exist_ok=True)
            pdf_path = long_path / "test.pdf"
            
            # Try to create a file with very long path
            with pytest.raises((OSError, FileNotFoundError)):
                extract_text_from_pdf(str(pdf_path))
        except OSError:
            # Path too long for filesystem
            pytest.skip("Filesystem doesn't support such long paths")
    
    def test_extract_text_unicode_filename(self, temp_dir, sample_pdf_with_text):
        """Test handling of filenames with Unicode characters."""
        unicode_name = temp_dir / "测试文档.pdf"
        
        try:
            # Copy the sample PDF to Unicode filename
            unicode_name.write_bytes(sample_pdf_with_text.read_bytes())
            
            extracted_text = extract_text_from_pdf(str(unicode_name))
            assert len(extracted_text) > 0
        except (UnicodeError, OSError):
            pytest.skip("Filesystem doesn't support Unicode filenames")
    
    def test_extract_text_special_characters_in_path(self, temp_dir, sample_pdf_with_text):
        """Test handling of special characters in file paths."""
        special_names = [
            "file with spaces.pdf",
            "file-with-dashes.pdf",
            "file_with_underscores.pdf",
            "file.with.dots.pdf",
        ]
        
        for name in special_names:
            special_path = temp_dir / name
            try:
                special_path.write_bytes(sample_pdf_with_text.read_bytes())
                
                extracted_text = extract_text_from_pdf(str(special_path))
                assert len(extracted_text) > 0
            except (OSError, ValueError):
                # Some special characters might not be supported
                continue
    
    @pytest.mark.asyncio
    async def test_concurrent_processing_same_document(self, async_db, sample_pdf_with_text):
        """Test concurrent processing of the same document (race condition)."""
        document = Document(
            id=uuid.uuid4(),
            filename="race_test.pdf",
            file_path=str(sample_pdf_with_text),
            file_size=1024,
            processing_status=ProcessingStatus.PENDING
        )
        async_db.add(document)
        await async_db.commit()
        await async_db.refresh(document)
        
        # Process same document concurrently
        import asyncio
        results = await asyncio.gather(
            async_process_pdf_document(str(document.id)),
            async_process_pdf_document(str(document.id)),
            return_exceptions=True
        )
        
        # At least one should succeed, others might fail or succeed
        success_count = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "success")
        assert success_count >= 1