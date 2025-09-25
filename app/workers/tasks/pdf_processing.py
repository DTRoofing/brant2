"""
Compatibility module for PDF processing tasks.
This module provides backward compatibility by importing from new_pdf_processing.
"""

# Import all the functions and classes from the new module
from .new_pdf_processing import (
    process_pdf_with_pipeline,
    process_document_with_claude_direct,
    cleanup_failed_documents,
    generate_processing_report,
    PipelineTask,
    _set_document_processing_status,
    _save_pipeline_results,
    _cleanup_temporary_gcs_files,
    _execute_pipeline_task,
    init_worker,
    shutdown_worker,
    engine,
    SessionLocal
)

# Import google_service and claude_service for testing compatibility
from app.services.google_services import google_service
from app.services.claude_service import claude_service

# For backward compatibility, also provide the old function name
def process_pdf_document(document_id: str):
    """
    Backward compatibility wrapper for process_pdf_with_pipeline.
    """
    return process_pdf_with_pipeline.delay(document_id)

# Make sure the module has the expected attributes
__all__ = [
    'process_pdf_with_pipeline',
    'process_pdf_document',  # Backward compatibility
    'process_document_with_claude_direct',
    'cleanup_failed_documents',
    'generate_processing_report',
    'PipelineTask',
    '_set_document_processing_status',
    '_save_pipeline_results',
    '_cleanup_temporary_gcs_files',
    '_execute_pipeline_task',
    'init_worker',
    'shutdown_worker',
    'engine',
    'SessionLocal',
    'google_service',  # For testing compatibility
    'claude_service'   # For testing compatibility
]
