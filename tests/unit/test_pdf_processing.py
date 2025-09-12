"""
Unit tests for PDF processing functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import uuid

from app.core.pdf_processing import extract_text_from_pdf, async_process_pdf_document
from app.models.core import Document, ProcessingStatus


class TestPDFTextExtraction:
    """Test cases for PDF text extraction functionality."""
    
    def test_extract_text_from_valid_pdf(self, sample_pdf_with_text):
        """Test extracting text from a valid PDF with readable content."""
        extracted_text = extract_text_from_pdf(str(sample_pdf_with_text))
        
        assert extracted_text is not None
        assert len(extracted_text.strip()) > 0
        assert "ROOFING ESTIMATE" in extracted_text
        assert "3,500 sq ft" in extracted_text
        assert "Total Estimate" in extracted_text
    
    def test_extract_text_handles_empty_pdf(self, empty_pdf):
        """Test handling of empty PDF files."""
        extracted_text = extract_text_from_pdf(str(empty_pdf))
        
        # Should return empty string or minimal content
        assert isinstance(extracted_text, str)
    
    def test_extract_text_file_not_found(self):
        """Test handling of non-existent files."""
        with pytest.raises(FileNotFoundError):
            extract_text_from_pdf("/path/to/nonexistent/file.pdf")
    
    def test_extract_text_invalid_file_path(self):
        """Test handling of invalid file paths."""
        with pytest.raises((FileNotFoundError, PermissionError, OSError)):
            extract_text_from_pdf("")
    
    @patch('app.core.pdf_processing.PyPDF2.PdfReader')
    def test_extract_text_pypdf2_failure_triggers_ocr(self, mock_pdf_reader, sample_pdf_with_text):
        """Test that OCR is used when PyPDF2 fails to extract text."""
        # Mock PyPDF2 to fail or return empty text
        mock_reader_instance = Mock()
        mock_reader_instance.pages = []
        mock_pdf_reader.return_value = mock_reader_instance
        
        with patch('app.core.pdf_processing.convert_from_path') as mock_convert, \
             patch('app.core.pdf_processing.pytesseract.image_to_string') as mock_tesseract:
            
            # Mock image conversion
            mock_image = Mock()
            mock_convert.return_value = [mock_image]
            
            # Mock OCR result
            mock_tesseract.return_value = "OCR extracted text"
            
            result = extract_text_from_pdf(str(sample_pdf_with_text))
            
            assert "OCR extracted text" in result
            mock_convert.assert_called_once()
            mock_tesseract.assert_called_once()
    
    @patch('app.core.pdf_processing.convert_from_path')
    @patch('app.core.pdf_processing.PyPDF2.PdfReader')
    def test_extract_text_ocr_failure_handling(self, mock_pdf_reader, mock_convert, sample_pdf_with_text):
        """Test handling when both PyPDF2 and OCR fail."""
        # Mock PyPDF2 to return minimal text
        mock_reader_instance = Mock()
        mock_reader_instance.pages = []
        mock_pdf_reader.return_value = mock_reader_instance
        
        # Mock OCR to fail
        mock_convert.side_effect = Exception("OCR conversion failed")
        
        # Should not raise exception but log error
        result = extract_text_from_pdf(str(sample_pdf_with_text))
        assert isinstance(result, str)
    
    def test_extract_text_corrupted_pdf(self, corrupted_pdf):
        """Test handling of corrupted PDF files."""
        with pytest.raises(Exception):  # Should raise some kind of exception
            extract_text_from_pdf(str(corrupted_pdf))


class TestAsyncPDFProcessing:
    """Test cases for async PDF processing workflow."""
    
    @pytest.mark.asyncio
    async def test_async_process_pdf_document_success(self, async_db, sample_pdf_with_text):
        """Test successful async processing of a PDF document."""
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
        result = await async_process_pdf_document(str(document.id))
        
        assert result["status"] == "success"
        assert "extracted_text_length" in result
        assert result["extracted_text_length"] > 0
        
        # Verify document status updated
        await async_db.refresh(document)
        assert document.processing_status == ProcessingStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_async_process_pdf_document_not_found(self, async_db):
        """Test processing with non-existent document ID."""
        non_existent_id = str(uuid.uuid4())
        
        result = await async_process_pdf_document(non_existent_id)
        
        assert result["status"] == "error"
        assert "Document not found" in result["detail"]
    
    @pytest.mark.asyncio
    async def test_async_process_pdf_file_not_found(self, async_db):
        """Test processing when PDF file doesn't exist."""
        # Create document with non-existent file path
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
        
        # Verify document status updated to failed
        await async_db.refresh(document)
        assert document.processing_status == ProcessingStatus.FAILED
        assert document.processing_error is not None
    
    @pytest.mark.asyncio
    @patch('app.core.pdf_processing.extract_text_from_pdf')
    async def test_async_process_pdf_extraction_failure(self, mock_extract, async_db, sample_pdf_with_text):
        """Test handling of text extraction failures."""
        # Mock extraction to fail
        mock_extract.side_effect = Exception("Extraction failed")
        
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
        
        result = await async_process_pdf_document(str(document.id))
        
        assert result["status"] == "error"
        assert "Extraction failed" in result["error"]
        
        # Verify document status updated to failed
        await async_db.refresh(document)
        assert document.processing_status == ProcessingStatus.FAILED
    
    @pytest.mark.asyncio
    async def test_async_process_pdf_database_transaction(self, async_db, sample_pdf_with_text):
        """Test that database transactions work correctly during processing."""
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
        
        # Verify status progression
        await async_db.refresh(document)
        assert document.processing_status == ProcessingStatus.COMPLETED
        assert document.processing_error is None


class TestPDFProcessingEdgeCases:
    """Test edge cases and boundary conditions for PDF processing."""
    
    def test_extract_text_large_file(self, large_pdf):
        """Test processing of large PDF files."""
        extracted_text = extract_text_from_pdf(str(large_pdf))
        
        assert extracted_text is not None
        assert len(extracted_text) > 1000  # Should have substantial content
        assert "Page 1 of 50" in extracted_text
        assert "Roofing measurement data" in extracted_text
    
    def test_extract_text_special_characters(self, temp_dir):
        """Test handling of PDFs with special characters."""
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        pdf_path = temp_dir / "special_chars.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        
        # Add text with special characters
        c.setFont("Helvetica", 12)
        c.drawString(72, 800, "Special Characters: àáâãäå çéñü ¢£¤¥")
        c.drawString(72, 780, "Currency: $1,234.56 €789.12")
        c.drawString(72, 760, "Measurements: 12' × 8' = 96 sq ft")
        
        c.save()
        
        extracted_text = extract_text_from_pdf(str(pdf_path))
        assert extracted_text is not None
        assert len(extracted_text.strip()) > 0
    
    def test_extract_text_multiple_fonts_and_styles(self, temp_dir):
        """Test handling of PDFs with multiple fonts and styles."""
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        pdf_path = temp_dir / "multiple_fonts.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        
        # Different fonts and sizes
        c.setFont("Helvetica-Bold", 16)
        c.drawString(72, 800, "TITLE IN BOLD")
        
        c.setFont("Times-Roman", 12)
        c.drawString(72, 780, "Body text in Times Roman")
        
        c.setFont("Courier", 10)
        c.drawString(72, 760, "Monospace text: 1234.56 sq ft")
        
        c.save()
        
        extracted_text = extract_text_from_pdf(str(pdf_path))
        assert "TITLE IN BOLD" in extracted_text
        assert "Body text" in extracted_text
        assert "1234.56 sq ft" in extracted_text


class TestPDFProcessingValidation:
    """Test input validation and sanitization."""
    
    def test_extract_text_path_traversal_protection(self):
        """Test protection against path traversal attacks."""
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "/etc/passwd",
            "C:\\Windows\\System32\\config\\SAM"
        ]
        
        for path in malicious_paths:
            with pytest.raises((FileNotFoundError, PermissionError, OSError)):
                extract_text_from_pdf(path)
    
    def test_extract_text_very_long_filename(self, temp_dir):
        """Test handling of very long filenames."""
        long_name = "a" * 200 + ".pdf"
        
        # This should either work or fail gracefully
        with pytest.raises((FileNotFoundError, OSError)):
            extract_text_from_pdf(str(temp_dir / long_name))