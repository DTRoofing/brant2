# Security Audit Fix Plan

## Priority Classification
- 🔴 **CRITICAL**: Immediate fix required (Issues 1, 2, 3)
- 🟠 **HIGH**: Fix within 24 hours (Issues 4, 5, 7, 8)
- 🟡 **MEDIUM**: Fix within week (Issues 6, 11, 12, 13, 14, 15, 16)
- 🟢 **LOW**: Fix in next sprint (Issues 9, 10, 17)

## 🔴 CRITICAL SECURITY FIXES

### 1. CORS Wildcard Configuration
**File**: `app/main.py:25`
**Current Issue**: `allow_origins=["*"]` allows any origin

**Fix**:
```python
# app/main.py
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://your-production-domain.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if not settings.DEBUG else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### 2. Credentials Exposed in Environment
**File**: `.env`
**Current Issue**: Plaintext credentials in version control

**Fix**:
1. Remove `.env` from git tracking
2. Use `.env.example` with placeholder values
3. Implement secret management (Google Secret Manager)
4. Rotate all exposed credentials immediately

```bash
# .env.example
CLAUDE_API_KEY=your-api-key-here
DATABASE_URL=postgresql://user:pass@host:port/db?sslmode=require
```

### 3. File Upload Validation Bypass
**File**: `app/api/v1/endpoints/uploads.py:19`
**Current Issue**: Only validates MIME type header

**Fix**:
```python
import magic
from pathlib import Path

async def validate_pdf_file(file_path: Path) -> bool:
    """Validate file is actually a PDF using magic bytes"""
    try:
        # Check magic bytes
        with open(file_path, 'rb') as f:
            header = f.read(5)
            if header != b'%PDF-':
                return False
        
        # Use python-magic for deeper validation
        mime = magic.from_file(str(file_path), mime=True)
        return mime == 'application/pdf'
    except Exception:
        return False

# In upload endpoint
if not await validate_pdf_file(file_path):
    file_path.unlink(missing_ok=True)
    raise HTTPException(
        status_code=415,
        detail="Invalid PDF file"
    )
```

## 🟠 HIGH PRIORITY FIXES

### 4. Race Condition in Document Status Updates
**File**: `app/api/v1/endpoints/pipeline.py:72-85`

**Fix**:
```python
async with db.begin():
    # Use SELECT FOR UPDATE to lock the row
    stmt = select(Document).where(
        Document.id == doc_uuid
    ).with_for_update()
    result = await db.execute(stmt)
    document = result.scalar_one_or_none()
    
    if document.processing_status == ProcessingStatus.PROCESSING:
        raise HTTPException(400, "Already processing")
    
    document.processing_status = ProcessingStatus.PROCESSING
    # Commit happens automatically with context manager
    
# Queue task after successful status update
task = process_pdf_with_pipeline.delay(str(document_id))
```

### 5. Async/Sync Database Mixing
**File**: `app/workers/tasks/new_pdf_processing.py:25-26`

**Fix**:
```python
# Use sync operations consistently in Celery tasks
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Keep sync for Celery workers
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
```

### 7. Unhandled Database Exceptions
**File**: `app/api/v1/endpoints/pipeline.py:133-139`

**Fix**:
```python
from sqlalchemy.exc import SQLAlchemyError

try:
    results_result = await db.execute(results_stmt)
    processing_results = results_result.scalar_one_or_none()
except SQLAlchemyError as e:
    logger.error(f"Database error: {e}")
    raise HTTPException(
        status_code=503,
        detail="Database temporarily unavailable"
    )
```

### 8. File System Error Handling
**File**: `app/workers/tasks/new_pdf_processing.py:85-87`

**Fix**:
```python
try:
    file_path = Path(file_path_str)
    if not file_path.exists():
        raise FileNotFoundError(f"PDF not found: {file_path}")
    if not file_path.is_file():
        raise ValueError(f"Not a file: {file_path}")
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"Cannot read: {file_path}")
except (FileNotFoundError, PermissionError, ValueError) as e:
    logger.error(f"File access error: {e}")
    raise self.retry(exc=e, countdown=60)
```

## 🟡 MEDIUM PRIORITY FIXES

### 6. Memory Leak in File Streaming
**Fix**:
```python
async def upload_with_cleanup(file, file_path, max_size):
    try:
        async with aiofiles.open(file_path, "wb") as out_file:
            # Stream with proper cleanup
            total_size = 0
            async for chunk in file.stream(chunk_size=1024*1024):
                total_size += len(chunk)
                if total_size > max_size:
                    raise ValueError("File too large")
                await out_file.write(chunk)
    except Exception as e:
        # Ensure cleanup on error
        if file_path.exists():
            file_path.unlink(missing_ok=True)
        raise
    finally:
        # Reset file pointer if needed
        if hasattr(file, 'seek'):
            await file.seek(0)
```

### 11. Frontend Dependency Conflicts
**Fix**: Remove unused framework dependencies from package.json

### 12. TypeScript Errors
**Fix**: Enable TypeScript checking:
```javascript
// next.config.mjs
typescript: {
  ignoreBuildErrors: false,
}
```

### 13. Docker Volume Mounting
**Fix**:
```yaml
# docker-compose.yml
volumes:
  - ./app:/app  # Correct path
```

### 14. Unbounded Queries
**Fix**:
```python
result = await db.execute(
    select(
        Document.processing_status,
        func.count(Document.id).label('count')
    ).group_by(Document.processing_status)
    .limit(100)  # Add reasonable limit
)
```

### 15. Missing Database Indexes
**Fix**:
```python
# app/models/core.py
class Document(Base):
    __tablename__ = "documents"
    
    processing_status = Column(
        Enum(ProcessingStatus),
        default=ProcessingStatus.PENDING,
        index=True  # Add index
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        index=True  # Add index
    )
```

### 16. Missing CANCELLED Status
**Fix**:
```python
# app/models/core.py
class ProcessingStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"  # Add missing status
```

## 🟢 LOW PRIORITY FIXES

### 9. Database Constraints
**Fix**:
```python
file_size = Column(
    Float,
    CheckConstraint('file_size > 0 AND file_size < 104857600'),  # 100MB max
    nullable=False
)
```

### 10. UUID Collision Check
**Fix**: UUID4 collisions are astronomically rare (not needed)

### 17. Hardcoded Timestamp
**Fix**:
```python
"timestamp": datetime.utcnow().isoformat()
```

## Implementation Priority Order

1. **Immediate (Now)**:
   - Remove .env from git
   - Fix CORS configuration
   - Add file validation

2. **Today**:
   - Fix race conditions
   - Add error handling
   - Fix async/sync mixing

3. **This Week**:
   - Add database indexes
   - Fix TypeScript config
   - Fix Docker volumes
   - Add missing enum values

4. **Next Sprint**:
   - Add database constraints
   - Fix hardcoded values