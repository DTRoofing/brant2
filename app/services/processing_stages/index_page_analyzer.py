import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import PyPDF2
from pdf2image import convert_from_path
import pytesseract
import json

logger = logging.getLogger(__name__)


class IndexPageAnalyzer:
    """Analyzes the first page table of contents to extract metadata and identify relevant pages by title"""

    def __init__(self):
        # Patterns to identify the table of contents section
        self.toc_patterns = [
            r'drawing\s+index',
            r'sheet\s+index',
            r'drawing\s+list',
            r'sheet\s+list',
            r'table\s+of\s+contents',
            r'index\s+of\s+drawings',
            r'drawing\s+schedule'
        ]

        # Title-based patterns for roof-related drawings
        self.roof_drawing_titles = [
            'roof plan',
            'roof plans',
            'roofplan',  # Sometimes written as one word
            'roofing plan',
            'roof framing',
            'roof framing plan',
            'roof details',
            'roof detail',
            'roof sections',
            'roof section',
            'parapet details',
            'roof drainage',
            'roof drainage plan',
            'roof layout',
            'roof structure',
            'rooftop plan',
            'rooftop equipment',
            'roof penetrations',
            'r.p.',  # Common abbreviation
            'rf plan',
            'roof membrane',
            'roof access'
        ]

        # Specific sheet designations that should ALWAYS be included
        self.required_sheet_patterns = [
            # Architectural
            r'A-?1\.3',  # A1.3 is standard for roof plans (with or without hyphen)
            r'A\s*1\.3',  # May have space: A 1.3

            # Structural
            r'S-?1\.2',  # S1.2 Roof Framing Plan
            r'S\s*1\.2',  # May have space: S 1.2

            # Mechanical
            r'M-?1\.0',  # M1.0 Mechanical Roof Plan
            r'M\s*1\.0',  # May have space: M 1.0

            # General Notes (usually page 2)
            r'general\s+notes',
            r'general\s+construction\s+notes',
            r'page\s+2.*general',  # Page 2 when it contains general notes
        ]

        # Track which required sheets we're looking for
        self.required_sheets_checklist = {
            'A1.3': 'Roof Plan',
            'S1.2': 'Roof Framing Plan',
            'M1.0': 'Mechanical Roof Plan',
            'Page 2': 'General Notes'
        }

        self.metadata_patterns = {
            # Building Information
            'square_footage': [
                r'(\d{1,3}(?:,\d{3})*)\s*(?:sq\.?\s*ft\.?|square\s+feet|sf)',
                r'area[:\s]*(\d{1,3}(?:,\d{3})*)\s*(?:sq\.?\s*ft\.?|sf)?',
                r'building\s+area[:\s]*(\d{1,3}(?:,\d{3})*)',
                r'gross\s+building\s+area[:\s]*(\d{1,3}(?:,\d{3})*)',
                r'total\s+area[:\s]*(\d{1,3}(?:,\d{3})*)'
            ],
            'building_height': [
                r'building\s+height[:\s]*([^\n]+)',
                r'height[:\s]*(\d+[\'\-]?\d*["\']?)',
                r'overall\s+height[:\s]*([^\n]+)'
            ],
            'structural_makeup': [
                r'structural\s+(?:makeup|system)[:\s]*([^\n]+)',
                r'structure[:\s]*([^\n]+)',
                r'construction\s+type[:\s]*([^\n]+)'
            ],

            # Project Information
            'project_name': [
                r'project[:\s]*([^\n]+)',
                r'job\s+name[:\s]*([^\n]+)',
                r'building[:\s]*([^\n]+)',
                r'title[:\s]*([^\n]+)'
            ],
            'project_number': [
                r'project\s+(?:no|number|#)[:\s]*([A-Z0-9\-]+)',
                r'job\s+(?:no|number|#)[:\s]*([A-Z0-9\-]+)',
                r'drawing\s+(?:no|number|#)[:\s]*([A-Z0-9\-]+)'
            ],
            'site_id': [
                r'site\s+id[:\s]*([A-Z0-9\-]+)',
                r'site\s+(?:no|number|#)[:\s]*([A-Z0-9\-]+)',
                r'location\s+id[:\s]*([A-Z0-9\-]+)'
            ],

            # Location
            'address': [
                r'address[:\s]*([^\n]+)',
                r'location[:\s]*([^\n]+)',
                r'site[:\s]*([^\n]+)',
                r'property\s+address[:\s]*([^\n]+)'
            ],

            # Contact Information
            'project_manager': [
                r'project\s+manager[:\s]*([^\n]+)',
                r'pm[:\s]*([A-Za-z\s]+)',
                r'manager[:\s]*([A-Za-z\s]+)'
            ],
            'pm_email': [
                r'(?:pm|project\s+manager)\s+email[:\s]*([\w\.\-]+@[\w\.\-]+)',
                r'email[:\s]*([\w\.\-]+@[\w\.\-]+)'
            ],
            'pm_phone': [
                r'(?:pm|project\s+manager)\s+phone[:\s]*([\d\-\.\(\)\s]+)',
                r'phone[:\s]*([\d\-\.\(\)\s]+)',
                r'tel[:\s]*([\d\-\.\(\)\s]+)'
            ],

            # Design Team
            'designer_of_record': [
                r'designer\s+of\s+record[:\s]*([^\n]+)',
                r'architect[:\s]*([^\n]+)',
                r'design\s+firm[:\s]*([^\n]+)',
                r'designed\s+by[:\s]*([^\n]+)'
            ],
            'engineer': [
                r'engineer[:\s]*([^\n]+)',
                r'structural\s+engineer[:\s]*([^\n]+)',
                r'engineer\s+of\s+record[:\s]*([^\n]+)'
            ],

            # Dates
            'issue_date': [
                r'(?:std\s+)?issue\s+date[:\s]*([\d/\-\.]+)',
                r'date\s+issued[:\s]*([\d/\-\.]+)',
                r'issued[:\s]*([\d/\-\.]+)'
            ],
            'review_date': [
                r'review(?:ed)?\s+(?:by|date)[:\s]*([\d/\-\.]+)',
                r'date\s+reviewed[:\s]*([\d/\-\.]+)'
            ],
            'reviewed_by': [
                r'reviewed?\s+by[:\s]*([A-Za-z\s]+)',
                r'reviewer[:\s]*([A-Za-z\s]+)'
            ],

            # Materials
            'roof_materials': [
                r'(?:roof|roofing)\s+(?:material|type)[:\s]*([^\n]+)',
                r'membrane[:\s]*([^\n]+)',
                r'shingle[s]?[:\s]*([^\n]+)',
                r'(?:tpo|epdm|pvc|modified\s+bitumen|built-up|metal)'
            ]
        }

    async def analyze_index_page(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze the first page to extract index and metadata

        Returns:
            Dictionary containing:
            - roof_pages: List of page numbers containing roof-related content
            - metadata: Extracted project metadata
            - index_text: Full OCR text from the first page
            - confidence: Confidence score for the extraction
        """
        logger.info(f"Analyzing index page of: {file_path}")

        try:
            # Extract text from first page using OCR for best results
            index_text = await self._ocr_first_page(file_path)

            # Parse the drawing index to find roof-related pages
            roof_drawings = self._extract_roof_pages_from_index(index_text)

            # Extract metadata from the first page
            metadata = self._extract_metadata(index_text)

            # Calculate confidence based on what we found
            confidence = self._calculate_confidence(roof_drawings, metadata, index_text)

            # Convert roof_drawings to simple page list for compatibility
            roof_pages = []
            roof_drawing_titles = []
            for drawing in roof_drawings:
                if drawing.get('page_number'):
                    roof_pages.append(drawing['page_number'])
                    roof_drawing_titles.append({
                        'page': drawing['page_number'],
                        'title': drawing['title'],
                        'sheet': drawing.get('reference', ''),
                        'required': drawing.get('required', False)
                    })

            result = {
                'roof_pages': sorted(list(set(roof_pages))),  # Unique, sorted page numbers
                'roof_drawings': roof_drawing_titles,  # Detailed drawing info
                'metadata': metadata,
                'index_text': index_text[:5000],  # Limit stored text
                'confidence': confidence,
                'has_index': self._has_table_of_contents(index_text)
            }

            # Check for all required sheets
            found_sheets = {}
            for drawing in roof_drawing_titles:
                sheet_ref = drawing.get('sheet', '').upper().replace('-', '').replace(' ', '')
                if sheet_ref == 'A1.3':
                    found_sheets['A1.3'] = True
                elif sheet_ref == 'S1.2':
                    found_sheets['S1.2'] = True
                elif sheet_ref == 'M1.0':
                    found_sheets['M1.0'] = True

                # Check for General Notes on page 2
                if drawing.get('page') == 2 and 'general' in drawing.get('title', '').lower():
                    found_sheets['Page 2'] = True

            # Log which required sheets were found
            logger.info("Required sheets detection:")
            for sheet_id, sheet_name in self.required_sheets_checklist.items():
                if found_sheets.get(sheet_id):
                    logger.info(f"  ✓ {sheet_id} ({sheet_name}) - FOUND")
                else:
                    logger.warning(f"  ⚠ {sheet_id} ({sheet_name}) - NOT FOUND")

            # Always include page 2 for General Notes even if not explicitly detected
            if 2 not in roof_pages and 'Page 2' not in found_sheets:
                roof_pages.append(2)
                logger.info("  → Adding page 2 for General Notes (always required)")

            logger.info(f"Index analysis complete. Found {len(roof_drawings)} roof-related drawings")
            logger.info(f"Roof drawings found: {json.dumps(roof_drawing_titles, indent=2)}")
            logger.info(f"Metadata extracted: {json.dumps(metadata, indent=2)}")

            return result

        except Exception as e:
            logger.error(f"Index page analysis failed: {e}")
            return {
                'roof_pages': [],
                'metadata': {},
                'index_text': '',
                'confidence': 0.0,
                'has_index': False,
                'error': str(e)
            }

    async def _ocr_first_page(self, file_path: str) -> str:
        """Perform OCR on the first page only"""
        try:
            # Convert only the first page to image
            images = convert_from_path(file_path, first_page=1, last_page=1, dpi=300)

            if not images:
                logger.warning("No images extracted from first page")
                return ""

            # OCR the first page with high quality settings
            first_page_image = images[0]

            # Configure tesseract for better results
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(first_page_image, config=custom_config)

            logger.info(f"OCR extracted {len(text)} characters from first page")
            return text

        except Exception as e:
            logger.error(f"OCR failed for first page: {e}")
            # Fallback to PyPDF2 text extraction
            return self._extract_text_pypdf(file_path, page_num=0)

    def _extract_text_pypdf(self, file_path: str, page_num: int = 0) -> str:
        """Fallback text extraction using PyPDF2"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                if len(pdf_reader.pages) > page_num:
                    return pdf_reader.pages[page_num].extract_text()
            return ""
        except Exception as e:
            logger.error(f"PyPDF2 extraction failed: {e}")
            return ""

    def _has_table_of_contents(self, text: str) -> bool:
        """Check if the page contains a table of contents/drawing index"""
        text_lower = text.lower()
        for pattern in self.toc_patterns:
            if re.search(pattern, text_lower):
                return True
        return False

    def _extract_roof_pages_from_index(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse the table of contents to find drawings with roof-related titles

        Returns:
            List of dictionaries containing page info with title and page number/reference
        """
        roof_drawings = []

        # Split text into lines for analysis
        lines = text.split('\n')

        # Look for table of contents entries
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()

            # Skip empty lines
            if not line_lower:
                continue

            # First check for required sheet patterns (like A1.3)
            is_required_sheet = False
            for pattern in self.required_sheet_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    is_required_sheet = True
                    drawing_info = self._parse_drawing_entry(line, i, lines)
                    if drawing_info:
                        drawing_info['required'] = True  # Mark as required
                        roof_drawings.append(drawing_info)
                        logger.info(f"Found REQUIRED roof sheet: {drawing_info['title']} on sheet {drawing_info['reference']}")
                    break

            # If not a required sheet, check if line contains a roof-related drawing title
            if not is_required_sheet:
                for title_pattern in self.roof_drawing_titles:
                    if title_pattern in line_lower:
                        # Extract the full line as it likely contains both title and page reference
                        drawing_info = self._parse_drawing_entry(line, i, lines)

                        if drawing_info:
                            drawing_info['required'] = False
                            roof_drawings.append(drawing_info)
                            logger.info(f"Found roof drawing: {drawing_info['title']} on page/sheet {drawing_info['reference']}")
                        break

        # If we found titled drawings but no page numbers, try to infer them
        if roof_drawings and not any(d.get('page_number') for d in roof_drawings):
            # Architectural drawings often follow a sequence after the first few pages
            # Typically: Cover, Index, Site Plan, Floor Plans, then Roof Plans
            logger.info("Found roof drawing titles without clear page numbers, inferring likely pages 4-7")
            for i, drawing in enumerate(roof_drawings):
                drawing['page_number'] = 4 + i

        return roof_drawings

    def _parse_drawing_entry(self, line: str, line_idx: int, all_lines: List[str]) -> Dict[str, Any]:
        """
        Parse a single drawing entry from the table of contents

        Returns:
            Dictionary with title, reference (sheet number), and page number if found
        """
        entry = {
            'title': '',
            'reference': '',  # Sheet number like A-301, R-1, etc.
            'page_number': None
        }

        # Common patterns for drawing entries:
        # "A-301  ROOF PLAN"
        # "ROOF PLAN ........... A-301"
        # "R-1 - ROOF DETAILS"
        # "ROOF DRAINAGE PLAN    R-2"

        # Pattern for sheet number (e.g., A-301, R-1, S-2.1, A1.3)
        # Updated to better capture A1.3 format
        sheet_patterns = [
            r'([A-Z]-?\d+\.\d+[A-Z]?)',  # A1.3, A-1.3, S-2.1A
            r'([A-Z]-\d{3})',  # A-301
            r'([A-Z]\d+)',  # A1, R1
            r'([A-Z]-\d+)',  # A-1, R-2
        ]

        sheet_match = None
        for pattern in sheet_patterns:
            sheet_match = re.search(pattern, line)
            if sheet_match:
                break

        if sheet_match:
            entry['reference'] = sheet_match.group(1)

            # Special handling for required sheets
            sheet_upper = entry['reference'].upper().replace('-', '').replace(' ', '')
            if sheet_upper == 'A1.3':
                logger.info(f"Detected A1.3 sheet - Roof Plan (REQUIRED)")
                entry['required'] = True
            elif sheet_upper == 'S1.2':
                logger.info(f"Detected S1.2 sheet - Roof Framing Plan (REQUIRED)")
                entry['required'] = True
            elif sheet_upper == 'M1.0':
                logger.info(f"Detected M1.0 sheet - Mechanical Roof Plan (REQUIRED)")
                entry['required'] = True

            # Remove the sheet reference to get the title
            title_text = line
            for pattern in sheet_patterns:
                title_text = re.sub(pattern, '', title_text)
            # Clean up dots, dashes, and extra spaces
            title_text = re.sub(r'[\.\-]{2,}', '', title_text)
            title_text = re.sub(r'\s+', ' ', title_text).strip()
            entry['title'] = title_text

            # Try to extract page number if present
            # Sometimes format is "Sheet A-301 (Page 5)"
            page_pattern = r'(?:page|pg|p\.?)\s*(\d+)'
            page_match = re.search(page_pattern, line, re.IGNORECASE)
            if page_match:
                entry['page_number'] = int(page_match.group(1))
            else:
                # Try to infer page number from sheet sequence
                # If this is sheet R-1 and we know the sequence, estimate the page
                entry['page_number'] = self._infer_page_from_sheet(entry['reference'])
        else:
            # No sheet reference found, just store the title
            entry['title'] = line.strip()

        return entry if entry['title'] else None

    def _infer_page_from_sheet(self, sheet_reference: str) -> Optional[int]:
        """
        Attempt to infer page number from sheet reference
        Common patterns:
        - A series (Architectural): Usually starts around page 3-5
        - S series (Structural): Usually after A series
        - R series (Roofing): Often dedicated roof sheets
        """
        if not sheet_reference:
            return None

        # Extract the numeric part
        num_match = re.search(r'(\d+)', sheet_reference)
        if not num_match:
            return None

        sheet_num = int(num_match.group(1))

        # Special handling for required sheets - positions vary by document
        sheet_upper = sheet_reference.upper().replace('-', '').replace(' ', '')

        if sheet_upper == 'A1.3':
            # A1.3 Roof Plan - position varies, could be page 5-20
            logger.info(f"A1.3 Roof Plan detected - actual page position must be determined from TOC")
            return None  # Don't assume, let TOC parsing determine actual page
        elif sheet_upper == 'S1.2':
            # S1.2 Roof Framing Plan - usually after architectural sheets
            logger.info(f"S1.2 Roof Framing Plan detected - actual page position must be determined from TOC")
            return None
        elif sheet_upper == 'M1.0':
            # M1.0 Mechanical Roof Plan - usually in mechanical section
            logger.info(f"M1.0 Mechanical Roof Plan detected - actual page position must be determined from TOC")
            return None

        # Rough estimation for other sheets based on common drawing organization
        if sheet_reference.startswith('A'):
            # A1.x series usually in sequence
            if '.' in sheet_reference:
                decimal_part = float(sheet_reference.split('.')[1][:1])
                return int(3 + decimal_part * 2)  # Rough estimate
            else:
                return 2 + sheet_num  # Architectural usually starts early
        elif sheet_reference.startswith('R'):
            return 5 + sheet_num  # Roofing sheets
        elif sheet_reference.startswith('S'):
            return 10 + sheet_num  # Structural usually comes later

        return None


    def _extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract comprehensive project metadata from the first page"""
        metadata = {}

        for field, patterns in self.metadata_patterns.items():
            for pattern in patterns:
                matches = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if matches:
                    value = matches.group(1).strip()

                    # Clean up the value based on field type
                    if field in ['square_footage']:
                        # Remove commas and convert to int
                        try:
                            value = int(value.replace(',', ''))
                        except:
                            pass
                    elif field in ['pm_phone']:
                        # Clean phone number format
                        value = re.sub(r'[^\d\-\(\)\s]', '', value).strip()
                    elif field in ['pm_email']:
                        # Validate email format
                        if '@' not in value:
                            continue
                        value = value.lower()
                    elif field in ['issue_date', 'review_date']:
                        # Standardize date format if possible
                        value = self._standardize_date(value)

                    metadata[field] = value
                    break

        # Look for McDonald's specific information
        if 'mcdonald' in text.lower():
            metadata['client'] = "McDonald's"

            # Look for store number
            store_match = re.search(r'store\s*#?\s*(\d{3}-\d{4}|\d{7})', text, re.IGNORECASE)
            if store_match:
                metadata['store_number'] = store_match.group(1)

        # Extract any phone numbers not yet captured
        if 'pm_phone' not in metadata:
            phone_patterns = [
                r'\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}',
                r'\d{3}\.\d{3}\.\d{4}'
            ]
            for pattern in phone_patterns:
                phone_match = re.search(pattern, text)
                if phone_match:
                    metadata['pm_phone'] = phone_match.group(0)
                    break

        # Extract any email addresses not yet captured
        if 'pm_email' not in metadata:
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            email_match = re.search(email_pattern, text)
            if email_match:
                metadata['pm_email'] = email_match.group(0).lower()

        return metadata

    def _standardize_date(self, date_str: str) -> str:
        """Attempt to standardize date format to MM/DD/YYYY"""
        import re
        from datetime import datetime

        # Common date patterns
        patterns = [
            (r'(\d{1,2})/(\d{1,2})/(\d{4})', '%m/%d/%Y'),
            (r'(\d{1,2})-(\d{1,2})-(\d{4})', '%m-%d-%Y'),
            (r'(\d{4})/(\d{1,2})/(\d{1,2})', '%Y/%m/%d'),
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', '%Y-%m-%d')
        ]

        for pattern, date_format in patterns:
            match = re.match(pattern, date_str.strip())
            if match:
                try:
                    date_obj = datetime.strptime(match.group(0), date_format)
                    return date_obj.strftime('%m/%d/%Y')
                except:
                    pass

        return date_str  # Return original if can't standardize

    def _calculate_confidence(self, roof_drawings: List[Dict], metadata: Dict, text: str) -> float:
        """Calculate confidence score for the extraction"""
        confidence = 0.0

        # Check if we found a table of contents
        if self._has_table_of_contents(text):
            confidence += 0.3

        # Check if we found roof drawings with titles
        if roof_drawings:
            confidence += 0.3
            # Bonus confidence for having sheet references
            if any(d.get('reference') for d in roof_drawings):
                confidence += 0.1

        # Check metadata quality
        if metadata.get('square_footage'):
            confidence += 0.15
        if metadata.get('project_name') or metadata.get('project_number'):
            confidence += 0.15
        if metadata.get('materials'):
            confidence += 0.1

        return min(confidence, 1.0)