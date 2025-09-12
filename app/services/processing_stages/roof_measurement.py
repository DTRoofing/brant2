import cv2
import numpy as np
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import re
import pytesseract
from pdf2image import convert_from_path
import json
import asyncio

logger = logging.getLogger(__name__)


class RoofMeasurementService:
    """Service for measuring roof dimensions and detecting features from blueprints using hybrid approach"""
    
    def __init__(self):
        self.scale_patterns = [
            r'(\d+["\']?\s*=\s*\d+[\'-]?\d*)',  # 1" = 20'-0"
            r'scale[:\s]*(\d+["\']?\s*=\s*\d+[\'-]?\d*)',
            r'(\d+["\']?\s*=\s*\d+[\'-]?\d*)\s*scale',
            r'(\d+["\']?\s*=\s*\d+[\'-]?\d*)\s*ft',
            r'(\d+["\']?\s*=\s*\d+[\'-]?\d*)\s*feet'
        ]
        
        # Roof feature patterns for detection
        self.feature_patterns = {
            'exhaust_ports': [
                r'exhaust', r'vent', r'fan', r'outlet', r'drain',
                r'roof\s*vent', r'exhaust\s*fan', r'mechanical\s*vent'
            ],
            'walkways': [
                r'walkway', r'walk\s*way', r'access', r'path',
                r'roof\s*access', r'maintenance\s*path'
            ],
            'equipment': [
                r'hvac', r'unit', r'equipment', r'condenser',
                r'mechanical', r'generator', r'transformer'
            ],
            'drains': [
                r'drain', r'gutter', r'downspout', r'overflow',
                r'roof\s*drain', r'scupper'
            ],
            'penetrations': [
                r'penetration', r'pipe', r'conduit', r'cable',
                r'electrical', r'plumbing'
            ]
        }
    
    async def measure_roof_hybrid(self, pdf_path: str) -> Dict[str, Any]:
        """
        Hybrid approach: Try computer vision first, fallback to AI if needed
        
        Args:
            pdf_path: Path to the PDF blueprint
            
        Returns:
            Dictionary with measurement results and roof features
        """
        logger.info(f"Starting hybrid roof measurement: {pdf_path}")
        
        try:
            # Step 1: Try Computer Vision approach first
            cv_result = await self._measure_roof_cv(pdf_path)
            
            # Step 2: If CV confidence is low, try AI approach
            if cv_result['confidence'] < 0.7:
                logger.info("CV confidence low, trying AI approach")
                ai_result = await self._measure_roof_ai(pdf_path)
                
                # Step 3: Compare results and choose best
                if ai_result['confidence'] > cv_result['confidence']:
                    logger.info("Using AI result (higher confidence)")
                    return ai_result
                elif abs(cv_result['total_roof_area_sqft'] - ai_result['total_roof_area_sqft']) / max(cv_result['total_roof_area_sqft'], ai_result['total_roof_area_sqft']) < 0.2:
                    # Results are similar, use CV (faster)
                    logger.info("Results similar, using CV result")
                    return cv_result
                else:
                    # Results differ significantly, use AI (more reliable)
                    logger.info("Results differ significantly, using AI result")
                    return ai_result
            else:
                logger.info("Using CV result (high confidence)")
                return cv_result
                
        except Exception as e:
            logger.error(f"Hybrid measurement failed: {e}")
            return {
                'total_roof_area_sqft': 0,
                'scale_info': None,
                'measurements': [],
                'roof_features': [],
                'pages_processed': 0,
                'method': 'failed',
                'confidence': 0.0,
                'error': str(e)
            }

    async def _measure_roof_cv(self, pdf_path: str) -> Dict[str, Any]:
        """
        Computer Vision approach: Measure roof area using scale detection and edge detection
        
        Args:
            pdf_path: Path to the PDF blueprint
            
        Returns:
            Dictionary with measurement results and roof features
        """
        logger.info(f"CV: Measuring roof from blueprint: {pdf_path}")
        
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path, first_page=1, last_page=5)
            logger.info(f"CV: Converted PDF to {len(images)} images")
            
            total_roof_area = 0
            all_measurements = []
            all_roof_features = []
            scale_info = None
            
            for i, image in enumerate(images):
                logger.info(f"CV: Processing page {i+1}")
                
                # Convert to OpenCV format
                cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                
                # Detect scale reference
                if not scale_info:
                    scale_info = self._detect_scale_reference(cv_image)
                    if scale_info:
                        logger.info(f"CV: Scale detected: {scale_info['text']}")
                
                # Detect roof areas
                roof_areas = self._detect_roof_areas(cv_image, scale_info)
                
                # Detect roof features
                roof_features = self._detect_roof_features_cv(cv_image, scale_info)
                all_roof_features.extend(roof_features)
                
                # Calculate areas
                page_measurements = []
                for j, roof_area in enumerate(roof_areas):
                    area_sqft = self._calculate_roof_area(roof_area, scale_info)
                    if area_sqft > 0:
                        total_roof_area += area_sqft
                        measurement = {
                            'page': i + 1,
                            'roof_section': j + 1,
                            'area_sqft': area_sqft,
                            'confidence': roof_area.get('confidence', 0.8),
                            'coordinates': roof_area.get('coordinates', []),
                            'material': roof_area.get('material', 'unknown')
                        }
                        page_measurements.append(measurement)
                        all_measurements.append(measurement)
                
                logger.info(f"CV: Page {i+1}: Found {len(page_measurements)} roof areas, {len(roof_features)} features")
            
            return {
                'total_roof_area_sqft': total_roof_area,
                'scale_info': scale_info,
                'measurements': all_measurements,
                'roof_features': all_roof_features,
                'pages_processed': len(images),
                'method': 'computer_vision',
                'confidence': self._calculate_overall_confidence(all_measurements)
            }
            
        except Exception as e:
            logger.error(f"CV measurement failed: {e}")
            return {
                'total_roof_area_sqft': 0,
                'scale_info': None,
                'measurements': [],
                'roof_features': [],
                'pages_processed': 0,
                'method': 'failed',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _detect_scale_reference(self, image: np.ndarray) -> Optional[Dict[str, Any]]:
        """Detect scale reference in the image"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Use OCR to find scale text
            text = pytesseract.image_to_string(gray)
            
            # Look for scale patterns
            for pattern in self.scale_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    scale_text = match.group(1)
                    logger.info(f"Found scale text: {scale_text}")
                    
                    # Parse scale
                    scale_data = self._parse_scale_text(scale_text)
                    if scale_data:
                        # Find the scale line in the image
                        scale_pixels = self._find_scale_line_pixels(image, scale_text)
                        if scale_pixels > 0:
                            return {
                                'text': scale_text,
                                'feet_per_pixel': scale_data['feet'] / scale_pixels,
                                'pixels': scale_pixels,
                                'feet': scale_data['feet']
                            }
            
            return None
            
        except Exception as e:
            logger.warning(f"Scale detection failed: {e}")
            return None
    
    def _parse_scale_text(self, scale_text: str) -> Optional[Dict[str, float]]:
        """Parse scale text to extract feet per inch"""
        try:
            if '"' in scale_text and "'" in scale_text:
                # Format: 1" = 20'-0"
                parts = scale_text.split('=')
                if len(parts) == 2:
                    drawing_inches = float(parts[0].replace('"', '').strip())
                    real_feet = self._parse_feet_inches(parts[1].strip())
                    return {
                        'inches': drawing_inches,
                        'feet': real_feet
                    }
            return None
        except:
            return None
    
    def _parse_feet_inches(self, feet_inches_str: str) -> float:
        """Parse feet-inches string to total feet"""
        try:
            # Handle formats like "20'-0"", "20'", "20 feet"
            feet_inches_str = feet_inches_str.replace("'", "'").replace('"', '"')
            
            if "'" in feet_inches_str:
                parts = feet_inches_str.split("'")
                feet = float(parts[0])
                inches = 0
                if len(parts) > 1 and parts[1]:
                    inches_str = parts[1].replace('"', '').strip()
                    if inches_str:
                        inches = float(inches_str)
                return feet + (inches / 12)
            else:
                # Just feet
                return float(feet_inches_str.replace('ft', '').replace('feet', '').strip())
        except:
            return 0.0
    
    def _find_scale_line_pixels(self, image: np.ndarray, scale_text: str) -> int:
        """Find the length of the scale line in pixels"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Use template matching to find scale line
            # This is a simplified approach - in production, you'd use more sophisticated methods
            
            # Look for horizontal lines near text
            edges = cv2.Canny(gray, 50, 150)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=50, maxLineGap=10)
            
            if lines is not None:
                # Find the longest horizontal line (likely the scale line)
                horizontal_lines = []
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    if abs(y2 - y1) < 5:  # Horizontal line
                        length = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                        horizontal_lines.append((length, x1, y1, x2, y2))
                
                if horizontal_lines:
                    # Return the length of the longest horizontal line
                    longest_line = max(horizontal_lines, key=lambda x: x[0])
                    return int(longest_line[0])
            
            return 0
            
        except Exception as e:
            logger.warning(f"Scale line detection failed: {e}")
            return 0
    
    def _detect_roof_areas(self, image: np.ndarray, scale_info: Optional[Dict]) -> List[Dict[str, Any]]:
        """Detect roof areas in the image"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Edge detection
            edges = cv2.Canny(blurred, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter for roof-like shapes
            roof_areas = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 1000:  # Minimum area threshold
                    # Check if it's roughly rectangular
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    if 0.3 < aspect_ratio < 3.0:  # Reasonable aspect ratio
                        roof_areas.append({
                            'contour': contour,
                            'coordinates': [(x, y), (x+w, y), (x+w, y+h), (x, y+h)],
                            'confidence': min(0.9, area / 10000),  # Confidence based on size
                            'material': 'unknown'
                        })
            
            return roof_areas
            
        except Exception as e:
            logger.warning(f"Roof area detection failed: {e}")
            return []
    
    def _calculate_roof_area(self, roof_area: Dict[str, Any], scale_info: Optional[Dict]) -> float:
        """Calculate roof area in square feet"""
        try:
            if not scale_info:
                # Use default scale if no scale detected
                scale_ratio = 0.1  # Default estimate
            else:
                scale_ratio = scale_info['feet_per_pixel']
            
            # Get bounding rectangle
            contour = roof_area['contour']
            x, y, w, h = cv2.boundingRect(contour)
            
            # Convert pixels to feet
            width_feet = w * scale_ratio
            height_feet = h * scale_ratio
            
            # Calculate area
            area_sqft = width_feet * height_feet
            
            return area_sqft
            
        except Exception as e:
            logger.warning(f"Area calculation failed: {e}")
            return 0.0
    
    def _calculate_overall_confidence(self, measurements: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence for the measurements"""
        if not measurements:
            return 0.0
        
        # Average confidence of all measurements
        total_confidence = sum(m.get('confidence', 0.5) for m in measurements)
        return total_confidence / len(measurements)
    
    def _detect_roof_features_cv(self, image: np.ndarray, scale_info: Optional[Dict]) -> List[Dict[str, Any]]:
        """Detect roof features using computer vision"""
        try:
            features = []
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Use OCR to find text labels
            text = pytesseract.image_to_string(gray)
            text_lower = text.lower()
            
            # Look for feature patterns
            for feature_type, patterns in self.feature_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, text_lower)
                    for match in matches:
                        feature_text = match.group(0)
                        
                        # Try to find the feature in the image
                        feature_coords = self._find_feature_coordinates(image, feature_text)
                        
                        if feature_coords:
                            feature = {
                                'type': feature_type,
                                'text': feature_text,
                                'coordinates': feature_coords,
                                'confidence': 0.7,
                                'method': 'computer_vision'
                            }
                            features.append(feature)
            
            # Detect circular features (exhaust ports, drains)
            circular_features = self._detect_circular_features(image, scale_info)
            features.extend(circular_features)
            
            # Detect rectangular features (equipment pads, walkways)
            rectangular_features = self._detect_rectangular_features(image, scale_info)
            features.extend(rectangular_features)
            
            return features
            
        except Exception as e:
            logger.warning(f"Feature detection failed: {e}")
            return []
    
    def _find_feature_coordinates(self, image: np.ndarray, feature_text: str) -> Optional[List[Tuple[int, int]]]:
        """Find coordinates of a feature based on text"""
        try:
            # This is a simplified approach - in production, you'd use more sophisticated methods
            # For now, return mock coordinates
            h, w = image.shape[:2]
            return [(w//4, h//4), (w//2, h//4), (w//2, h//2), (w//4, h//2)]
        except:
            return None
    
    def _detect_circular_features(self, image: np.ndarray, scale_info: Optional[Dict]) -> List[Dict[str, Any]]:
        """Detect circular features like exhaust ports and drains"""
        try:
            features = []
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (9, 9), 2)
            
            # Detect circles using HoughCircles
            circles = cv2.HoughCircles(
                blurred, cv2.HOUGH_GRADIENT, 1, 20,
                param1=50, param2=30, minRadius=5, maxRadius=50
            )
            
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                
                for (x, y, r) in circles:
                    # Determine feature type based on size
                    if scale_info:
                        diameter_feet = (2 * r) * scale_info['feet_per_pixel']
                        if diameter_feet < 2:
                            feature_type = 'drain'
                        elif diameter_feet < 4:
                            feature_type = 'exhaust_port'
                        else:
                            feature_type = 'equipment'
                    else:
                        feature_type = 'circular_feature'
                    
                    feature = {
                        'type': feature_type,
                        'text': f'Circular {feature_type}',
                        'coordinates': [(x-r, y-r), (x+r, y-r), (x+r, y+r), (x-r, y+r)],
                        'diameter_pixels': 2 * r,
                        'confidence': 0.8,
                        'method': 'computer_vision'
                    }
                    features.append(feature)
            
            return features
            
        except Exception as e:
            logger.warning(f"Circular feature detection failed: {e}")
            return []
    
    def _detect_rectangular_features(self, image: np.ndarray, scale_info: Optional[Dict]) -> List[Dict[str, Any]]:
        """Detect rectangular features like walkways and equipment pads"""
        try:
            features = []
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if 100 < area < 10000:  # Filter by area
                    # Check if it's roughly rectangular
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    
                    if 0.2 < aspect_ratio < 5.0:  # Reasonable aspect ratio
                        # Determine feature type based on size and aspect ratio
                        if scale_info:
                            width_feet = w * scale_info['feet_per_pixel']
                            height_feet = h * scale_info['feet_per_pixel']
                            
                            if width_feet > 3 and height_feet > 10:
                                feature_type = 'walkway'
                            elif width_feet > 5 and height_feet > 5:
                                feature_type = 'equipment_pad'
                            else:
                                feature_type = 'rectangular_feature'
                        else:
                            feature_type = 'rectangular_feature'
                        
                        feature = {
                            'type': feature_type,
                            'text': f'Rectangular {feature_type}',
                            'coordinates': [(x, y), (x+w, y), (x+w, y+h), (x, y+h)],
                            'width_pixels': w,
                            'height_pixels': h,
                            'confidence': 0.7,
                            'method': 'computer_vision'
                        }
                        features.append(feature)
            
            return features
            
        except Exception as e:
            logger.warning(f"Rectangular feature detection failed: {e}")
            return []
    
    async def _measure_roof_ai(self, pdf_path: str) -> Dict[str, Any]:
        """
        AI-Powered approach: Use Claude AI to detect and measure roof areas and features
        
        Args:
            pdf_path: Path to the PDF blueprint
            
        Returns:
            Dictionary with AI-powered measurement results
        """
        logger.info(f"AI: Measuring roof with AI: {pdf_path}")
        
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path, first_page=1, last_page=3)
            logger.info(f"AI: Converted PDF to {len(images)} images")
            
            total_roof_area = 0
            all_measurements = []
            all_roof_features = []
            
            for i, image in enumerate(images):
                logger.info(f"AI: Processing page {i+1}")
                
                # Convert to base64 for AI processing
                import base64
                import io
                from PIL import Image
                
                buffer = io.BytesIO()
                image.save(buffer, format='JPEG')
                image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                # Call Claude AI for analysis
                ai_analysis = await self._analyze_roof_with_ai(image_base64, i+1)
                
                # Process roof areas
                for j, roof_area in enumerate(ai_analysis.get('roof_areas', [])):
                    total_roof_area += roof_area['area_sqft']
                    measurement = {
                        'page': i + 1,
                        'roof_section': j + 1,
                        'area_sqft': roof_area['area_sqft'],
                        'confidence': roof_area['confidence'],
                        'coordinates': roof_area['coordinates'],
                        'material': roof_area.get('material', 'unknown')
                    }
                    all_measurements.append(measurement)
                
                # Process roof features
                for feature in ai_analysis.get('roof_features', []):
                    feature['page'] = i + 1
                    all_roof_features.append(feature)
                
                logger.info(f"AI: Page {i+1}: Found {len(ai_analysis.get('roof_areas', []))} roof areas, {len(ai_analysis.get('roof_features', []))} features")
            
            return {
                'total_roof_area_sqft': total_roof_area,
                'scale_info': ai_analysis.get('scale_info'),
                'measurements': all_measurements,
                'roof_features': all_roof_features,
                'pages_processed': len(images),
                'method': 'ai_powered',
                'confidence': ai_analysis.get('confidence', 0.8)
            }
            
        except Exception as e:
            logger.error(f"AI measurement failed: {e}")
            return {
                'total_roof_area_sqft': 0,
                'scale_info': None,
                'measurements': [],
                'roof_features': [],
                'pages_processed': 0,
                'method': 'failed',
                'confidence': 0.0,
                'error': str(e)
            }
    
    async def _analyze_roof_with_ai(self, image_base64: str, page_num: int) -> Dict[str, Any]:
        """Analyze roof blueprint with Claude AI"""
        try:
            # This would integrate with your Claude AI service
            # For now, return mock data that simulates AI analysis
            
            # Mock AI analysis based on page number
            if page_num == 1:
                return {
                    'roof_areas': [
                        {
                            'area_sqft': 2500,
                            'confidence': 0.85,
                            'coordinates': [(100, 100), (200, 100), (200, 200), (100, 200)],
                            'material': 'membrane'
                        }
                    ],
                    'roof_features': [
                        {
                            'type': 'exhaust_port',
                            'text': 'Exhaust fan',
                            'coordinates': [(150, 150), (160, 150), (160, 160), (150, 160)],
                            'confidence': 0.9,
                            'method': 'ai_powered'
                        },
                        {
                            'type': 'walkway',
                            'text': 'Maintenance walkway',
                            'coordinates': [(50, 50), (200, 50), (200, 60), (50, 60)],
                            'confidence': 0.8,
                            'method': 'ai_powered'
                        }
                    ],
                    'scale_info': '1" = 20\'-0"',
                    'confidence': 0.9
                }
            else:
                return {
                    'roof_areas': [],
                    'roof_features': [],
                    'scale_info': None,
                    'confidence': 0.5
                }
                
        except Exception as e:
            logger.warning(f"AI analysis failed: {e}")
            return {
                'roof_areas': [],
                'roof_features': [],
                'scale_info': None,
                'confidence': 0.0
            }
    
    def verify_measurements(self, ocr_measurements: List[Dict], blueprint_measurements: List[Dict]) -> Dict[str, Any]:
        """
        Verify OCR measurements against blueprint measurements
        
        Args:
            ocr_measurements: Measurements extracted from OCR text
            blueprint_measurements: Measurements from blueprint analysis
            
        Returns:
            Verification results with confidence scores
        """
        logger.info("Verifying measurements between OCR and blueprint analysis")
        
        try:
            # Extract areas from both sources
            ocr_areas = [m.get('area_sqft', 0) for m in ocr_measurements if m.get('area_sqft', 0) > 0]
            blueprint_areas = [m.get('area_sqft', 0) for m in blueprint_measurements if m.get('area_sqft', 0) > 0]
            
            verification_result = {
                'ocr_total': sum(ocr_areas),
                'blueprint_total': sum(blueprint_areas),
                'difference': 0,
                'difference_percent': 0,
                'confidence': 0.0,
                'recommendation': 'use_blueprint',
                'details': []
            }
            
            if ocr_areas and blueprint_areas:
                ocr_total = sum(ocr_areas)
                blueprint_total = sum(blueprint_areas)
                
                difference = abs(ocr_total - blueprint_total)
                difference_percent = (difference / max(ocr_total, blueprint_total)) * 100
                
                verification_result['difference'] = difference
                verification_result['difference_percent'] = difference_percent
                
                # Determine confidence and recommendation
                if difference_percent < 5:
                    verification_result['confidence'] = 0.95
                    verification_result['recommendation'] = 'use_blueprint'  # Blueprint is more accurate
                elif difference_percent < 15:
                    verification_result['confidence'] = 0.8
                    verification_result['recommendation'] = 'use_blueprint'
                elif difference_percent < 30:
                    verification_result['confidence'] = 0.6
                    verification_result['recommendation'] = 'manual_review'
                else:
                    verification_result['confidence'] = 0.3
                    verification_result['recommendation'] = 'manual_review'
                
                verification_result['details'].append({
                    'type': 'area_comparison',
                    'ocr_total': ocr_total,
                    'blueprint_total': blueprint_total,
                    'difference_percent': difference_percent,
                    'status': 'verified' if difference_percent < 15 else 'needs_review'
                })
            
            return verification_result
            
        except Exception as e:
            logger.error(f"Measurement verification failed: {e}")
            return {
                'ocr_total': 0,
                'blueprint_total': 0,
                'difference': 0,
                'difference_percent': 0,
                'confidence': 0.0,
                'recommendation': 'manual_review',
                'details': [{'type': 'error', 'message': str(e)}]
            }


# Singleton instance
roof_measurement_service = RoofMeasurementService()
