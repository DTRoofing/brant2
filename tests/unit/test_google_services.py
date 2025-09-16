"""
Unit tests for Google Cloud services integration.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from pathlib import Path
import json

from app.services.google_services import GoogleCloudService, google_service


class TestGoogleCloudService:
    """Test cases for Google Cloud service integration."""
    
    def test_init_without_credentials(self):
        """Test initialization without credentials."""
        with patch('app.services.google_services.settings') as mock_settings:
            mock_settings.GOOGLE_APPLICATION_CREDENTIALS = None
            mock_settings.GOOGLE_CLOUD_PROJECT_ID = "test-project"
            
            service = GoogleCloudService()
            
            assert service.credentials is None
            assert service._document_ai_client is None
            assert service._storage_client is None
            assert service._vision_client is None
    
    @patch('app.services.google_services.service_account')
    @patch('app.services.google_services.os.path.exists')
    def test_init_with_valid_credentials(self, mock_exists, mock_service_account):
        """Test initialization with valid credentials file."""
        mock_exists.return_value = True
        mock_credentials = Mock()
        mock_service_account.Credentials.from_service_account_file.return_value = mock_credentials
        
        with patch('app.services.google_services.settings') as mock_settings:
            mock_settings.GOOGLE_APPLICATION_CREDENTIALS = "/path/to/credentials.json"
            mock_settings.GOOGLE_CLOUD_PROJECT_ID = "test-project"
            mock_settings.DOCUMENT_AI_PROCESSOR_ID = "processor-id"
            mock_settings.DOCUMENT_AI_LOCATION = "us"
            mock_settings.GOOGLE_CLOUD_STORAGE_BUCKET = "test-bucket"
            
            service = GoogleCloudService()
            
            assert service.credentials == mock_credentials
            mock_service_account.Credentials.from_service_account_file.assert_called_once_with(
                "/path/to/credentials.json"
            )
    
    @patch('app.services.google_services.service_account')
    @patch('app.services.google_services.os.path.exists')
    def test_init_with_missing_credentials_file(self, mock_exists, mock_service_account):
        """Test initialization when credentials file doesn't exist."""
        mock_exists.return_value = False
        
        with patch('app.services.google_services.settings') as mock_settings:
            mock_settings.GOOGLE_APPLICATION_CREDENTIALS = "/path/to/missing.json"
            
            service = GoogleCloudService()
            
            assert service.credentials is None
            mock_service_account.Credentials.from_service_account_file.assert_not_called()
    
    @patch('app.services.google_services.documentai')
    def test_document_ai_client_lazy_initialization(self, mock_documentai):
        """Test lazy initialization of Document AI client."""
        mock_credentials = Mock()
        mock_client = Mock()
        mock_documentai.DocumentProcessorServiceClient.return_value = mock_client
        
        service = GoogleCloudService()
        service.credentials = mock_credentials
        
        # First access should initialize
        client1 = service.document_ai_client
        assert client1 == mock_client
        mock_documentai.DocumentProcessorServiceClient.assert_called_once_with(
            credentials=mock_credentials
        )
        
        # Second access should return cached instance
        client2 = service.document_ai_client
        assert client2 == mock_client
        assert mock_documentai.DocumentProcessorServiceClient.call_count == 1
    
    @patch('app.services.google_services.storage')
    def test_storage_client_lazy_initialization(self, mock_storage):
        """Test lazy initialization of Storage client."""
        mock_credentials = Mock()
        mock_client = Mock()
        mock_storage.Client.return_value = mock_client
        
        with patch('app.services.google_services.settings') as mock_settings:
            mock_settings.GOOGLE_CLOUD_PROJECT_ID = "test-project"
            
            service = GoogleCloudService()
            service.credentials = mock_credentials
            service.project_id = "test-project"
            
            client = service.storage_client
            
            assert client == mock_client
            mock_storage.Client.assert_called_once_with(
                credentials=mock_credentials,
                project="test-project"
            )
    
    @patch('app.services.google_services.vision')
    def test_vision_client_lazy_initialization(self, mock_vision):
        """Test lazy initialization of Vision client."""
        mock_credentials = Mock()
        mock_client = Mock()
        mock_vision.ImageAnnotatorClient.return_value = mock_client
        
        service = GoogleCloudService()
        service.credentials = mock_credentials
        
        client = service.vision_client
        
        assert client == mock_client
        mock_vision.ImageAnnotatorClient.assert_called_once_with(
            credentials=mock_credentials
        )


class TestGoogleCloudStorageUpload:
    """Test cases for Google Cloud Storage upload functionality."""
    
    @pytest.mark.asyncio
    async def test_upload_to_gcs_success(self, sample_pdf_with_text):
        """Test successful file upload to Google Cloud Storage."""
        mock_storage_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        mock_storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        service = GoogleCloudService()
        service._storage_client = mock_storage_client
        service.bucket_name = "test-bucket"
        
        result = await service.upload_to_gcs(
            str(sample_pdf_with_text), 
            "documents/test.pdf"
        )
        
        assert result == "gs://test-bucket/documents/test.pdf"
        mock_storage_client.bucket.assert_called_once_with("test-bucket")
        mock_bucket.blob.assert_called_once_with("documents/test.pdf")
        mock_blob.upload_from_filename.assert_called_once_with(str(sample_pdf_with_text))
    
    @pytest.mark.asyncio
    async def test_upload_to_gcs_no_client(self):
        """Test upload when storage client is not configured."""
        service = GoogleCloudService()
        service._storage_client = None
        
        result = await service.upload_to_gcs("test.pdf", "dest.pdf")
        
        assert result == ""
    
    @pytest.mark.asyncio
    async def test_upload_to_gcs_no_bucket(self, sample_pdf_with_text):
        """Test upload when bucket name is not configured."""
        mock_storage_client = Mock()
        
        service = GoogleCloudService()
        service._storage_client = mock_storage_client
        service.bucket_name = None
        
        result = await service.upload_to_gcs(
            str(sample_pdf_with_text), 
            "documents/test.pdf"
        )
        
        assert result == ""
    
    @pytest.mark.asyncio
    async def test_upload_to_gcs_failure(self, sample_pdf_with_text):
        """Test handling of upload failures."""
        mock_storage_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        mock_storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.upload_from_filename.side_effect = Exception("Upload failed")
        
        service = GoogleCloudService()
        service._storage_client = mock_storage_client
        service.bucket_name = "test-bucket"
        
        result = await service.upload_to_gcs(
            str(sample_pdf_with_text), 
            "documents/test.pdf"
        )
        
        assert result == ""


class TestGoogleDocumentAI:
    """Test cases for Google Document AI processing."""
    
    @pytest.mark.asyncio
    async def test_process_document_with_ai_success(self, sample_pdf_with_text):
        """Test successful document processing with Document AI."""
        # Mock Document AI response
        mock_result = Mock()
        mock_document = Mock()
        mock_document.text = "Extracted text from Document AI"
        mock_document.pages = [Mock(), Mock()]  # 2 pages
        mock_document.entities = []
        mock_result.document = mock_document
        
        mock_client = Mock()
        mock_client.process_document.return_value = mock_result
        
        service = GoogleCloudService()
        service._document_ai_client = mock_client
        service.project_id = "test-project"
        service.processor_id = "processor-id"
        service.location = "us"
        
        result = await service.process_document_with_ai(str(sample_pdf_with_text))
        
        assert result["text"] == "Extracted text from Document AI"
        assert result["pages"] == 2
        assert "entities" in result
        assert "tables" in result
        assert "measurements" in result
    
    @pytest.mark.asyncio
    async def test_process_document_with_ai_no_client(self, sample_pdf_with_text):
        """Test processing when Document AI client is not configured."""
        service = GoogleCloudService()
        service._document_ai_client = None
        
        result = await service.process_document_with_ai(str(sample_pdf_with_text))
        
        assert result == {}
    
    @pytest.mark.asyncio
    async def test_process_document_with_ai_missing_config(self, sample_pdf_with_text):
        """Test processing with missing configuration."""
        mock_client = Mock()
        
        service = GoogleCloudService()
        service._document_ai_client = mock_client
        service.project_id = None  # Missing project ID
        service.processor_id = "processor-id"
        
        result = await service.process_document_with_ai(str(sample_pdf_with_text))
        
        assert result == {}
    
    @pytest.mark.asyncio
    async def test_process_document_with_ai_with_entities(self, sample_pdf_with_text):
        """Test processing with entities containing measurements."""
        # Mock Document AI response with entities
        mock_entity1 = Mock()
        mock_entity1.type_ = "area"
        mock_entity1.mention_text = "3500 sq ft"
        mock_entity1.confidence = 0.95
        
        mock_entity2 = Mock()
        mock_entity2.type_ = "measurement"
        mock_entity2.mention_text = "roof area 2800 square feet"
        mock_entity2.confidence = 0.87
        
        mock_entity3 = Mock()
        mock_entity3.type_ = "other"
        mock_entity3.mention_text = "property address"
        mock_entity3.confidence = 0.92
        
        mock_document = Mock()
        mock_document.text = "Document with entities"
        mock_document.pages = [Mock()]
        mock_document.entities = [mock_entity1, mock_entity2, mock_entity3]
        
        # Mock pages with no tables
        mock_document.pages[0].tables = []
        
        mock_result = Mock()
        mock_result.document = mock_document
        
        mock_client = Mock()
        mock_client.process_document.return_value = mock_result
        
        service = GoogleCloudService()
        service._document_ai_client = mock_client
        service.project_id = "test-project"
        service.processor_id = "processor-id"
        service.location = "us"
        
        result = await service.process_document_with_ai(str(sample_pdf_with_text))
        
        assert len(result["entities"]) == 3
        assert len(result["measurements"]) == 2  # Only entities with measurement keywords
        
        # Check that measurement entities are properly identified
        measurement_texts = [m["text"] for m in result["measurements"]]
        assert "3500 sq ft" in measurement_texts
        assert "roof area 2800 square feet" in measurement_texts
    
    @pytest.mark.asyncio
    async def test_process_document_with_ai_with_tables(self, sample_pdf_with_text):
        """Test processing documents with tables."""
        # Mock table structure
        mock_cell1 = Mock()
        mock_cell1.layout.text_anchor.text_segments = [Mock(start_index=0, end_index=5)]
        
        mock_cell2 = Mock()
        mock_cell2.layout.text_anchor.text_segments = [Mock(start_index=5, end_index=10)]
        
        mock_row = Mock()
        mock_row.cells = [mock_cell1, mock_cell2]
        
        mock_table = Mock()
        mock_table.body_rows = [mock_row]
        
        mock_page = Mock()
        mock_page.tables = [mock_table]
        
        mock_document = Mock()
        mock_document.text = "Cell1Cell2"  # Text for extraction
        mock_document.pages = [mock_page]
        mock_document.entities = []
        
        mock_result = Mock()
        mock_result.document = mock_document
        
        mock_client = Mock()
        mock_client.process_document.return_value = mock_result
        
        service = GoogleCloudService()
        service._document_ai_client = mock_client
        service.project_id = "test-project"
        service.processor_id = "processor-id"
        service.location = "us"
        
        result = await service.process_document_with_ai(str(sample_pdf_with_text))
        
        assert len(result["tables"]) == 1
        assert len(result["tables"][0]) == 1  # One row
        assert len(result["tables"][0][0]) == 2  # Two cells
    
    @pytest.mark.asyncio
    async def test_process_document_with_ai_failure(self, sample_pdf_with_text):
        """Test handling of Document AI processing failures."""
        mock_client = Mock()
        mock_client.process_document.side_effect = Exception("API Error")
        
        service = GoogleCloudService()
        service._document_ai_client = mock_client
        service.project_id = "test-project"
        service.processor_id = "processor-id"
        service.location = "us"
        
        result = await service.process_document_with_ai(str(sample_pdf_with_text))
        
        assert result == {}
    
    def test_get_text_from_layout(self):
        """Test text extraction from layout elements."""
        # Mock layout with text segments
        mock_segment1 = Mock()
        mock_segment1.start_index = 0
        mock_segment1.end_index = 5
        
        mock_segment2 = Mock()
        mock_segment2.start_index = 10
        mock_segment2.end_index = 15
        
        mock_layout = Mock()
        mock_layout.text_anchor.text_segments = [mock_segment1, mock_segment2]
        
        service = GoogleCloudService()
        document_text = "Hello     World Extra Text"
        
        result = service._get_text_from_layout(mock_layout, document_text)
        
        assert result == "HelloWorld"
    
    def test_get_text_from_layout_with_none_start_index(self):
        """Test text extraction when start_index is None."""
        mock_segment = Mock()
        mock_segment.start_index = None
        mock_segment.end_index = 5
        
        mock_layout = Mock()
        mock_layout.text_anchor.text_segments = [mock_segment]
        
        service = GoogleCloudService()
        document_text = "Hello World"
        
        result = service._get_text_from_layout(mock_layout, document_text)
        
        assert result == "Hello"


class TestGoogleVisionAPI:
    """Test cases for Google Vision API integration."""
    
    @pytest.mark.asyncio
    async def test_analyze_image_with_vision_success(self, sample_pdf_with_text):
        """Test successful image analysis with Vision API."""
        # Mock Vision API response
        mock_annotation1 = Mock()
        mock_annotation1.description = "Full text content"
        
        mock_annotation2 = Mock()
        mock_annotation2.description = "Roofing"
        mock_vertex1 = Mock()
        mock_vertex1.x, mock_vertex1.y = 10, 20
        mock_vertex2 = Mock()
        mock_vertex2.x, mock_vertex2.y = 100, 120
        mock_annotation2.bounding_poly.vertices = [mock_vertex1, mock_vertex2]
        
        mock_response = Mock()
        mock_response.text_annotations = [mock_annotation1, mock_annotation2]
        
        mock_client = Mock()
        mock_client.text_detection.return_value = mock_response
        
        service = GoogleCloudService()
        service._vision_client = mock_client
        
        # Use a dummy file (content doesn't matter for mocked test)
        result = await service.analyze_image_with_vision(str(sample_pdf_with_text))
        
        assert result["text"] == "Full text content"
        assert len(result["annotations"]) == 1
        assert result["annotations"][0]["text"] == "Roofing"
        assert result["annotations"][0]["bounds"] == [(10, 20), (100, 120)]
    
    @pytest.mark.asyncio
    async def test_analyze_image_with_vision_no_client(self, sample_pdf_with_text):
        """Test image analysis when Vision client is not configured."""
        service = GoogleCloudService()
        service._vision_client = None
        
        result = await service.analyze_image_with_vision(str(sample_pdf_with_text))
        
        assert result == {}
    
    @pytest.mark.asyncio
    async def test_analyze_image_with_vision_no_text_found(self, sample_pdf_with_text):
        """Test image analysis when no text is detected."""
        mock_response = Mock()
        mock_response.text_annotations = []
        
        mock_client = Mock()
        mock_client.text_detection.return_value = mock_response
        
        service = GoogleCloudService()
        service._vision_client = mock_client
        
        result = await service.analyze_image_with_vision(str(sample_pdf_with_text))
        
        assert result["text"] == ""
        assert result["annotations"] == []
    
    @pytest.mark.asyncio
    async def test_analyze_image_with_vision_failure(self, sample_pdf_with_text):
        """Test handling of Vision API failures."""
        mock_client = Mock()
        mock_client.text_detection.side_effect = Exception("Vision API Error")
        
        service = GoogleCloudService()
        service._vision_client = mock_client
        
        result = await service.analyze_image_with_vision(str(sample_pdf_with_text))
        
        assert result == {}


class TestGoogleServicesSingleton:
    """Test the singleton google_service instance."""
    
    def test_google_service_singleton_creation(self):
        """Test that google_service is properly instantiated."""
        from app.services.google_services import google_service
        
        assert isinstance(google_service, GoogleCloudService)
        assert google_service is not None