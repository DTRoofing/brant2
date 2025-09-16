"""
Selective Page Extractor
Extracts only specific pages from a PDF instead of processing the entire document
"""
import os
import logging
import tempfile
from typing import List, Optional
from pathlib import Path
from PyPDF2 import PdfWriter, PdfReader

logger = logging.getLogger(__name__)


class SelectivePageExtractor:
    """Extracts only specific pages from a PDF to avoid processing unnecessary content"""

    def extract_pages(self, file_path: str, page_numbers: List[int],
                     max_pages: int = 10) -> Optional[str]:
        """
        Extract specific pages from a PDF

        Args:
            file_path: Path to source PDF
            page_numbers: List of page numbers to extract (1-indexed)
            max_pages: Maximum number of pages to extract (safety limit)

        Returns:
            Path to new PDF with only the selected pages, or None if extraction fails
        """
        if not page_numbers:
            logger.warning("No page numbers specified for extraction")
            return None

        # Limit pages to extract for safety
        pages_to_extract = page_numbers[:max_pages]

        try:
            logger.info(f"Extracting pages {pages_to_extract} from {file_path}")

            # Create temporary file for extracted pages
            temp_dir = tempfile.mkdtemp(prefix="extracted_pages_")
            output_filename = f"{Path(file_path).stem}_extracted_pages.pdf"
            output_path = os.path.join(temp_dir, output_filename)

            with open(file_path, 'rb') as input_file:
                reader = PdfReader(input_file)
                writer = PdfWriter()

                total_pages = len(reader.pages)
                extracted_count = 0

                for page_num in pages_to_extract:
                    # Convert to 0-indexed
                    page_idx = page_num - 1

                    if 0 <= page_idx < total_pages:
                        writer.add_page(reader.pages[page_idx])
                        extracted_count += 1
                        logger.info(f"  Added page {page_num} to extracted document")
                    else:
                        logger.warning(f"  Page {page_num} out of range (document has {total_pages} pages)")

                # Always include page 2 for General Notes if not already included
                if 2 not in pages_to_extract and 1 < total_pages:
                    writer.add_page(reader.pages[1])  # Page 2 (0-indexed)
                    extracted_count += 1
                    logger.info("  Added page 2 (General Notes) as required")

                # Write the extracted pages
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)

                file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                logger.info(f"Successfully extracted {extracted_count} pages to {output_path} ({file_size_mb:.2f}MB)")

                return output_path

        except Exception as e:
            logger.error(f"Failed to extract pages from {file_path}: {e}")
            return None

    def should_use_extraction(self, file_path: str, relevant_pages: List[int]) -> bool:
        """
        Determine if selective extraction should be used

        Args:
            file_path: Path to PDF file
            relevant_pages: List of relevant page numbers

        Returns:
            True if extraction would significantly reduce processing
        """
        try:
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                total_pages = len(reader.pages)

                # Use extraction if we're processing less than 30% of the document
                # or if the document has more than 20 pages
                if relevant_pages:
                    pages_to_process = len(relevant_pages)

                    # Always use extraction for large documents
                    if total_pages > 20:
                        logger.info(f"Large document ({total_pages} pages) - will extract {pages_to_process} relevant pages")
                        return True

                    # Use extraction if we're processing less than 30% of pages
                    if pages_to_process < total_pages * 0.3:
                        logger.info(f"Will extract {pages_to_process}/{total_pages} pages (less than 30%)")
                        return True

            return False

        except Exception as e:
            logger.error(f"Error checking extraction criteria: {e}")
            return False


# Singleton instance
selective_page_extractor = SelectivePageExtractor()