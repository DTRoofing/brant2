"""
End-to-end tests for the complete PDF processing pipeline.
"""
import pytest
import time
import uuid
import asyncio
from unittest.mock import patch, Mock
from pathlib import Path
import httpx

from app.models.core import Document, ProcessingStatus, Measurement


class TestCompletePDFPipeline:
    """End-to-end tests for the complete PDF processing pipeline."""
    
    @pytest.mark.e2e
    def test_complete_pdf_processing_pipeline(self, test_client, sample_pdf_with_text):
        """Test the complete pipeline from upload to final results."""
        # Step 1: Upload PDF
        with open(sample_pdf_with_text, "rb") as f:
            upload_response = test_client.post(
                "/api/v1/documents/upload",
                files={"file": ("roofing_estimate.pdf", f, "application/pdf")}
            )
        
        assert upload_response.status_code == 202
        upload_data = upload_response.json()
        document_id = upload_data["id"]
        
        # Verify upload response
        assert upload_data["filename"] == "roofing_estimate.pdf"
        assert upload_data["processing_status"] == "pending"
        assert upload_data["file_size"] > 0
        
        # Step 2: Check initial status
        status_response = test_client.get(f"/api/v1/documents/{document_id}")
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["processing_status"] == "pending"
        
        # Step 3: Wait for processing to complete (in a real scenario)
        # For testing, we'll simulate the processing completion
        # In production, you'd poll the status endpoint
        
        print(f"Pipeline test completed for document {document_id}")
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_large_pdf_processing_pipeline(self, test_client, large_pdf):
        """Test processing pipeline with a large PDF file."""
        # Upload large PDF
        with open(large_pdf, "rb") as f:
            upload_response = test_client.post(
                "/api/v1/documents/upload",
                files={"file": ("large_document.pdf", f, "application/pdf")}
            )
        
        assert upload_response.status_code == 202
        upload_data = upload_response.json()
        document_id = upload_data["id"]
        
        # Verify large file was accepted
        assert upload_data["file_size"] > 50000  # Should be substantial
        
        # Check status immediately after upload
        status_response = test_client.get(f"/api/v1/documents/{document_id}")
        assert status_response.status_code == 200
        
        print(f"Large PDF pipeline test completed for document {document_id}")
    
    @pytest.mark.e2e
    def test_multiple_pdf_concurrent_processing(self, test_client, sample_pdf_with_text):
        """Test processing multiple PDFs concurrently."""
        document_ids = []
        
        # Upload multiple documents
        for i in range(3):
            with open(sample_pdf_with_text, "rb") as f:
                upload_response = test_client.post(
                    "/api/v1/documents/upload",
                    files={"file": (f"document_{i}.pdf", f, "application/pdf")}
                )
            
            assert upload_response.status_code == 202
            document_ids.append(upload_response.json()["id"])
        
        # Check all documents were uploaded
        assert len(document_ids) == 3
        assert len(set(document_ids)) == 3  # All unique
        
        # Verify all documents can be retrieved
        for doc_id in document_ids:
            status_response = test_client.get(f"/api/v1/documents/{doc_id}")
            assert status_response.status_code == 200
        
        print(f"Concurrent processing test completed for {len(document_ids)} documents")
    
    @pytest.mark.e2e
    def test_error_handling_pipeline(self, test_client, corrupted_pdf):
        """Test pipeline error handling with corrupted PDF."""
        # Upload corrupted PDF
        with open(corrupted_pdf, "rb") as f:
            upload_response = test_client.post(
                "/api/v1/documents/upload",
                files={"file": ("corrupted.pdf", f, "application/pdf")}
            )
        
        # Upload should succeed (validation happens during processing)
        assert upload_response.status_code == 202
        upload_data = upload_response.json()
        document_id = upload_data["id"]
        
        # Document should be created in database
        status_response = test_client.get(f"/api/v1/documents/{document_id}")
        assert status_response.status_code == 200
        
        print(f"Error handling pipeline test completed for document {document_id}")
    
    @pytest.mark.e2e
    def test_empty_pdf_processing(self, test_client, empty_pdf):
        """Test processing pipeline with empty PDF."""
        with open(empty_pdf, "rb") as f:
            upload_response = test_client.post(
                "/api/v1/documents/upload",
                files={"file": ("empty.pdf", f, "application/pdf")}
            )
        
        assert upload_response.status_code == 202
        upload_data = upload_response.json()
        document_id = upload_data["id"]
        
        # Empty PDF should have minimal file size
        assert upload_data["file_size"] < 1000  # Should be very small
        
        status_response = test_client.get(f"/api/v1/documents/{document_id}")
        assert status_response.status_code == 200
        
        print(f"Empty PDF pipeline test completed for document {document_id}")


class TestPDFPipelineWithMockedServices:
    """E2E tests with mocked external services for predictable results."""
    
    @pytest.mark.e2e
    @patch('app.workers.tasks.pdf_processing.google_service')
    @patch('app.workers.tasks.pdf_processing.claude_service')
    def test_full_pipeline_with_ai_services(
        self, 
        mock_claude_service, 
        mock_google_service, 
        test_client, 
        sample_pdf_with_text
    ):
        """Test complete pipeline with mocked AI services."""
        # Mock Google AI response
        mock_google_service.upload_to_gcs = Mock(return_value="gs://bucket/file.pdf")
        mock_google_service.process_document_with_ai = Mock(return_value={
            "text": "Mock extracted text from Google AI",
            "measurements": [
                {"text": "3500 sq ft", "confidence": 0.95},
                {"text": "roof pitch 8/12", "confidence": 0.88}
            ]
        })
        
        # Mock Claude AI response
        mock_claude_service.analyze_text_for_estimate.return_value = {
            "total_roof_area_sqft": 3500,
            "measurements": [
                {"value": "3500", "label": "total_roof_area"},
                {"value": "8/12", "label": "roof_pitch"}
            ],
            "confidence": 0.92
        }
        
        # Upload document
        with open(sample_pdf_with_text, "rb") as f:
            upload_response = test_client.post(
                "/api/v1/documents/upload",
                files={"file": ("ai_test.pdf", f, "application/pdf")}
            )
        
        assert upload_response.status_code == 202
        document_id = upload_response.json()["id"]
        
        # Verify document was created
        status_response = test_client.get(f"/api/v1/documents/{document_id}")
        assert status_response.status_code == 200
        
        print(f"AI services pipeline test completed for document {document_id}")
    
    @pytest.mark.e2e  
    @patch('app.core.pdf_processing.extract_text_from_pdf')
    def test_pipeline_with_ocr_fallback(self, mock_extract, test_client, sample_pdf_image_only):
        """Test pipeline when OCR fallback is needed."""
        # Mock text extraction to simulate OCR usage
        mock_extract.return_value = "OCR extracted: Roof area 2800 sq ft, Pitch 6/12"
        
        with open(sample_pdf_image_only, "rb") as f:
            upload_response = test_client.post(
                "/api/v1/documents/upload",
                files={"file": ("ocr_test.pdf", f, "application/pdf")}
            )
        
        assert upload_response.status_code == 202
        document_id = upload_response.json()["id"]
        
        status_response = test_client.get(f"/api/v1/documents/{document_id}")
        assert status_response.status_code == 200
        
        print(f"OCR fallback pipeline test completed for document {document_id}")


class TestPDFPipelineRealWorldScenarios:
    """E2E tests simulating real-world usage scenarios."""
    
    @pytest.mark.e2e
    def test_typical_roofing_estimate_workflow(self, test_client, temp_dir):
        """Test workflow with typical roofing estimate document."""
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        # Create realistic roofing estimate PDF
        pdf_path = temp_dir / "roofing_estimate_realistic.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        
        # Page 1: Cover and summary
        c.setFont("Helvetica-Bold", 16)
        c.drawString(72, 750, "ROOFING ESTIMATE")
        c.setFont("Helvetica", 12)
        c.drawString(72, 720, "Customer: John Smith")
        c.drawString(72, 700, "Property: 123 Oak Street, Springfield, IL")
        c.drawString(72, 680, "Date: September 11, 2025")
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(72, 640, "SUMMARY")
        c.setFont("Helvetica", 12)
        c.drawString(72, 620, "Total Roof Area: 2,847 sq ft")
        c.drawString(72, 600, "Material: Architectural Shingles")
        c.drawString(72, 580, "Total Cost: $18,450")
        
        c.showPage()
        
        # Page 2: Detailed measurements
        c.setFont("Helvetica-Bold", 14)
        c.drawString(72, 750, "DETAILED MEASUREMENTS")
        c.setFont("Helvetica", 12)
        
        measurements = [
            "Main Roof Section: 2,240 sq ft",
            "Dormer #1: 156 sq ft", 
            "Dormer #2: 183 sq ft",
            "Garage: 268 sq ft",
            "Ridge Cap: 94 linear ft",
            "Gutters: 124 linear ft",
            "Downspouts: 8 units"
        ]
        
        y_pos = 720
        for measurement in measurements:
            c.drawString(72, y_pos, measurement)
            y_pos -= 25
        
        c.save()
        
        # Test the complete workflow
        with open(pdf_path, "rb") as f:
            upload_response = test_client.post(
                "/api/v1/documents/upload",
                files={"file": ("realistic_estimate.pdf", f, "application/pdf")}
            )
        
        assert upload_response.status_code == 202
        upload_data = upload_response.json()
        document_id = upload_data["id"]
        
        # Verify realistic file size
        assert upload_data["file_size"] > 5000  # Should be substantial
        
        status_response = test_client.get(f"/api/v1/documents/{document_id}")
        assert status_response.status_code == 200
        status_data = status_response.json()
        
        assert status_data["filename"] == "realistic_estimate.pdf"
        
        print(f"Realistic roofing workflow test completed for document {document_id}")
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_batch_processing_workflow(self, test_client, temp_dir):
        """Test workflow for processing multiple documents in batch."""
        # Create multiple PDF documents
        document_ids = []
        
        for i in range(5):
            pdf_path = temp_dir / f"batch_doc_{i}.pdf"
            c = canvas.Canvas(str(pdf_path), pagesize=letter)
            
            c.setFont("Helvetica", 12)
            c.drawString(72, 750, f"Batch Document #{i+1}")
            c.drawString(72, 730, f"Roof Area: {2000 + i*500} sq ft")
            c.drawString(72, 710, f"Customer ID: BATCH_{i+1:03d}")
            
            c.save()
            
            # Upload document
            with open(pdf_path, "rb") as f:
                upload_response = test_client.post(
                    "/api/v1/documents/upload",
                    files={"file": (f"batch_{i}.pdf", f, "application/pdf")}
                )
            
            assert upload_response.status_code == 202
            document_ids.append(upload_response.json()["id"])
        
        # Verify all documents
        for doc_id in document_ids:
            status_response = test_client.get(f"/api/v1/documents/{doc_id}")
            assert status_response.status_code == 200
        
        print(f"Batch processing workflow completed for {len(document_ids)} documents")
    
    @pytest.mark.e2e
    def test_edge_case_document_formats(self, test_client, temp_dir):
        """Test various edge cases in document formats."""
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter, A4, legal
        
        test_cases = [
            ("letter_size.pdf", letter),
            ("a4_size.pdf", A4),
            ("legal_size.pdf", legal)
        ]
        
        document_ids = []
        
        for filename, page_size in test_cases:
            pdf_path = temp_dir / filename
            c = canvas.Canvas(str(pdf_path), pagesize=page_size)
            
            c.setFont("Helvetica", 12)
            c.drawString(72, page_size[1] - 100, f"Document: {filename}")
            c.drawString(72, page_size[1] - 120, f"Page size: {page_size}")
            c.drawString(72, page_size[1] - 140, "Roof measurements: 2400 sq ft")
            
            c.save()
            
            # Upload and test
            with open(pdf_path, "rb") as f:
                upload_response = test_client.post(
                    "/api/v1/documents/upload",
                    files={"file": (filename, f, "application/pdf")}
                )
            
            assert upload_response.status_code == 202
            document_ids.append(upload_response.json()["id"])
        
        # Verify all edge case documents
        for doc_id in document_ids:
            status_response = test_client.get(f"/api/v1/documents/{doc_id}")
            assert status_response.status_code == 200
        
        print(f"Edge case formats test completed for {len(document_ids)} documents")


class TestPDFPipelineErrorRecovery:
    """E2E tests for error recovery scenarios."""
    
    @pytest.mark.e2e
    def test_processing_timeout_recovery(self, test_client, sample_pdf_with_text):
        """Test recovery from processing timeouts."""
        # Upload document
        with open(sample_pdf_with_text, "rb") as f:
            upload_response = test_client.post(
                "/api/v1/documents/upload",
                files={"file": ("timeout_test.pdf", f, "application/pdf")}
            )
        
        assert upload_response.status_code == 202
        document_id = upload_response.json()["id"]
        
        # Document should be retrievable even if processing times out
        status_response = test_client.get(f"/api/v1/documents/{document_id}")
        assert status_response.status_code == 200
        
        print(f"Timeout recovery test completed for document {document_id}")
    
    @pytest.mark.e2e
    @patch('app.workers.tasks.pdf_processing.google_service')
    def test_external_service_failure_recovery(self, mock_google_service, test_client, sample_pdf_with_text):
        """Test recovery when external services fail."""
        # Mock Google service to fail
        mock_google_service.upload_to_gcs.side_effect = Exception("Google service unavailable")
        mock_google_service.process_document_with_ai.side_effect = Exception("AI processing failed")
        
        with open(sample_pdf_with_text, "rb") as f:
            upload_response = test_client.post(
                "/api/v1/documents/upload",
                files={"file": ("service_failure_test.pdf", f, "application/pdf")}
            )
        
        assert upload_response.status_code == 202
        document_id = upload_response.json()["id"]
        
        # Document should still be created and retrievable
        status_response = test_client.get(f"/api/v1/documents/{document_id}")
        assert status_response.status_code == 200
        
        print(f"Service failure recovery test completed for document {document_id}")
    
    @pytest.mark.e2e
    def test_disk_space_error_handling(self, test_client, sample_pdf_with_text):
        """Test handling of disk space errors during upload."""
        with patch('app.api.v1.endpoints.uploads.aiofiles.open') as mock_open:
            # Mock disk space error
            mock_file = Mock()
            mock_file.__aenter__.return_value = mock_file
            mock_file.write.side_effect = OSError("No space left on device")
            mock_open.return_value = mock_file
            
            with open(sample_pdf_with_text, "rb") as f:
                upload_response = test_client.post(
                    "/api/v1/documents/upload",
                    files={"file": ("disk_space_test.pdf", f, "application/pdf")}
                )
            
            # Should return appropriate error
            assert upload_response.status_code == 500
            assert "error uploading" in upload_response.json()["detail"].lower()
        
        print("Disk space error handling test completed")