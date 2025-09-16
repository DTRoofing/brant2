"""
File validation utilities for secure file upload handling
"""
import os
import hashlib
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# PDF magic bytes signatures
PDF_SIGNATURES = [
    b'%PDF-1.',  # PDF 1.x
    b'%PDF-2.',  # PDF 2.x
]

# Maximum allowed file size (200MB)
MAX_FILE_SIZE = 200 * 1024 * 1024

# Allowed MIME types
ALLOWED_MIME_TYPES = {
    'application/pdf',
}


async def validate_pdf_magic_bytes(file_path: Path) -> bool:
    """
    Validate that a file is actually a PDF by checking magic bytes
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        True if file is a valid PDF, False otherwise
    """
    try:
        with open(file_path, 'rb') as f:
            # Read first 8 bytes
            header = f.read(8)
            
            # Check against known PDF signatures
            for signature in PDF_SIGNATURES:
                if header.startswith(signature):
                    return True
                    
            # Also check for PDF header anywhere in first 1024 bytes
            # (some PDFs have garbage before the header)
            f.seek(0)
            first_kb = f.read(1024)
            return b'%PDF-' in first_kb
            
    except Exception as e:
        logger.error(f"Error validating PDF magic bytes: {e}")
        return False


async def validate_pdf_structure(file_path: Path) -> Tuple[bool, Optional[str]]:
    """
    Perform deeper PDF structure validation
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        with open(file_path, 'rb') as f:
            # Check file size
            f.seek(0, os.SEEK_END)
            file_size = f.tell()
            if file_size > MAX_FILE_SIZE:
                return False, f"File size {file_size} exceeds maximum {MAX_FILE_SIZE}"
            
            # Check for PDF header
            f.seek(0)
            header = f.read(8)
            if not any(header.startswith(sig) for sig in PDF_SIGNATURES):
                # Check in first 1KB for header
                f.seek(0)
                first_kb = f.read(1024)
                if b'%PDF-' not in first_kb:
                    return False, "Invalid PDF header"
            
            # Check for PDF trailer (should contain %%EOF)
            f.seek(max(0, file_size - 1024))
            trailer = f.read()
            if b'%%EOF' not in trailer:
                # Some PDFs have trailing bytes after %%EOF
                # Check last 4KB instead
                f.seek(max(0, file_size - 4096))
                trailer = f.read()
                if b'%%EOF' not in trailer:
                    return False, "Invalid PDF trailer - missing %%EOF"
            
            # Basic structure checks
            f.seek(0)
            content = f.read(min(file_size, 1024 * 1024))  # Read first 1MB
            
            # Check for required PDF objects
            if b'/Root' not in content and b'/Catalog' not in content:
                return False, "Missing required PDF catalog"
            
            if b'obj' not in content or b'endobj' not in content:
                return False, "Missing PDF object markers"
            
            return True, None
            
    except Exception as e:
        logger.error(f"Error validating PDF structure: {e}")
        return False, str(e)


async def calculate_file_hash(file_path: Path, algorithm: str = 'sha256') -> str:
    """
    Calculate cryptographic hash of a file
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use (default: sha256)
        
    Returns:
        Hex digest of the file hash
    """
    hash_func = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        # Read in chunks to handle large files
        for chunk in iter(lambda: f.read(8192), b''):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()


async def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent directory traversal and other attacks
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove path components
    filename = os.path.basename(filename)
    
    # Remove dangerous characters
    dangerous_chars = ['/', '\\', '..', '~', '|', '>', '<', ':', '*', '?', '"']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')
    
    # Limit filename length
    name, ext = os.path.splitext(filename)
    if len(name) > 100:
        name = name[:100]
    
    # Ensure PDF extension
    if ext.lower() != '.pdf':
        ext = '.pdf'
    
    return name + ext


async def validate_upload(
    file_path: Path,
    original_filename: str,
    content_type: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Comprehensive file upload validation
    
    Args:
        file_path: Path to uploaded file
        original_filename: Original filename from upload
        content_type: MIME type from upload headers
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check MIME type if provided
    if content_type and content_type not in ALLOWED_MIME_TYPES:
        return False, f"Invalid content type: {content_type}"
    
    # Validate filename
    if not original_filename.lower().endswith('.pdf'):
        return False, "File must have .pdf extension"
    
    # Check magic bytes
    if not await validate_pdf_magic_bytes(file_path):
        return False, "File is not a valid PDF (invalid magic bytes)"
    
    # Validate PDF structure
    is_valid, error = await validate_pdf_structure(file_path)
    if not is_valid:
        return False, f"Invalid PDF structure: {error}"
    
    return True, None