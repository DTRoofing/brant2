"""
Comprehensive error handling utilities for the Brant Roofing System.
"""
import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better classification"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    FILE_PROCESSING = "file_processing"
    DATABASE = "database"
    EXTERNAL_SERVICE = "external_service"
    NETWORK = "network"
    CONFIGURATION = "configuration"
    UNKNOWN = "unknown"


class BrantError(Exception):
    """Base exception class for Brant-specific errors"""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        recoverable: bool = False
    ):
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.recoverable = recoverable
        self.timestamp = datetime.now()
        super().__init__(self.message)


class ErrorHandler:
    """Centralized error handling and logging"""
    
    @staticmethod
    def handle_error(
        error: Exception,
        context: str = "",
        user_message: Optional[str] = None,
        log_level: int = logging.ERROR
    ) -> HTTPException:
        """
        Handle an error and return an appropriate HTTPException.
        
        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
            user_message: Custom message to show to the user
            log_level: Logging level for the error
            
        Returns:
            HTTPException with appropriate status code and message
        """
        # Log the error with context
        logger.log(
            log_level,
            f"Error in {context}: {str(error)}",
            exc_info=True
        )
        
        # Determine error category and severity
        category, severity = ErrorHandler._classify_error(error)
        
        # Get appropriate HTTP status code
        status_code = ErrorHandler._get_status_code(error, category, severity)
        
        # Get user-friendly message
        if user_message:
            message = user_message
        else:
            message = ErrorHandler._get_user_message(error, category)
        
        # Add error details for debugging
        error_details = {
            "error_type": type(error).__name__,
            "category": category.value,
            "severity": severity.value,
            "timestamp": datetime.now().isoformat(),
            "context": context
        }
        
        return HTTPException(
            status_code=status_code,
            detail={
                "message": message,
                "error_details": error_details
            }
        )
    
    @staticmethod
    def _classify_error(error: Exception) -> tuple[ErrorCategory, ErrorSeverity]:
        """Classify an error by category and severity"""
        error_type = type(error).__name__
        
        # Authentication errors
        if any(auth_error in error_type for auth_error in ["AuthenticationError", "InvalidCredentials", "TokenError"]):
            return ErrorCategory.AUTHENTICATION, ErrorSeverity.HIGH
        
        # Authorization errors
        if any(auth_error in error_type for auth_error in ["PermissionError", "ForbiddenError", "AccessDenied"]):
            return ErrorCategory.AUTHORIZATION, ErrorSeverity.HIGH
        
        # Validation errors
        if any(val_error in error_type for val_error in ["ValidationError", "ValueError", "TypeError"]):
            return ErrorCategory.VALIDATION, ErrorSeverity.MEDIUM
        
        # File processing errors
        if any(file_error in error_type for file_error in ["FileNotFoundError", "PDFError", "ImageError"]):
            return ErrorCategory.FILE_PROCESSING, ErrorSeverity.MEDIUM
        
        # Database errors
        if any(db_error in error_type for db_error in ["DatabaseError", "SQLAlchemyError", "IntegrityError"]):
            return ErrorCategory.DATABASE, ErrorSeverity.HIGH
        
        # External service errors
        if any(ext_error in error_type for ext_error in ["GoogleAPICallError", "ClaudeError", "ExternalServiceError"]):
            return ErrorCategory.EXTERNAL_SERVICE, ErrorSeverity.MEDIUM
        
        # Network errors
        if any(net_error in error_type for net_error in ["ConnectionError", "TimeoutError", "NetworkError"]):
            return ErrorCategory.NETWORK, ErrorSeverity.MEDIUM
        
        # Configuration errors
        if any(config_error in error_type for config_error in ["ConfigurationError", "MissingConfig"]):
            return ErrorCategory.CONFIGURATION, ErrorSeverity.CRITICAL
        
        # Default classification
        return ErrorCategory.UNKNOWN, ErrorSeverity.MEDIUM
    
    @staticmethod
    def _get_status_code(error: Exception, category: ErrorCategory, severity: ErrorSeverity) -> int:
        """Get appropriate HTTP status code for an error"""
        if category == ErrorCategory.AUTHENTICATION:
            return status.HTTP_401_UNAUTHORIZED
        elif category == ErrorCategory.AUTHORIZATION:
            return status.HTTP_403_FORBIDDEN
        elif category == ErrorCategory.VALIDATION:
            return status.HTTP_422_UNPROCESSABLE_ENTITY
        elif category == ErrorCategory.FILE_PROCESSING:
            if "FileNotFoundError" in type(error).__name__:
                return status.HTTP_404_NOT_FOUND
            elif "FileTooLarge" in str(error):
                return status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            else:
                return status.HTTP_400_BAD_REQUEST
        elif category == ErrorCategory.DATABASE:
            return status.HTTP_500_INTERNAL_SERVER_ERROR
        elif category == ErrorCategory.EXTERNAL_SERVICE:
            return status.HTTP_502_BAD_GATEWAY
        elif category == ErrorCategory.NETWORK:
            return status.HTTP_503_SERVICE_UNAVAILABLE
        elif category == ErrorCategory.CONFIGURATION:
            return status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            return status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def _get_user_message(error: Exception, category: ErrorCategory) -> str:
        """Get user-friendly error message"""
        if category == ErrorCategory.AUTHENTICATION:
            return "Authentication failed. Please check your credentials."
        elif category == ErrorCategory.AUTHORIZATION:
            return "You don't have permission to perform this action."
        elif category == ErrorCategory.VALIDATION:
            return "Invalid data provided. Please check your input."
        elif category == ErrorCategory.FILE_PROCESSING:
            if "FileNotFoundError" in type(error).__name__:
                return "File not found. Please check the file path."
            elif "FileTooLarge" in str(error):
                return "File is too large. Please use a smaller file."
            else:
                return "Error processing file. Please try again."
        elif category == ErrorCategory.DATABASE:
            return "Database error occurred. Please try again later."
        elif category == ErrorCategory.EXTERNAL_SERVICE:
            return "External service temporarily unavailable. Please try again later."
        elif category == ErrorCategory.NETWORK:
            return "Network error occurred. Please check your connection and try again."
        elif category == ErrorCategory.CONFIGURATION:
            return "System configuration error. Please contact support."
        else:
            return "An unexpected error occurred. Please try again later."


# Convenience functions for common error scenarios
def handle_upload_error(error: Exception, filename: str = "") -> HTTPException:
    """Handle file upload errors with specific context"""
    context = f"file upload: {filename}" if filename else "file upload"
    return ErrorHandler.handle_error(
        error,
        context=context,
        user_message=f"Failed to upload file '{filename}'. Please try again."
    )


def handle_processing_error(error: Exception, document_id: str = "") -> HTTPException:
    """Handle document processing errors with specific context"""
    context = f"document processing: {document_id}" if document_id else "document processing"
    return ErrorHandler.handle_error(
        error,
        context=context,
        user_message="Failed to process document. Please try again later."
    )


def handle_database_error(error: Exception, operation: str = "") -> HTTPException:
    """Handle database errors with specific context"""
    context = f"database operation: {operation}" if operation else "database operation"
    return ErrorHandler.handle_error(
        error,
        context=context,
        user_message="Database error occurred. Please try again later."
    )


def handle_auth_error(error: Exception, action: str = "") -> HTTPException:
    """Handle authentication errors with specific context"""
    context = f"authentication: {action}" if action else "authentication"
    return ErrorHandler.handle_error(
        error,
        context=context,
        user_message="Authentication failed. Please check your credentials."
    )
