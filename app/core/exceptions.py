"""
Custom exceptions for the Brant Roofing System API.
"""
from fastapi import HTTPException
from typing import Any, Dict, Optional


class BrantAPIException(HTTPException):
    """Base exception for Brant API with enhanced error details."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.context = context or {}


class DocumentNotFoundError(BrantAPIException):
    """Raised when a document is not found."""
    
    def __init__(self, document_id: str):
        super().__init__(
            status_code=404,
            detail=f"Document with ID {document_id} not found",
            error_code="DOCUMENT_NOT_FOUND",
            context={"document_id": document_id}
        )


class DocumentProcessingError(BrantAPIException):
    """Raised when document processing fails."""
    
    def __init__(self, document_id: str, reason: str):
        super().__init__(
            status_code=422,
            detail=f"Document processing failed: {reason}",
            error_code="PROCESSING_FAILED",
            context={"document_id": document_id, "reason": reason}
        )


class InvalidFileTypeError(BrantAPIException):
    """Raised when an invalid file type is uploaded."""
    
    def __init__(self, file_type: str, allowed_types: list):
        super().__init__(
            status_code=400,
            detail=f"Invalid file type '{file_type}'. Allowed types: {', '.join(allowed_types)}",
            error_code="INVALID_FILE_TYPE",
            context={"file_type": file_type, "allowed_types": allowed_types}
        )


class FileSizeExceededError(BrantAPIException):
    """Raised when file size exceeds the maximum allowed size."""
    
    def __init__(self, file_size: int, max_size: int):
        super().__init__(
            status_code=413,
            detail=f"File size {file_size} bytes exceeds maximum allowed size of {max_size} bytes",
            error_code="FILE_SIZE_EXCEEDED",
            context={"file_size": file_size, "max_size": max_size}
        )


class GoogleCloudServiceError(BrantAPIException):
    """Raised when Google Cloud service operations fail."""
    
    def __init__(self, service: str, operation: str, reason: str):
        super().__init__(
            status_code=503,
            detail=f"Google Cloud {service} {operation} failed: {reason}",
            error_code="GCP_SERVICE_ERROR",
            context={"service": service, "operation": operation, "reason": reason}
        )


class RateLimitExceededError(BrantAPIException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, retry_after: int):
        super().__init__(
            status_code=429,
            detail=f"Rate limit exceeded. Try again in {retry_after} seconds",
            error_code="RATE_LIMIT_EXCEEDED",
            context={"retry_after": retry_after}
        )


class ValidationError(BrantAPIException):
    """Raised when request validation fails."""
    
    def __init__(self, field: str, value: Any, reason: str):
        super().__init__(
            status_code=422,
            detail=f"Validation error for field '{field}': {reason}",
            error_code="VALIDATION_ERROR",
            context={"field": field, "value": value, "reason": reason}
        )

