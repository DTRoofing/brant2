@echo off
REM =============================================================================
REM Brant Roofing System - COMPLETE Cursor Rules Setup Script (Windows)
REM =============================================================================

echo 🏠 Setting up COMPLETE Cursor Rules for Brant Roofing System...
echo ================================================================

REM Create directory structure
echo 📁 Creating directory structure...
if not exist ".cursor" mkdir ".cursor"
if not exist ".cursor\rules" mkdir ".cursor\rules"
if not exist ".cursor\rules\fastapi" mkdir ".cursor\rules\fastapi"
if not exist ".cursor\rules\ai-services" mkdir ".cursor\rules\ai-services"
if not exist ".cursor\rules\database" mkdir ".cursor\rules\database"
if not exist ".cursor\rules\frontend" mkdir ".cursor\rules\frontend"
if not exist ".cursor\rules\testing" mkdir ".cursor\rules\testing"
if not exist ".cursor\rules\security" mkdir ".cursor\rules\security"

echo ✅ Directory structure created!

REM ============================================================================
REM 1. MAIN PROJECT RULES
REM ============================================================================
echo 📝 Creating main project rules...
(
echo rule "project-structure" {
echo   description = "Maintain proper project structure for Brant Roofing System"
echo   when = "organizing code files and directories"
echo   then = "Follow this structure:
echo - app/ for Python FastAPI backend
echo - app/domain/ for business entities
echo - app/models/ for SQLAlchemy models  
echo - app/schemas/ for Pydantic models
echo - app/api/v1/endpoints/ for API endpoints
echo - app/services/ for AI service integrations
echo - app/workers/ for Celery background tasks
echo - frontend/ for Next.js TypeScript frontend
echo - tests/ for all test files"
echo }
echo.
echo rule "naming-conventions" {
echo   description = "Use consistent naming conventions"
echo   when = "naming files, functions, classes, or variables"
echo   then = "Follow these conventions:
echo - snake_case for Python functions and variables
echo - PascalCase for Python classes
echo - camelCase for TypeScript/JavaScript
echo - kebab-case for file names and URLs
echo - UPPER_CASE for constants
echo - Descriptive names that reflect business domain"
echo }
) > ".cursor\rules\brant-roofing-system.mdc"

REM ============================================================================
REM 2. FASTAPI RULES
REM ============================================================================
echo 📝 Creating FastAPI rules...

REM API Design Rules
(
echo rule "fastapi-endpoint-structure" {
echo   description = "Standardize FastAPI endpoint patterns"
echo   when = "creating API endpoints"
echo   then = "Use consistent patterns:
echo - Include response_model in decorator
echo - Use Depends^(^) for dependency injection
echo - Include proper HTTP status codes
echo - Add comprehensive docstrings
echo - Use appropriate HTTP methods
echo.
echo Example:
echo @router.post^('/upload', response_model=DocumentResponse^)
echo async def upload_document^(
echo     file: UploadFile = File^(...^),
echo     db: Session = Depends^(get_db^)
echo ^) -^> DocumentResponse:
echo     '''Upload a PDF blueprint for processing.'''
echo     # Implementation"
echo }
echo.
echo rule "pydantic-validation" {
echo   description = "Use comprehensive Pydantic validation"
echo   when = "creating request/response models"
echo   then = "Include proper validation:
echo - Field descriptions for API documentation
echo - Validation constraints ^(ge, le, regex^)
echo - Custom validators for business rules
echo - from_attributes = True for SQLAlchemy
echo - JSON encoders for special types
echo.
echo Example:
echo class DocumentResponse^(BaseModel^):
echo     id: str = Field^(..., description='Document UUID'^)
echo     status: Literal^['pending', 'processing', 'completed', 'failed'^]
echo     confidence_score: float = Field^(..., ge=0, le=1^)
echo     
echo     class Config:
echo         from_attributes = True"
echo }
) > ".cursor\rules\fastapi\api-design.mdc"

REM Error Handling Rules
(
echo rule "error-handling-patterns" {
echo   description = "Implement comprehensive error handling"
echo   when = "handling errors or exceptions"
echo   then = "Use custom exception hierarchy:
echo - Create domain-specific exceptions
echo - Map business exceptions to HTTP status codes
echo - Include error context and correlation IDs
echo - Log errors with structured data
echo - Provide meaningful error messages
echo.
echo Example:
echo class RoofingSystemException^(Exception^):
echo     def __init__^(self, message: str, details: Optional^[Dict^] = None^):
echo         self.message = message
echo         self.details = details or {}
echo.
echo def map_exception_to_http^(exc: Exception^) -^> HTTPException:
echo     mapping = {
echo         ValidationError: status.HTTP_400_BAD_REQUEST,
echo         ProcessingError: status.HTTP_422_UNPROCESSABLE_ENTITY,
echo     }
echo     return HTTPException^(
echo         status_code=mapping.get^(type^(exc^), 500^),
echo         detail={'error_type': type^(exc^).__name__, 'message': str^(exc^)}
echo     ^)"
echo }
) > ".cursor\rules\fastapi\error-handling.mdc"

REM ============================================================================
REM 3. AI SERVICES RULES
REM ============================================================================
echo 📝 Creating AI service integration rules...

REM Document AI Rules
(
echo rule "document-ai-integration" {
echo   description = "Google Document AI integration patterns"
echo   when = "integrating with Google Document AI"
echo   then = "Follow these patterns:
echo - Handle quota limits gracefully
echo - Include confidence scores in all responses
echo - Store raw responses for debugging
echo - Implement proper retry logic
echo - Validate extracted entities
echo.
echo Example:
echo class DocumentAIService:
echo     async def process_document^(self, file_path: str^):
echo         try:
echo             result = self.client.process_document^(request^)
echo             return self._extract_structured_data^(result^)
echo         except Exception as e:
echo             if 'quota' in str^(e^).lower^(^):
echo                 raise ServiceUnavailableError^('Quota exceeded'^)
echo             raise ProcessingError^(f'Processing failed: {e}'^)"
echo }
) > ".cursor\rules\ai-services\document-ai.mdc"

REM Claude Integration Rules
(
echo rule "claude-integration-patterns" {
echo   description = "Anthropic Claude integration best practices"
echo   when = "integrating with Anthropic Claude API"
echo   then = "Use these patterns:
echo - Structure prompts for consistent outputs
echo - Include measurement validation
echo - Handle rate limits with backoff
echo - Cache expensive analysis results
echo - Parse structured responses safely
echo.
echo Example:
echo class ClaudeService:
echo     async def analyze_measurements^(self, text: str^) -^> Dict:
echo         prompt = f'''
echo         Analyze this blueprint text for roof measurements:
echo         {text}
echo         
echo         Return JSON with: area_sf, confidence, coordinates
echo         '''
echo         
echo         response = await self.client.messages.create^(
echo             model='claude-3-sonnet-20240229',
echo             messages=^[{'role': 'user', 'content': prompt}^]
echo         ^)
echo         return self._parse_response^(response^)"
echo }
) > ".cursor\rules\ai-services\claude-integration.mdc"

REM Background Tasks Rules
(
echo rule "celery-task-patterns" {
echo   description = "Robust Celery background task implementation"
echo   when = "creating Celery background tasks"
echo   then = "Follow these patterns:
echo - Use bind=True for task instance access
echo - Implement progress tracking with update_state
echo - Handle retries with exponential backoff
echo - Include proper error handling and logging
echo - Update database status throughout processing
echo.
echo Example:
echo @celery_app.task^(bind=True, max_retries=3^)
echo def process_document_task^(self, document_id: str^):
echo     try:
echo         self.update_state^(
echo             state='PROGRESS',
echo             meta={'progress': 0.2, 'stage': 'Starting Document AI'}
echo         ^)
echo         # Process document...
echo     except Exception as e:
echo         if self.request.retries ^< self.max_retries:
echo             countdown = 60 * ^(2 ** self.request.retries^)
echo             raise self.retry^(countdown=countdown, exc=e^)
echo         raise"
echo }
) > ".cursor\rules\ai-services\background-tasks.mdc"

REM ============================================================================
REM 4. DATABASE RULES
REM ============================================================================
echo 📝 Creating database optimization rules...

REM SQLAlchemy Patterns
(
echo rule "sqlalchemy-patterns" {
echo   description = "SQLAlchemy best practices and patterns"
echo   when = "working with database models and queries"
echo   then = "Follow these patterns:
echo - Use async sessions correctly
echo - Implement eager loading for related objects
echo - Create repository patterns for data access
echo - Use proper transaction management
echo - Add database indexes for performance
echo.
echo Example:
echo # Optimized query with eager loading
echo stmt = ^(
echo     select^(Project^)
echo     .options^(selectinload^(Project.measurements^)^)
echo     .where^(Project.id == project_id^)
echo ^)
echo.
echo # Proper session management
echo @asynccontextmanager
echo async def get_db_session^(^):
echo     async with AsyncSessionLocal^(^) as session:
echo         try:
echo             yield session
echo             await session.commit^(^)
echo         except Exception:
echo             await session.rollback^(^)
echo             raise"
echo }
) > ".cursor\rules\database\sqlalchemy-patterns.mdc"

REM Performance Rules
(
echo rule "database-performance" {
echo   description = "Database performance optimization"
echo   when = "optimizing database queries and connections"
echo   then = "Apply these optimizations:
echo - Use connection pooling with proper sizing
echo - Implement query result caching
echo - Use database indexes strategically
echo - Optimize N+1 query problems
echo - Monitor query performance
echo.
echo Example:
echo # Connection pooling configuration
echo engine = create_async_engine^(
echo     DATABASE_URL,
echo     pool_size=20,
echo     max_overflow=30,
echo     pool_pre_ping=True,
echo     pool_recycle=3600
echo ^)
echo.
echo # Query optimization with caching
echo @cached^(ttl=3600^)
echo async def get_project_measurements^(project_id: str^):
echo     # Cached expensive query"
echo }
) > ".cursor\rules\database\performance.mdc"

REM ============================================================================
REM 5. FRONTEND RULES
REM ============================================================================
echo 📝 Creating frontend integration rules...

REM TypeScript API Rules
(
echo rule "typescript-api-client" {
echo   description = "Type-safe API client implementation"
echo   when = "creating frontend API integration"
echo   then = "Use these patterns:
echo - Generate TypeScript types from OpenAPI
echo - Create type-safe API client classes
echo - Implement proper error handling
echo - Use correlation IDs for tracing
echo - Handle authentication tokens
echo.
echo Example:
echo interface DocumentResponse {
echo   id: string;
echo   status: 'pending' ^| 'processing' ^| 'completed' ^| 'failed';
echo   confidence_score: number;
echo }
echo.
echo class DocumentsAPI {
echo   static async upload^(file: File^): Promise^<DocumentResponse^> {
echo     const response = await apiClient.post^<DocumentResponse^>^(
echo       '/documents/upload',
echo       formData
echo     ^);
echo     return response.data;
echo   }
echo }"
echo }
) > ".cursor\rules\frontend\typescript-api.mdc"

REM React Patterns Rules
(
echo rule "react-query-patterns" {
echo   description = "React Query integration for server state"
echo   when = "managing server state in React components"
echo   then = "Use React Query patterns:
echo - Create custom hooks for API operations
echo - Implement proper caching strategies
echo - Handle loading and error states
echo - Use optimistic updates where appropriate
echo - Implement real-time updates for processing status
echo.
echo Example:
echo export function useDocumentUpload^(^) {
echo   const queryClient = useQueryClient^(^);
echo   
echo   return useMutation^({
echo     mutationFn: DocumentsAPI.upload,
echo     onSuccess: ^(data^) =^> {
echo       queryClient.invalidateQueries^(^['documents'^]^);
echo       toast.success^(`Document uploaded successfully`^);
echo     },
echo     onError: ^(error^) =^> {
echo       toast.error^(error.message^);
echo     }
echo   }^);
echo }"
echo }
) > ".cursor\rules\frontend\react-patterns.mdc"

REM ============================================================================
REM 6. TESTING RULES
REM ============================================================================
echo 📝 Creating testing strategy rules...

REM Unit Testing Rules
(
echo rule "unit-testing-patterns" {
echo   description = "Unit testing for domain logic"
echo   when = "writing unit tests for business logic"
echo   then = "Create comprehensive unit tests:
echo - Test all business logic methods
echo - Use descriptive test names
echo - Follow AAA pattern ^(Arrange, Act, Assert^)
echo - Test edge cases and error conditions
echo - Use pytest fixtures for test data
echo.
echo Example:
echo class TestRoofingProject:
echo     def test_estimate_cost_with_valid_measurements^(self^):
echo         # Arrange
echo         measurements = ^[Measurement^(area_sf=Decimal^('1000'^), confidence=0.9^)^]
echo         project = RoofingProject^(measurements=measurements^)
echo         
echo         # Act
echo         cost = project.estimate_cost^(Decimal^('5.50'^)^)
echo         
echo         # Assert
echo         assert cost == Decimal^('8250.00'^)"
echo }
) > ".cursor\rules\testing\unit-tests.mdc"

REM Integration Testing Rules
(
echo rule "integration-testing" {
echo   description = "Integration testing for AI services and database"
echo   when = "testing integration between components"
echo   then = "Create integration tests that:
echo - Test AI service integrations with mocks
echo - Test database operations with test database
echo - Test complete workflows end-to-end
echo - Use proper setup and teardown
echo - Mock external dependencies appropriately
echo.
echo Example:
echo @pytest.mark.integration
echo async def test_document_processing_pipeline^(
echo     mock_document_ai, db_session
echo ^):
echo     # Setup test document
echo     document = Document^(filename='test.pdf'^)
echo     db_session.add^(document^)
echo     await db_session.commit^(^)
echo     
echo     # Process document
echo     result = await process_document_task^(str^(document.id^)^)
echo     
echo     # Verify results
echo     assert result^['status'^] == 'completed'"
echo }
) > ".cursor\rules\testing\integration-tests.mdc"

REM ============================================================================
REM 7. SECURITY RULES
REM ============================================================================
echo 📝 Creating security validation rules...

REM Input Validation Rules
(
echo rule "input-validation" {
echo   description = "Comprehensive input validation and sanitization"
echo   when = "handling user inputs or file uploads"
echo   then = "Apply security validation:
echo - Validate file types using content detection
echo - Sanitize filenames to prevent path traversal
echo - Implement rate limiting on endpoints
echo - Validate file sizes before processing
echo - Use Pydantic validators for data validation
echo.
echo Example:
echo class SecurityValidator:
echo     @classmethod
echo     def validate_upload^(cls, file: UploadFile^) -^> None:
echo         cls._validate_file_type^(file^)
echo         cls._validate_file_size^(file^)
echo         cls._validate_filename^(file.filename^)
echo         
echo     @classmethod
echo     def _validate_file_type^(cls, file: UploadFile^) -^> None:
echo         if not file.content_type == 'application/pdf':
echo             raise ValidationError^('Only PDF files allowed'^)"
echo }
) > ".cursor\rules\security\input-validation.mdc"

REM File Security Rules
(
echo rule "file-security" {
echo   description = "Secure file handling practices"
echo   when = "processing uploaded files"
echo   then = "Implement secure file handling:
echo - Scan file content, not just extensions
echo - Use secure temporary file storage
echo - Implement virus scanning if possible
echo - Limit file processing resources
echo - Clean up temporary files properly
echo.
echo Example:
echo class SecureFileHandler:
echo     @staticmethod
echo     def validate_pdf_content^(file_content: bytes^) -^> bool:
echo         # Check PDF magic bytes
echo         if not file_content.startswith^(b'%%PDF'^):
echo             raise ValidationError^('Invalid PDF file'^)
echo         
echo         # Additional content validation
echo         return True
echo     
echo     @staticmethod
echo     def create_secure_temp_file^(^) -^> str:
echo         temp_dir = tempfile.mkdtemp^(prefix='roofing_'^)
echo         return temp_dir"
echo }
) > ".cursor\rules\security\file-security.mdc"

echo.
echo 🎉 COMPLETE Cursor Rules setup finished!
echo ========================================
echo.
echo 📁 Created complete structure with 14 rule files:
echo   .cursor\rules\
echo   ├── brant-roofing-system.mdc      ^(main project rules^)
echo   ├── fastapi\
echo   │   ├── api-design.mdc            ^(API patterns^)
echo   │   └── error-handling.mdc        ^(error management^)
echo   ├── ai-services\
echo   │   ├── document-ai.mdc           ^(Google Document AI^)
echo   │   ├── claude-integration.mdc    ^(Anthropic Claude^)
echo   │   └── background-tasks.mdc      ^(Celery workers^)
echo   ├── database\
echo   │   ├── sqlalchemy-patterns.mdc   ^(DB best practices^)
echo   │   └── performance.mdc           ^(query optimization^)
echo   ├── frontend\
echo   │   ├── typescript-api.mdc        ^(API integration^)
echo   │   └── react-patterns.mdc        ^(React Query^)
echo   ├── testing\
echo   │   ├── unit-tests.mdc           ^(unit testing^)
echo   │   └── integration-tests.mdc    ^(integration testing^)
echo   └── security\
echo       ├── input-validation.mdc     ^(security validation^)
echo       └── file-security.mdc        ^(file handling^)
echo.
echo 🚀 Next steps:
echo   1. Open your project in Cursor IDE
echo   2. Test the rules: /rules test-all
echo   3. Monitor rule usage: /rules monitor
echo   4. Start coding with elite patterns!
echo.
echo ✅ Your Brant Roofing System now has COMPLETE elite development patterns!

pause