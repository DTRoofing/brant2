# Brant Roofing System - Automated Test Suite

This directory contains comprehensive automated tests for the Brant Roofing
System upload pipeline.

## 🧪 Test Files Overview

### Core Test Scripts

1. **`test_upload_simple.py`** - Simple API-based test (no browser required)
   - Tests all API endpoints
   - Uploads file to Google Cloud Storage
   - Monitors processing progress
   - **Recommended for CI/CD and quick validation**

2. **`test_upload_automation.py`** - Full browser automation test
   - Uses Selenium WebDriver
   - Tests frontend interfaces
   - Visual browser interaction
   - **Recommended for comprehensive UI testing**

3. **`demo_upload_test.py`** - Interactive step-by-step demo
   - User-guided demonstration
   - Educational and debugging tool
   - **Recommended for learning and troubleshooting**

### Test Runner Scripts

1. **`run_tests.py`** - Comprehensive test runner
   - Multiple test types (quick, simple, browser, all)
   - System requirements checking
   - **Recommended for automated testing**

2. **`run_browser_test.py`** - Browser test launcher
   - Handles dependency installation
   - **Recommended for browser-specific testing**

## 🚀 Quick Start

### Prerequisites

1. **Docker containers running:**

   ```bash
   docker-compose --profile local up -d
   ```

2. **Test file available:**
   - `tests/mcdonalds collection/small_set.pdf`

3. **Python dependencies:**

   ```bash
   pip install requests selenium
   ```

### Running Tests

#### Option 1: Simple API Test (Recommended)

```bash
python test_upload_simple.py
```

#### Option 2: Quick System Check

```bash
python run_tests.py --type quick
```

#### Option 3: Full Test Suite

```bash
python run_tests.py --type all
```

#### Option 4: Interactive Demo

```bash
python demo_upload_test.py
```

## 📋 Test Coverage

### API Endpoints Tested

- ✅ `GET /api/v1/health` - Health check
- ✅ `POST /api/v1/documents/generate-url` - Upload URL generation
- ✅ `POST /api/v1/documents/start-processing` - Document processing

### System Components Tested

- ✅ **API Server** - FastAPI application
- ✅ **Database** - PostgreSQL connectivity and queries
- ✅ **Storage** - Google Cloud Storage upload/download
- ✅ **Worker** - Celery background processing
- ✅ **Frontend** - Next.js web interface
- ✅ **Monitoring** - Flower task monitoring

### File Processing Tested

- ✅ **Large File Handling** - 24MB+ PDFs automatically chunked
- ✅ **Cloud Storage** - Direct upload to GCS
- ✅ **Document AI** - OCR and text extraction
- ✅ **Background Processing** - Celery worker tasks
- ✅ **Status Tracking** - Real-time progress monitoring

## 🔧 Test Configuration

### Environment Variables

Tests use the following endpoints by default:

- API: `http://localhost:3001`
- Frontend: `http://localhost:3000`
- Flower: `http://localhost:5555`

### Test File

- **File**: `tests/mcdonalds collection/small_set.pdf`
- **Size**: ~24.7MB
- **Type**: PDF document
- **Purpose**: Tests large file handling and chunking

## 📊 Test Results

### Expected Results

```text
📋 TEST RESULTS SUMMARY
============================================================
✅ API Health: PASS - healthy
✅ Database Connectivity: PASS - X documents
✅ Upload URL Generation: PASS - uploads/uuid/filename.pdf
✅ File Upload: PASS - 24,759,678 bytes
✅ Document Processing: PASS - document-uuid
✅ Frontend Access: PASS - DT Commercial Roofing
✅ Flower Monitoring: PASS - Flower UI accessible
✅ Processing Progress: PASS - Final status: COMPLETED
============================================================
📊 SUMMARY: 8 passed, 0 failed, 0 errors/warnings
============================================================
🎉 ALL TESTS PASSED! Upload pipeline is working perfectly!
```

### Troubleshooting

#### Common Issues

1. **Containers not running**

   ```bash
   docker-compose --profile local up -d
   ```

2. **Test file not found**
   - Ensure `tests/mcdonalds collection/small_set.pdf` exists

3. **Dependencies missing**

   ```bash
   pip install -r test_requirements.txt
   ```

4. **Chrome/Selenium issues**
   - Install Chrome browser
   - Update ChromeDriver if needed

#### Debug Mode

Run tests with verbose output:

```bash
python test_upload_simple.py 2>&1 | tee test_output.log
```

## 🎯 Test Scenarios

### Scenario 1: Complete Upload Pipeline

1. Generate secure upload URL
2. Upload 24MB PDF to Google Cloud Storage
3. Start document processing
4. Monitor processing progress
5. Verify completion

### Scenario 2: System Health Check

1. Verify API health
2. Check database connectivity
3. Test frontend accessibility
4. Validate monitoring interfaces

### Scenario 3: Error Handling

1. Test with invalid file types
2. Test with oversized files
3. Test with network interruptions
4. Verify error recovery

## 🔍 Monitoring and Debugging

### Real-time Monitoring

- **Flower UI**: `http://localhost:5555` - Task monitoring
- **API Docs**: `http://localhost:3001/docs` - API testing
- **Frontend**: `http://localhost:3000` - Web interface

### Log Analysis

```bash
# API logs
docker logs brant-api-local --tail 50

# Worker logs
docker logs brant-worker-local --tail 50

# Database logs
docker logs brant-postgres-local --tail 50
```

### Database Queries

```bash
# Check document status
docker exec brant-postgres-local psql -U brant_user -d brant_roofing \
  -c "SELECT id, filename, processing_status, created_at FROM documents \
      ORDER BY created_at DESC LIMIT 5;"

# Check processing results
docker exec brant-postgres-local psql -U brant_user -d brant_roofing \
  -c "SELECT * FROM processing_results ORDER BY created_at DESC LIMIT 3;"
```

## 🚀 Continuous Integration

### GitHub Actions Example

```yaml
name: Upload Pipeline Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Start services
        run: docker-compose --profile local up -d
      - name: Wait for services
        run: sleep 30
      - name: Run tests
        run: python test_upload_simple.py
      - name: Cleanup
        run: docker-compose down
```

## 📈 Performance Metrics

### Expected Performance

- **Upload Speed**: ~5MB/second to GCS
- **Processing Start**: < 2 seconds
- **PDF Chunking**: < 1 second for 24MB
- **API Response**: < 200ms
- **Database Queries**: < 100ms

### Load Testing

For load testing, run multiple instances:

```bash
# Run 5 concurrent tests
for i in {1..5}; do
  python test_upload_simple.py &
done
wait
```

## 🎉 Success Criteria

A successful test run should demonstrate:

- ✅ All API endpoints responding correctly
- ✅ File upload to Google Cloud Storage
- ✅ Document processing pipeline activation
- ✅ Real-time status monitoring
- ✅ Database persistence
- ✅ Error handling and recovery
- ✅ System integration and scalability

---

**🎯 The Brant Roofing System upload pipeline is fully tested and production-ready!**
