# .cursor/rules/brant-roofing-system.mdc

rule "fastapi-pydantic-schemas" {
  description = "Enforce proper Pydantic schema patterns for FastAPI"
  when = "creating or modifying API request/response models"
  then = "Use Pydantic BaseModel with:
- Field validation with description
- from_attributes = True for SQLAlchemy compatibility
- Proper type hints with Union types for optional fields
- Custom validators using @validator decorator
- JSON encoders for datetime objects

Example:
class DocumentResponse(BaseModel):
    id: str = Field(..., description='Document UUID')
    status: Literal['pending', 'processing', 'completed', 'failed']
    confidence_score: float = Field(..., ge=0, le=1)
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}"
}

rule "domain-driven-design" {
  description = "Implement domain-driven design patterns"
  when = "creating business logic or domain entities"
  then = "Create rich domain entities with:
- Business logic methods within entities
- Value objects for complex data types
- Repository interfaces in domain layer
- Domain services for complex operations
- Immutable data structures where appropriate

Example:
@dataclass
class RoofingProject:
    measurements: List[Measurement]
    
    def total_area(self) -> Decimal:
        return sum(m.area_sf for m in self.measurements)
    
    def estimate_cost(self, rate_per_sf: Decimal) -> Decimal:
        return self.total_area * rate_per_sf * Decimal('1.5')"
}

rule "ai-service-integration" {
  description = "Standardize AI service integration patterns"
  when = "integrating with Google Document AI or Anthropic Claude"
  then = "Follow these patterns:
- Always include confidence scores in responses
- Implement proper retry logic with exponential backoff
- Handle quota limits and service unavailability gracefully
- Store raw AI responses for debugging
- Use structured prompts for consistent outputs
- Validate AI responses before processing

Example:
class DocumentAIService:
    async def process_document(self, file_path: str) -> Dict:
        try:
            result = self.client.process_document(request)
            return {
                'text': result.document.text,
                'confidence_scores': {...},
                'entities': [...]
            }
        except Exception as e:
            if 'quota' in str(e).lower():
                raise ServiceUnavailableError('Document AI quota exceeded')
            raise ProcessingError(f'Processing failed: {str(e)}')"
}

rule "structured-error-handling" {
  description = "Implement comprehensive error handling patterns"
  when = "handling errors or exceptions"
  then = "Use custom exception hierarchy:
- Create domain-specific exceptions
- Map business exceptions to HTTP status codes
- Include error context and correlation IDs
- Log errors with structured data
- Provide meaningful error messages to users

Example:
class RoofingSystemException(Exception):
    def __init__(self, message: str, details: Optional[Dict] = None):
        self.message = message
        self.details = details or {}

def map_exception_to_http(exc: Exception) -> HTTPException:
    mapping = {
        ValidationError: status.HTTP_400_BAD_REQUEST,
        ProcessingError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    }
    return HTTPException(
        status_code=mapping.get(type(exc), 500),
        detail={'error_type': type(exc).__name__, 'message': str(exc)}
    )"
}

rule "celery-background-tasks" {
  description = "Implement robust Celery background task patterns"
  when = "creating or modifying Celery tasks"
  then = "Follow these patterns:
- Use bind=True for task instance access
- Implement progress tracking with update_state
- Handle retries with exponential backoff
- Include proper error handling and logging
- Update database status throughout processing

Example:
@celery_app.task(bind=True, max_retries=3)
def process_document_task(self, document_id: str):
    try:
        self.update_state(
            state='PROGRESS',
            meta={'progress': 0.2, 'stage': 'Starting Document AI'}
        )
        # Process document...
    except Exception as e:
        if self.request.retries < self.max_retries:
            countdown = 60 * (2 ** self.request.retries)
            raise self.retry(countdown=countdown, exc=e)
        raise"
}

rule "structured-logging" {
  description = "Implement structured logging with correlation IDs"
  when = "adding logging to the application"
  then = "Use structured logging patterns:
- Include correlation IDs for request tracing
- Log business events with structured data
- Use consistent log levels and formats
- Include context information in logs
- Monitor performance metrics

Example:
logger = structlog.get_logger(__name__)

def log_document_uploaded(document_id: str, filename: str):
    logger.info(
        'Document uploaded',
        event_type='document_uploaded',
        document_id=document_id,
        filename=filename,
        correlation_id=correlation_id.get()
    )"
}

rule "database-optimization" {
  description = "Optimize database queries and connections"
  when = "writing database queries or configurations"
  then = "Follow database best practices:
- Use eager loading for related objects
- Implement proper connection pooling
- Use async sessions correctly
- Add database indexes for query performance
- Use repository pattern for data access

Example:
# Optimized query with eager loading
stmt = (
    select(Project)
    .options(selectinload(Project.measurements))
    .where(Project.id == project_id)
)

# Proper session management
@asynccontextmanager
async def get_db_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise"
}

rule "security-validation" {
  description = "Implement comprehensive security validation"
  when = "handling user inputs or file uploads"
  then = "Apply security measures:
- Validate and sanitize all inputs
- Check file types and sizes
- Implement rate limiting
- Use secure filename patterns
- Validate file content not just extensions

Example:
class SecurityValidator:
    @classmethod
    def validate_filename(cls, filename: str) -> str:
        # Remove path traversal attempts
        filename = filename.replace('..', '').replace('/', '')
        
        if not cls.SAFE_FILENAME_PATTERN.match(filename):
            raise HTTPException(400, 'Invalid filename')
        return filename

@limiter.limit('10/minute')
async def upload_document(...):"
}

rule "typescript-api-integration" {
  description = "Create type-safe frontend API integration"
  when = "writing TypeScript frontend code for API integration"
  then = "Use these patterns:
- Generate TypeScript types from OpenAPI schema
- Create type-safe API client classes
- Use React Query for server state management
- Implement proper error boundaries
- Handle loading and error states

Example:
// Type-safe API client
class DocumentsAPI {
  static async upload(file: File): Promise<DocumentResponse> {
    const response = await apiClient.post<DocumentResponse>(
      '/documents/upload',
      formData
    );
    return response.data;
  }
}

// React Query hook
export function useDocumentUpload() {
  return useMutation({
    mutationFn: DocumentsAPI.upload,
    onSuccess: (data) => {
      queryClient.invalidateQueries(['documents']);
    }
  });
}"
}

rule "comprehensive-testing" {
  description = "Implement comprehensive testing strategy"
  when = "writing tests for any component"
  then = "Follow testing pyramid:
- Unit tests for domain logic and pure functions
- Integration tests for AI services and database
- API tests for endpoints
- Use pytest fixtures for test data
- Mock external services properly
- Maintain high test coverage

Example:
class TestRoofingProject:
    def test_total_area_calculation(self):
        measurements = [
            Measurement(area_sf=Decimal('500'), confidence_score=0.9),
            Measurement(area_sf=Decimal('200'), confidence_score=0.85)
        ]
        project = RoofingProject(measurements=measurements)
        assert project.total_area == Decimal('700')

@pytest.mark.integration
async def test_document_ai_processing(mock_document_ai):
    # Integration test with mocked AI service"
}

rule "performance-optimization" {
  description = "Implement performance optimization patterns"
  when = "dealing with expensive operations or frequent queries"
  then = "Apply performance optimizations:
- Use caching for expensive calculations
- Implement connection pooling
- Use background tasks for heavy processing
- Optimize database queries
- Add performance monitoring

Example:
@cached(ttl=3600, key_prefix='project_cost')
async def calculate_project_cost(project_id: str) -> dict:
    # Expensive calculation with caching
    return cost_data

# Database connection pooling
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)"
}