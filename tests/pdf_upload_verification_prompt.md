# 🧪 PDF Upload & Google Services Verification Guide

## Quick Test Prompt

**Use this prompt to verify your PDF upload and Google Document AI integration is working:**

---

"I need to test if my Brant Roofing System can successfully upload and process PDF blueprints using Google Document AI. Please help me verify the complete pipeline from file upload to measurement extraction.

**My current setup:**
- FastAPI backend with file upload endpoint
- Google Document AI processor ID: `dc22888af5489eae`
- Google Cloud project: `brant-roofing-system-2025`
- Service account key in `secrets/` directory
- Celery workers for background processing

**What I want to test:**
1. Upload a PDF file via the API
2. Verify Google Document AI processes the file
3. Check that measurements are extracted
4. Confirm results are stored in the database

**Please provide:**
1. Step-by-step testing commands
2. Sample test PDF content recommendations
3. Expected API responses at each stage
4. Troubleshooting steps if something fails
5. Log locations to check for errors

**Current endpoint structure:**
- Upload: `POST /api/v1/documents/upload`
- Status: `GET /api/v1/documents/{id}/status`
- Results: `GET /api/v1/documents/{id}/measurements`

Help me create a comprehensive test that proves the Google integration is working end-to-end."

---

## 🔍 Detailed Verification Steps

### **Step 1: Prepare Test Environment**

**Create a test PDF file:**
```bash
# Create a simple test PDF with measurement text
echo "Roof Area: 2,500 square feet
Main Structure: 40' x 50'
Garage: 20' x 24' 
Total Project Area: 2,980 SF" > test-blueprint.txt

# Convert to PDF (if you have tools installed)
# Or create manually with any PDF tool
```

**Check service prerequisites:**
```bash
# Verify Docker containers are running
docker-compose ps

# Check if API is responding
curl http://localhost:3001/health

# Verify Google Cloud credentials
ls -la secrets/brant-roofing-system-2025-a5b8920b36d5.json
```

### **Step 2: Test File Upload**

**Upload test file:**
```bash
# Test file upload
curl -X POST "http://localhost:3001/api/v1/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test-blueprint.pdf" \
  -v

# Expected response:
# {
#   "document_id": "uuid-here",
#   "filename": "test-blueprint.pdf",
#   "status": "pending"
# }
```

**Save the document_id from response for next steps.**

### **Step 3: Monitor Processing Status**

**Check processing status:**
```bash
# Replace DOCUMENT_ID with actual ID from upload
export DOCUMENT_ID="your-document-id-here"

# Check status (repeat every 30 seconds)
curl "http://localhost:3001/api/v1/documents/$DOCUMENT_ID/status"

# Expected progression:
# 1. "status": "pending"
# 2. "status": "processing" 
# 3. "status": "completed" (success) OR "status": "failed" (error)
```

### **Step 4: Verify Results**

**Check extracted measurements:**
```bash
# Get measurement results
curl "http://localhost:3001/api/v1/documents/$DOCUMENT_ID/measurements"

# Expected response:
# [
#   {
#     "id": "measurement-uuid",
#     "area_sf": 2500.0,
#     "confidence_score": 0.85,
#     "measurement_type": "roof_area",
#     "extraction_method": "document_ai"
#   }
# ]
```

### **Step 5: Check Logs for Errors**

**View application logs:**
```bash
# API logs
docker-compose logs api

# Worker logs  
docker-compose logs worker

# Look for these success indicators:
# ✅ "Document AI processing completed"
# ✅ "Measurements extracted: X found"
# ✅ "Document processing completed successfully"

# Look for these error indicators:
# ❌ "Document AI quota exceeded"
# ❌ "Authentication failed"
# ❌ "Processing failed"
```

## 🚨 Troubleshooting Guide

### **Common Issues & Solutions**

**Issue: Upload fails with 400 error**
```bash
# Check file size and type
ls -lh test-blueprint.pdf
file test-blueprint.pdf

# Ensure file is actually a PDF
```

**Issue: Document AI authentication fails**
```bash
# Verify service account key location
ls -la secrets/brant-roofing-system-2025-a5b8920b36d5.json

# Check Docker volume mount
docker-compose exec api ls -la /secrets/

# Test Google Cloud authentication
docker-compose exec api python -c "
from google.cloud import documentai
client = documentai.DocumentProcessorServiceClient()
print('Authentication successful!')
"
```

**Issue: Processing stays in "pending" status**
```bash
# Check if Celery worker is running
docker-compose ps worker

# Check Redis connection
docker-compose exec redis redis-cli ping

# Check Celery task queue
docker-compose exec worker celery -A workers.celery_app inspect active
```

**Issue: No measurements extracted**
```bash
# Check Document AI response in logs
docker-compose logs worker | grep "Document AI"

# Verify PDF contains readable text
docker-compose exec api python -c "
import pdf2image
from PIL import Image
pages = pdf2image.convert_from_path('/app/uploads/your-file.pdf')
print(f'PDF has {len(pages)} pages')
"
```

## ✅ Success Indicators

**Your system is working correctly if you see:**

1. **Upload Success:**
   - HTTP 200 response with document_id
   - File appears in uploads directory

2. **Processing Success:**
   - Status progresses: pending → processing → completed
   - Processing time under 2 minutes for small files

3. **Document AI Success:**
   - Logs show "Document AI processing completed"
   - Raw text extracted from PDF
   - Entities found with confidence scores

4. **Claude Analysis Success:**
   - Measurements extracted with area values
   - Confidence scores between 0.7-1.0
   - Results stored in database

5. **Database Success:**
   - Document record updated to "completed"
   - Measurement records created
   - No error messages in logs

## 🎯 Quick Health Check Script

**Create this test script (`test-upload.sh`):**
```bash
#!/bin/bash

echo "🧪 Testing Brant Roofing PDF Upload & Processing..."

# 1. Health check
echo "1. Checking API health..."
if curl -f http://localhost:3001/health; then
    echo "✅ API is healthy"
else
    echo "❌ API is not responding"
    exit 1
fi

# 2. Upload test file
echo "2. Uploading test PDF..."
RESPONSE=$(curl -s -X POST "http://localhost:3001/api/v1/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test-blueprint.pdf")

DOCUMENT_ID=$(echo $RESPONSE | jq -r '.document_id')
echo "📄 Document ID: $DOCUMENT_ID"

# 3. Wait and check status
echo "3. Monitoring processing..."
for i in {1..20}; do
    STATUS=$(curl -s "http://localhost:3001/api/v1/documents/$DOCUMENT_ID/status" | jq -r '.status')
    echo "   Status: $STATUS"
    
    if [ "$STATUS" = "completed" ]; then
        echo "✅ Processing completed successfully!"
        break
    elif [ "$STATUS" = "failed" ]; then
        echo "❌ Processing failed!"
        exit 1
    fi
    
    sleep 15
done

# 4. Check results
echo "4. Checking extracted measurements..."
MEASUREMENTS=$(curl -s "http://localhost:3001/api/v1/documents/$DOCUMENT_ID/measurements")
COUNT=$(echo $MEASUREMENTS | jq '. | length')
echo "📊 Found $COUNT measurements"

if [ "$COUNT" -gt 0 ]; then
    echo "✅ PDF upload and Google Document AI integration working!"
else
    echo "⚠️ No measurements extracted - check logs"
fi
```

**Run the test:**
```bash
chmod +x test-upload.sh
./test-upload.sh
```

This comprehensive verification will confirm your PDF upload and Google Document AI integration is working correctly! 🎉