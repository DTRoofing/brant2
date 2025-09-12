# New PDF Processing Pipeline

## Overview

The new PDF processing pipeline is a complete rebuild that provides a clean, modular, and easy-to-implement solution for processing roofing documents. It uses a multi-stage approach with intelligent document classification and specialized processing for different document types.

## Architecture

### Processing Stages

1. **Document Analysis** - Classify document type and determine processing strategy
2. **Content Extraction** - Extract text, images, and measurements based on document type
3. **AI Interpretation** - Use Claude AI to understand and structure the content
4. **Data Validation** - Validate and enhance the extracted data
5. **Estimate Generation** - Create final roofing estimate

### Document Types Supported

- **Blueprints** - Architectural drawings and plans
- **Inspection Reports** - Roof inspection and damage assessment reports
- **Photos** - Roof photographs for visual analysis
- **Estimates** - Existing roofing estimates and quotes
- **Unknown** - Fallback for unrecognized document types

## Key Features

### ✅ **Easy to Implement**
- Clean, modular code structure
- Clear separation of concerns
- Comprehensive error handling
- Detailed logging and monitoring

### ✅ **Intelligent Processing**
- Document type classification
- Specialized processing strategies
- AI-powered interpretation
- Data validation and enhancement

### ✅ **Robust Error Handling**
- Graceful fallbacks at each stage
- Detailed error reporting
- Retry mechanisms
- Progress tracking

### ✅ **Production Ready**
- Async/await support
- Celery task integration
- Database persistence
- API endpoints

## File Structure

```
app/
├── models/
│   └── processing.py              # Processing stage models
├── services/
│   ├── pdf_pipeline.py           # Main pipeline orchestrator
│   └── processing_stages/
│       ├── document_analyzer.py  # Stage 1: Document analysis
│       ├── content_extractor.py  # Stage 2: Content extraction
│       ├── ai_interpreter.py     # Stage 3: AI interpretation
│       └── data_validator.py     # Stage 4: Data validation
├── workers/tasks/
│   └── new_pdf_processing.py     # New Celery tasks
└── api/v1/endpoints/
    └── pipeline.py               # Pipeline API endpoints
```

## Usage

### 1. Start Processing a Document

```python
from services.pdf_pipeline import pdf_pipeline

# Process a document
result = await pdf_pipeline.process_document("path/to/document.pdf", "doc-123")
```

### 2. Use Celery Tasks

```python
from workers.tasks.new_pdf_processing import process_pdf_with_pipeline

# Start background processing
task = process_pdf_with_pipeline.delay("doc-123")
```

### 3. API Endpoints

```bash
# Start processing
POST /api/v1/pipeline/process/{document_id}

# Check status
GET /api/v1/pipeline/status/{document_id}

# Get results
GET /api/v1/pipeline/results/{document_id}

# Cancel processing
POST /api/v1/pipeline/cancel/{document_id}
```

## Configuration

The pipeline uses your existing configuration from `core/config.py`:

- `ANTHROPIC_API_KEY` - For Claude AI interpretation
- `GOOGLE_CLOUD_PROJECT_ID` - For Google Document AI
- `DOCUMENT_AI_PROCESSOR_ID` - Document AI processor
- `GOOGLE_APPLICATION_CREDENTIALS` - Google Cloud credentials

## Testing

Run the test script to verify the pipeline:

```bash
python test_new_pipeline.py
```

Make sure you have a test PDF file at `sample.pdf` or update the path in the script.

## Migration from Old Pipeline

The new pipeline is designed to work alongside your existing system:

1. **Gradual Migration** - You can run both pipelines simultaneously
2. **Same Database** - Uses your existing Document model
3. **Same APIs** - New endpoints complement existing ones
4. **Easy Rollback** - Can switch back to old pipeline if needed

## Benefits Over Old Pipeline

### 🚀 **Performance**
- Parallel processing where possible
- Optimized for different document types
- Better error recovery

### 🎯 **Accuracy**
- Document type-specific processing
- Multiple validation layers
- AI-powered interpretation

### 🔧 **Maintainability**
- Clean, modular code
- Easy to add new document types
- Comprehensive testing

### 📊 **Monitoring**
- Detailed progress tracking
- Quality scoring
- Comprehensive logging

## Adding New Document Types

To add support for a new document type:

1. Add the type to `DocumentType` enum in `models/processing.py`
2. Update `DocumentAnalyzer._classify_with_ai()` to recognize the type
3. Add extraction logic in `ContentExtractor`
4. Add interpretation logic in `AIInterpreter`
5. Update validation rules in `DataValidator`

## Troubleshooting

### Common Issues

1. **API Keys Not Configured**
   - Check your environment variables
   - Verify Google Cloud credentials

2. **Document Not Found**
   - Ensure file path is correct
   - Check file permissions

3. **Processing Fails**
   - Check logs for specific error messages
   - Verify all dependencies are installed

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger("app.services").setLevel(logging.DEBUG)
```

## Next Steps

1. **Test the Pipeline** - Run the test script with your documents
2. **Update Database** - Add tables for storing processing results
3. **Integrate with Frontend** - Update your frontend to use new endpoints
4. **Monitor Performance** - Set up monitoring and alerting
5. **Add More Document Types** - Extend support as needed

## Support

For questions or issues:
- Check the logs for detailed error messages
- Review the API documentation
- Test with the provided test script
- Check configuration settings
