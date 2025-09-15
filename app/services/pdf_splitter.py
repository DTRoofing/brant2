"""
PDF Splitter Service
Handles splitting large PDFs into smaller chunks that meet Google Document AI limits
"""
import os
import logging
import tempfile
from typing import List, Dict, Any
from pathlib import Path
import PyPDF2
from PyPDF2 import PdfWriter, PdfReader

logger = logging.getLogger(__name__)

class PDFSplitter:
    """Service for splitting large PDFs into manageable chunks"""
    
    def __init__(self, max_pages: int = 15, max_size_mb: int = 25):
        """
        Initialize PDF splitter
        
        Args:
            max_pages: Maximum pages per chunk (default 15 for Document AI processor)
            max_size_mb: Maximum size in MB per chunk (default 25 to stay under 30MB limit)
        """
        self.max_pages = max_pages
        self.max_size_mb = max_size_mb
        self.max_size_bytes = max_size_mb * 1024 * 1024
    
    def needs_splitting(self, file_path: str) -> bool:
        """
        Check if a PDF needs to be split
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            True if PDF exceeds limits and needs splitting
        """
        try:
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > self.max_size_bytes:
                logger.info(f"PDF {file_path} exceeds size limit: {file_size/1024/1024:.2f}MB > {self.max_size_mb}MB")
                return True
            
            # Check page count
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                page_count = len(reader.pages)
                
                if page_count > self.max_pages:
                    logger.info(f"PDF {file_path} exceeds page limit: {page_count} pages > {self.max_pages} pages")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking PDF limits for {file_path}: {e}")
            return False
    
    def split_pdf(self, file_path: str, output_dir: str = None) -> List[Dict[str, Any]]:
        """
        Split a PDF into smaller chunks
        
        Args:
            file_path: Path to source PDF
            output_dir: Directory for output files (if None, uses temp directory)
            
        Returns:
            List of dictionaries with chunk information:
            {
                'file_path': str,
                'start_page': int,
                'end_page': int,
                'page_count': int,
                'file_size_mb': float,
                'chunk_index': int
            }
        """
        try:
            if not self.needs_splitting(file_path):
                # Return original file if no splitting needed
                file_size = os.path.getsize(file_path)
                with open(file_path, 'rb') as file:
                    reader = PdfReader(file)
                    page_count = len(reader.pages)
                
                return [{
                    'file_path': file_path,
                    'start_page': 1,
                    'end_page': page_count,
                    'page_count': page_count,
                    'file_size_mb': round(file_size / 1024 / 1024, 2),
                    'chunk_index': 0,
                    'is_original': True
                }]
            
            # Create output directory
            if output_dir is None:
                output_dir = tempfile.mkdtemp(prefix="pdf_chunks_")
            else:
                os.makedirs(output_dir, exist_ok=True)
            
            logger.info(f"Splitting PDF {file_path} into chunks...")
            
            # Read the source PDF
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                total_pages = len(reader.pages)
            
            chunks = []
            chunk_index = 0
            
            # Split into chunks
            for start_page in range(0, total_pages, self.max_pages):
                end_page = min(start_page + self.max_pages, total_pages)
                
                # Create chunk filename
                base_name = Path(file_path).stem
                chunk_filename = f"{base_name}_chunk_{chunk_index + 1}_pages_{start_page + 1}-{end_page}.pdf"
                chunk_path = os.path.join(output_dir, chunk_filename)
                
                # Create the chunk PDF
                writer = PdfWriter()
                
                with open(file_path, 'rb') as file:
                    reader = PdfReader(file)
                    for page_num in range(start_page, end_page):
                        writer.add_page(reader.pages[page_num])
                
                # Write chunk to file
                with open(chunk_path, 'wb') as chunk_file:
                    writer.write(chunk_file)
                
                # Get chunk info
                chunk_size = os.path.getsize(chunk_path)
                chunk_pages = end_page - start_page
                
                chunk_info = {
                    'file_path': chunk_path,
                    'start_page': start_page + 1,  # 1-indexed
                    'end_page': end_page,
                    'page_count': chunk_pages,
                    'file_size_mb': round(chunk_size / 1024 / 1024, 2),
                    'chunk_index': chunk_index,
                    'is_original': False
                }
                
                chunks.append(chunk_info)
                
                logger.info(f"Created chunk {chunk_index + 1}: {chunk_filename} "
                          f"({chunk_pages} pages, {chunk_info['file_size_mb']}MB)")
                
                # Check if chunk still exceeds size limit
                if chunk_size > self.max_size_bytes:
                    logger.warning(f"Chunk {chunk_filename} still exceeds size limit: "
                                 f"{chunk_info['file_size_mb']}MB > {self.max_size_mb}MB")
                
                chunk_index += 1
            
            logger.info(f"Successfully split PDF into {len(chunks)} chunks in {output_dir}")
            return chunks
            
        except Exception as e:
            logger.error(f"Error splitting PDF {file_path}: {e}")
            raise
    
    def merge_results(self, chunk_results: List[Dict[str, Any]], 
                     source_file: str) -> Dict[str, Any]:
        """
        Merge processing results from multiple chunks
        
        Args:
            chunk_results: List of processing results from each chunk
            source_file: Path to original source file
            
        Returns:
            Combined results dictionary
        """
        try:
            if not chunk_results:
                return {}
            
            # Initialize combined results
            combined = {
                'source_file': source_file,
                'chunk_count': len(chunk_results),
                'total_pages': sum(r.get('page_count', 0) for r in chunk_results),
                'combined_text': '',
                'combined_entities': [],
                'combined_tables': [],
                'combined_measurements': [],
                'chunk_summaries': []
            }
            
            # Combine text and data from all chunks
            for i, chunk_result in enumerate(chunk_results):
                chunk_summary = {
                    'chunk_index': i,
                    'pages': f"{chunk_result.get('start_page', 0)}-{chunk_result.get('end_page', 0)}",
                    'text_length': len(chunk_result.get('text', '')),
                    'entities_count': len(chunk_result.get('entities', [])),
                    'tables_count': len(chunk_result.get('tables', [])),
                    'file_path': chunk_result.get('file_path', '')
                }
                combined['chunk_summaries'].append(chunk_summary)
                
                # Combine text
                chunk_text = chunk_result.get('text', '')
                if chunk_text:
                    combined['combined_text'] += chunk_text + '\n\n'
                
                # Combine entities with page offset
                entities = chunk_result.get('entities', [])
                for entity in entities:
                    entity_copy = entity.copy()
                    entity_copy['source_chunk'] = i
                    entity_copy['source_pages'] = chunk_summary['pages']
                    combined['combined_entities'].append(entity_copy)
                
                # Combine tables
                tables = chunk_result.get('tables', [])
                for table in tables:
                    table_copy = table.copy() if isinstance(table, dict) else table
                    if isinstance(table_copy, dict):
                        table_copy['source_chunk'] = i
                        table_copy['source_pages'] = chunk_summary['pages']
                    combined['combined_tables'].append(table_copy)
                
                # Combine measurements
                measurements = chunk_result.get('measurements', [])
                for measurement in measurements:
                    measurement_copy = measurement.copy() if isinstance(measurement, dict) else measurement
                    if isinstance(measurement_copy, dict):
                        measurement_copy['source_chunk'] = i
                        measurement_copy['source_pages'] = chunk_summary['pages']
                    combined['combined_measurements'].append(measurement_copy)
            
            logger.info(f"Merged results from {len(chunk_results)} chunks: "
                       f"{len(combined['combined_text'])} chars, "
                       f"{len(combined['combined_entities'])} entities, "
                       f"{len(combined['combined_tables'])} tables")
            
            return combined
            
        except Exception as e:
            logger.error(f"Error merging chunk results: {e}")
            raise
    
    def cleanup_chunks(self, chunks: List[Dict[str, Any]]):
        """
        Clean up temporary chunk files
        
        Args:
            chunks: List of chunk information dictionaries
        """
        try:
            for chunk in chunks:
                if not chunk.get('is_original', False):
                    chunk_file = chunk.get('file_path')
                    if chunk_file and os.path.exists(chunk_file):
                        os.unlink(chunk_file)
                        logger.debug(f"Deleted chunk file: {chunk_file}")
                        
            # Try to remove empty temp directory
            if chunks and not chunks[0].get('is_original', False):
                first_chunk_dir = os.path.dirname(chunks[0]['file_path'])
                if first_chunk_dir and first_chunk_dir.startswith('/tmp') or 'temp' in first_chunk_dir.lower():
                    try:
                        os.rmdir(first_chunk_dir)
                        logger.debug(f"Removed temp directory: {first_chunk_dir}")
                    except OSError:
                        pass  # Directory not empty or doesn't exist
                        
        except Exception as e:
            logger.warning(f"Error cleaning up chunk files: {e}")

# Singleton instance
pdf_splitter = PDFSplitter()