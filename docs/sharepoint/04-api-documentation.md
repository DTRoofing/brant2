# Brant Roofing System - API Documentation

## 🔗 API Overview

The Brant Roofing System provides a comprehensive RESTful API for document processing, measurement extraction, and cost estimation. All API endpoints are versioned and follow RESTful conventions.

### **Base URL**

```
Production: https://api.brant-roofing.com/api/v1
Development: http://localhost:3001/api/v1
```

### **Authentication**

All API requests require authentication using JWT tokens in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## 📋 API Endpoints

### **Health Check**

#### `GET /health`

Check API health status.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "google_cloud": "healthy"
  }
}
```

### **Document Management**

#### `POST /documents/generate-url`

Generate a signed URL for file upload to Google Cloud Storage.

**Request Body:**

```json
{
  "filename": "roof_plan.pdf",
  "content_type": "application/pdf"
}
```

**Response:**

```json
{
  "upload_url": "https://storage.googleapis.com/bucket/uploads/uuid/roof_plan.pdf?signature=...",
  "gcs_object_name": "uploads/uuid/roof_plan.pdf"
}
```

#### `POST /documents/start-processing`

Start processing an uploaded document.

**Request Body:**

```json
{
  "gcs_object_name": "uploads/uuid/roof_plan.pdf",
  "original_filename": "roof_plan.pdf",
  "document_type": "blueprint"
}
```

**Response:**

```json
{
  "document_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "processing",
  "estimated_completion": "2025-01-15T10:35:00Z"
}
```

#### `GET /documents/{document_id}`

Get document details and processing status.

**Response:**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "filename": "roof_plan.pdf",
  "processing_status": "completed",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:32:00Z",
  "measurements": [
    {
      "id": "456e7890-e89b-12d3-a456-426614174001",
      "area_sf": 2500.5,
      "confidence_score": 0.95,
      "measurement_type": "roof_area",
      "extraction_method": "ai_ocr"
    }
  ]
}
```

### **Processing Pipeline**

#### `POST /pipeline/process/{document_id}`

Start the AI processing pipeline for a document.

**Request Body:**

```json
{
  "processing_mode": "standard",
  "extract_visual_elements": true,
  "extract_text_annotations": true,
  "extract_measurements": true
}
```

**Response:**

```json
{
  "task_id": "celery-task-uuid",
  "status": "queued",
  "estimated_duration": "2-5 minutes"
}
```

#### `GET /pipeline/status/{task_id}`

Get processing task status.

**Response:**

```json
{
  "task_id": "celery-task-uuid",
  "status": "completed",
  "progress": 100,
  "result": {
    "measurements": [...],
    "confidence_scores": {...},
    "processing_time": "3.2 seconds"
  }
}
```

### **Claude Processing**

#### `POST /pipeline/claude/analyze`

Send document content to Claude for analysis.

**Request Body:**

```json
{
  "document_id": "123e4567-e89b-12d3-a456-426614174000",
  "analysis_type": "measurement_extraction",
  "prompt": "Extract all roof measurements from this document"
}
```

**Response:**

```json
{
  "analysis_id": "claude-analysis-uuid",
  "status": "completed",
  "results": {
    "measurements": [...],
    "confidence": 0.92,
    "reasoning": "Based on the architectural drawing..."
  }
}
```

## 🔧 Request/Response Examples

### **Complete Workflow Example**

#### 1. Generate Upload URL

```bash
curl -X POST "https://api.brant-roofing.com/api/v1/documents/generate-url" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "house_blueprint.pdf",
    "content_type": "application/pdf"
  }'
```

#### 2. Upload File to GCS

```bash
curl -X PUT "https://storage.googleapis.com/bucket/uploads/uuid/house_blueprint.pdf?signature=..." \
  -H "Content-Type: application/pdf" \
  --data-binary @house_blueprint.pdf
```

#### 3. Start Processing

```bash
curl -X POST "https://api.brant-roofing.com/api/v1/documents/start-processing" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "gcs_object_name": "uploads/uuid/house_blueprint.pdf",
    "original_filename": "house_blueprint.pdf",
    "document_type": "blueprint"
  }'
```

#### 4. Check Processing Status

```bash
curl -X GET "https://api.brant-roofing.com/api/v1/documents/123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer your-jwt-token"
```

## 📊 Response Codes

| Code | Description | Meaning |
|------|-------------|---------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

## 🔒 Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Standard Users**: 100 requests per minute
- **Premium Users**: 500 requests per minute
- **Enterprise Users**: 1000 requests per minute

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248000
```

## 🛠️ SDK Examples

### **Python SDK**

```python
from brant_roofing import BrantClient

client = BrantClient(api_key="your-api-key")

# Generate upload URL
upload_data = client.documents.generate_upload_url(
    filename="roof_plan.pdf",
    content_type="application/pdf"
)

# Upload file
client.upload_file(upload_data["upload_url"], "roof_plan.pdf")

# Start processing
document = client.documents.start_processing(
    gcs_object_name=upload_data["gcs_object_name"],
    original_filename="roof_plan.pdf",
    document_type="blueprint"
)

# Check status
status = client.documents.get_status(document["document_id"])
print(f"Status: {status['processing_status']}")
```

### **JavaScript SDK**

```javascript
import { BrantClient } from '@brant-roofing/sdk';

const client = new BrantClient({ apiKey: 'your-api-key' });

// Generate upload URL
const uploadData = await client.documents.generateUploadUrl({
  filename: 'roof_plan.pdf',
  contentType: 'application/pdf'
});

// Upload file
await client.uploadFile(uploadData.uploadUrl, file);

// Start processing
const document = await client.documents.startProcessing({
  gcsObjectName: uploadData.gcsObjectName,
  originalFilename: 'roof_plan.pdf',
  documentType: 'blueprint'
});

// Check status
const status = await client.documents.getStatus(document.documentId);
console.log(`Status: ${status.processingStatus}`);
```

## 🔍 Error Handling

### **Error Response Format**

```json
{
  "detail": "Document not found",
  "error_code": "DOCUMENT_NOT_FOUND",
  "context": {
    "document_id": "123e4567-e89b-12d3-a456-426614174000"
  },
  "timestamp": "2025-01-15T10:30:00Z",
  "request_id": "req-uuid-123"
}
```

### **Common Error Codes**

- `DOCUMENT_NOT_FOUND`: Document ID doesn't exist
- `PROCESSING_FAILED`: Document processing failed
- `INVALID_FILE_TYPE`: Unsupported file format
- `FILE_SIZE_EXCEEDED`: File too large
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `VALIDATION_ERROR`: Request validation failed
- `GCP_SERVICE_ERROR`: Google Cloud service error

## 📈 Webhooks

The API supports webhooks for real-time notifications:

### **Webhook Events**

- `document.uploaded`: Document uploaded successfully
- `document.processing.started`: Processing started
- `document.processing.completed`: Processing completed
- `document.processing.failed`: Processing failed
- `measurement.extracted`: New measurement extracted

### **Webhook Payload**

```json
{
  "event": "document.processing.completed",
  "data": {
    "document_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "completed",
    "measurements_count": 5,
    "confidence_score": 0.95
  },
  "timestamp": "2025-01-15T10:35:00Z"
}
```

## 🧪 Testing

### **Postman Collection**

A complete Postman collection is available for testing all API endpoints:

- Import the collection from `/docs/postman/brant-api-collection.json`
- Set up environment variables for different environments
- Run automated tests for all endpoints

### **API Testing Tools**

- **Postman**: Manual testing and automation
- **Insomnia**: API testing and documentation
- **curl**: Command-line testing
- **HTTPie**: User-friendly command-line client

---

**Last Updated**: January 2025  
**Version**: 1.0.0  
**Document Owner**: Brant Roofing System Development Team
