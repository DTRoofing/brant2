"""
YOLO model service for visual element detection in blueprint and schematic PDFs.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
import json
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from PIL import Image
import io
import asyncio
from tenacity import retry, wait_exponential, stop_after_attempt

logger = logging.getLogger(__name__)

@dataclass
class BoundingBox:
    """Bounding box for detected element"""
    x1: int
    y1: int
    x2: int
    y2: int
    confidence: float
    
    @property
    def width(self) -> int:
        return self.x2 - self.x1
    
    @property
    def height(self) -> int:
        return self.y2 - self.y1
    
    @property
    def center(self) -> Tuple[int, int]:
        return ((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)
    
    @property
    def area(self) -> int:
        return self.width * self.height


@dataclass
class DetectedElement:
    """Detected visual element from YOLO"""
    element_type: str
    bounding_box: BoundingBox
    attributes: Dict[str, Any]
    related_text: Optional[str] = None
    confidence: float = 0.0


@dataclass
class YOLODetectionResult:
    """Result from YOLO visual detection"""
    detected_elements: List[DetectedElement]
    image_dimensions: Tuple[int, int]
    processing_time: float
    confidence_score: float
    metadata: Dict[str, Any]


class YOLOService:
    """Service for visual element detection in technical drawings using YOLO"""
    
    # Roofing-specific element classes
    ELEMENT_CLASSES = {
        "roof_outline": "Roof Outline",
        "dimension_line": "Dimension Line",
        "measurement_text": "Measurement Text",
        "roof_section": "Roof Section",
        "valley": "Valley",
        "ridge": "Ridge",
        "hip": "Hip",
        "gable": "Gable",
        "dormer": "Dormer",
        "skylight": "Skylight",
        "vent": "Roof Vent",
        "chimney": "Chimney",
        "flashing": "Flashing Detail",
        "gutter": "Gutter",
        "downspout": "Downspout",
        "annotation": "Annotation",
        "detail_callout": "Detail Callout",
        "north_arrow": "North Arrow",
        "scale_indicator": "Scale Indicator",
        "title_block": "Title Block",
        "revision_cloud": "Revision Cloud",
        "material_hatch": "Material Hatch Pattern",
        "slope_arrow": "Slope Arrow"
    }
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize YOLO service.
        
        Args:
            model_path: Path to YOLO model weights (optional)
        """
        self.model_path = model_path or "yolo-roofing-v1.pt"
        self.model = None
        
    async def initialize(self):
        """Initialize YOLO model"""
        # In production, load actual YOLO model
        logger.info(f"Initializing YOLO model from {self.model_path}")
        self.model = "MockYOLOModel"  # Placeholder
        
    @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
    async def detect_elements(
        self,
        image_data: bytes,
        confidence_threshold: float = 0.5,
        nms_threshold: float = 0.4,
        target_elements: Optional[List[str]] = None
    ) -> YOLODetectionResult:
        """
        Detect visual elements in blueprint/schematic images.
        
        Args:
            image_data: Image data as bytes
            confidence_threshold: Minimum confidence for detections
            nms_threshold: Non-maximum suppression threshold
            target_elements: Specific elements to detect (None = all)
            
        Returns:
            YOLODetectionResult with detected elements
        """
        start_time = datetime.now()
        
        try:
            # Convert bytes to image
            image = Image.open(io.BytesIO(image_data))
            image_dimensions = image.size
            
            logger.info(f"Processing image of size {image_dimensions}")
            
            # Simulate YOLO detection
            # In production, this would use actual YOLO inference
            await asyncio.sleep(1.5)
            
            # Mock detected elements
            detected_elements = self._simulate_detection(
                image_dimensions,
                confidence_threshold,
                target_elements
            )
            
            # Apply non-maximum suppression
            detected_elements = self._apply_nms(detected_elements, nms_threshold)
            
            # Calculate overall confidence
            overall_confidence = np.mean([e.confidence for e in detected_elements]) if detected_elements else 0.0
            
            result = YOLODetectionResult(
                detected_elements=detected_elements,
                image_dimensions=image_dimensions,
                processing_time=(datetime.now() - start_time).total_seconds(),
                confidence_score=overall_confidence,
                metadata={
                    "model_version": "yolo-roofing-v1",
                    "confidence_threshold": confidence_threshold,
                    "nms_threshold": nms_threshold,
                    "detection_timestamp": datetime.now().isoformat()
                }
            )
            
            logger.info(f"YOLO detection completed: {len(detected_elements)} elements found")
            return result
            
        except Exception as e:
            logger.error(f"Error during YOLO detection: {str(e)}")
            raise
    
    def _simulate_detection(
        self,
        image_dimensions: Tuple[int, int],
        confidence_threshold: float,
        target_elements: Optional[List[str]]
    ) -> List[DetectedElement]:
        """Simulate element detection (mock implementation)"""
        
        width, height = image_dimensions
        detected_elements = []
        
        # Simulate roof outline detection
        roof_outline = DetectedElement(
            element_type="roof_outline",
            bounding_box=BoundingBox(
                x1=int(width * 0.1),
                y1=int(height * 0.1),
                x2=int(width * 0.9),
                y2=int(height * 0.8),
                confidence=0.95
            ),
            attributes={
                "shape": "complex_hip",
                "sections": 4,
                "has_valleys": True
            },
            confidence=0.95
        )
        detected_elements.append(roof_outline)
        
        # Simulate dimension lines
        dimension_lines = [
            DetectedElement(
                element_type="dimension_line",
                bounding_box=BoundingBox(
                    x1=int(width * 0.1),
                    y1=int(height * 0.85),
                    x2=int(width * 0.9),
                    y2=int(height * 0.87),
                    confidence=0.92
                ),
                attributes={
                    "orientation": "horizontal",
                    "measurement": "48'-0\"",
                    "scale": "1/4\" = 1'-0\""
                },
                related_text="48'-0\"",
                confidence=0.92
            ),
            DetectedElement(
                element_type="dimension_line",
                bounding_box=BoundingBox(
                    x1=int(width * 0.05),
                    y1=int(height * 0.1),
                    x2=int(width * 0.07),
                    y2=int(height * 0.8),
                    confidence=0.91
                ),
                attributes={
                    "orientation": "vertical",
                    "measurement": "32'-6\"",
                    "scale": "1/4\" = 1'-0\""
                },
                related_text="32'-6\"",
                confidence=0.91
            )
        ]
        detected_elements.extend(dimension_lines)
        
        # Simulate roof features
        roof_features = [
            DetectedElement(
                element_type="ridge",
                bounding_box=BoundingBox(
                    x1=int(width * 0.3),
                    y1=int(height * 0.3),
                    x2=int(width * 0.7),
                    y2=int(height * 0.35),
                    confidence=0.88
                ),
                attributes={
                    "length_estimate": "40 ft",
                    "type": "main_ridge"
                },
                confidence=0.88
            ),
            DetectedElement(
                element_type="valley",
                bounding_box=BoundingBox(
                    x1=int(width * 0.2),
                    y1=int(height * 0.4),
                    x2=int(width * 0.4),
                    y2=int(height * 0.6),
                    confidence=0.86
                ),
                attributes={
                    "angle": "45 degrees",
                    "type": "open_valley"
                },
                confidence=0.86
            ),
            DetectedElement(
                element_type="dormer",
                bounding_box=BoundingBox(
                    x1=int(width * 0.6),
                    y1=int(height * 0.4),
                    x2=int(width * 0.75),
                    y2=int(height * 0.55),
                    confidence=0.84
                ),
                attributes={
                    "type": "shed_dormer",
                    "width": "12 ft",
                    "has_window": True
                },
                confidence=0.84
            )
        ]
        detected_elements.extend(roof_features)
        
        # Simulate annotations and callouts
        annotations = [
            DetectedElement(
                element_type="annotation",
                bounding_box=BoundingBox(
                    x1=int(width * 0.7),
                    y1=int(height * 0.7),
                    x2=int(width * 0.95),
                    y2=int(height * 0.78),
                    confidence=0.90
                ),
                attributes={
                    "type": "material_spec",
                    "content": "30-year architectural shingles"
                },
                related_text="30-year architectural shingles",
                confidence=0.90
            ),
            DetectedElement(
                element_type="slope_arrow",
                bounding_box=BoundingBox(
                    x1=int(width * 0.45),
                    y1=int(height * 0.45),
                    x2=int(width * 0.55),
                    y2=int(height * 0.5),
                    confidence=0.87
                ),
                attributes={
                    "slope": "6:12",
                    "direction": "north"
                },
                related_text="6:12",
                confidence=0.87
            )
        ]
        detected_elements.extend(annotations)
        
        # Filter by confidence threshold
        detected_elements = [
            e for e in detected_elements 
            if e.confidence >= confidence_threshold
        ]
        
        # Filter by target elements if specified
        if target_elements:
            detected_elements = [
                e for e in detected_elements 
                if e.element_type in target_elements
            ]
        
        return detected_elements
    
    def _apply_nms(
        self,
        elements: List[DetectedElement],
        nms_threshold: float
    ) -> List[DetectedElement]:
        """Apply non-maximum suppression to remove overlapping detections"""
        
        if not elements:
            return elements
        
        # Group elements by type
        elements_by_type = {}
        for element in elements:
            if element.element_type not in elements_by_type:
                elements_by_type[element.element_type] = []
            elements_by_type[element.element_type].append(element)
        
        # Apply NMS within each type
        final_elements = []
        for element_type, type_elements in elements_by_type.items():
            # Sort by confidence
            type_elements.sort(key=lambda x: x.confidence, reverse=True)
            
            kept_elements = []
            for element in type_elements:
                # Check overlap with kept elements
                keep = True
                for kept in kept_elements:
                    iou = self._calculate_iou(
                        element.bounding_box,
                        kept.bounding_box
                    )
                    if iou > nms_threshold:
                        keep = False
                        break
                
                if keep:
                    kept_elements.append(element)
            
            final_elements.extend(kept_elements)
        
        return final_elements
    
    def _calculate_iou(self, box1: BoundingBox, box2: BoundingBox) -> float:
        """Calculate intersection over union of two bounding boxes"""
        
        # Calculate intersection
        x1 = max(box1.x1, box2.x1)
        y1 = max(box1.y1, box2.y1)
        x2 = min(box1.x2, box2.x2)
        y2 = min(box1.y2, box2.y2)
        
        if x2 < x1 or y2 < y1:
            return 0.0
        
        intersection = (x2 - x1) * (y2 - y1)
        union = box1.area + box2.area - intersection
        
        return intersection / union if union > 0 else 0.0
    
    async def extract_measurements_from_detections(
        self,
        detection_result: YOLODetectionResult,
        scale_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract measurements from detected elements.
        
        Args:
            detection_result: YOLO detection results
            scale_info: Scale information from drawing
            
        Returns:
            Extracted measurements and calculations
        """
        measurements = {
            "dimensions": [],
            "areas": [],
            "lengths": [],
            "slopes": [],
            "counts": {}
        }
        
        # Extract dimension line measurements
        dimension_elements = [
            e for e in detection_result.detected_elements 
            if e.element_type == "dimension_line"
        ]
        
        for dim_element in dimension_elements:
            if "measurement" in dim_element.attributes:
                measurements["dimensions"].append({
                    "value": dim_element.attributes["measurement"],
                    "orientation": dim_element.attributes.get("orientation"),
                    "location": dim_element.bounding_box.center,
                    "confidence": dim_element.confidence
                })
        
        # Extract slope information
        slope_elements = [
            e for e in detection_result.detected_elements 
            if e.element_type == "slope_arrow"
        ]
        
        for slope_element in slope_elements:
            if "slope" in slope_element.attributes:
                measurements["slopes"].append({
                    "value": slope_element.attributes["slope"],
                    "direction": slope_element.attributes.get("direction"),
                    "location": slope_element.bounding_box.center,
                    "confidence": slope_element.confidence
                })
        
        # Count roof features
        feature_types = ["ridge", "valley", "hip", "dormer", "skylight", "vent"]
        for feature_type in feature_types:
            count = len([
                e for e in detection_result.detected_elements 
                if e.element_type == feature_type
            ])
            if count > 0:
                measurements["counts"][feature_type] = count
        
        # Estimate areas from roof outlines
        roof_outlines = [
            e for e in detection_result.detected_elements 
            if e.element_type == "roof_outline"
        ]
        
        if roof_outlines and scale_info:
            # Calculate approximate area based on bounding box and scale
            for outline in roof_outlines:
                bbox = outline.bounding_box
                pixel_area = bbox.area
                
                # Convert to real area using scale
                # This is simplified; actual implementation would be more sophisticated
                if "scale_factor" in scale_info:
                    real_area = pixel_area * (scale_info["scale_factor"] ** 2)
                    measurements["areas"].append({
                        "value": real_area,
                        "unit": "sq ft",
                        "shape": outline.attributes.get("shape"),
                        "confidence": outline.confidence * 0.8  # Reduce confidence for estimates
                    })
        
        return measurements
    
    async def generate_element_relationships(
        self,
        detection_result: YOLODetectionResult
    ) -> List[Dict[str, Any]]:
        """
        Analyze spatial relationships between detected elements.
        
        Args:
            detection_result: YOLO detection results
            
        Returns:
            List of element relationships
        """
        relationships = []
        elements = detection_result.detected_elements
        
        # Find measurements near roof sections
        roof_sections = [e for e in elements if e.element_type in ["roof_outline", "roof_section"]]
        dimension_lines = [e for e in elements if e.element_type == "dimension_line"]
        
        for section in roof_sections:
            for dim_line in dimension_lines:
                # Check if dimension line is near roof section
                distance = self._calculate_distance(
                    section.bounding_box.center,
                    dim_line.bounding_box.center
                )
                
                if distance < 100:  # Threshold in pixels
                    relationships.append({
                        "type": "measurement_association",
                        "element1": {
                            "type": section.element_type,
                            "id": id(section)
                        },
                        "element2": {
                            "type": dim_line.element_type,
                            "id": id(dim_line),
                            "measurement": dim_line.attributes.get("measurement")
                        },
                        "confidence": min(section.confidence, dim_line.confidence)
                    })
        
        # Find valleys between roof sections
        valleys = [e for e in elements if e.element_type == "valley"]
        
        for valley in valleys:
            adjacent_sections = []
            for section in roof_sections:
                if self._are_adjacent(valley.bounding_box, section.bounding_box):
                    adjacent_sections.append(section)
            
            if len(adjacent_sections) >= 2:
                relationships.append({
                    "type": "valley_connection",
                    "valley": {
                        "id": id(valley),
                        "angle": valley.attributes.get("angle")
                    },
                    "connected_sections": [
                        {"type": s.element_type, "id": id(s)} 
                        for s in adjacent_sections
                    ],
                    "confidence": valley.confidence
                })
        
        return relationships
    
    def _calculate_distance(self, point1: Tuple[int, int], point2: Tuple[int, int]) -> float:
        """Calculate Euclidean distance between two points"""
        return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5
    
    def _are_adjacent(self, box1: BoundingBox, box2: BoundingBox, threshold: int = 50) -> bool:
        """Check if two bounding boxes are adjacent"""
        # Expand boxes by threshold
        expanded_box1 = BoundingBox(
            x1=box1.x1 - threshold,
            y1=box1.y1 - threshold,
            x2=box1.x2 + threshold,
            y2=box1.y2 + threshold,
            confidence=box1.confidence
        )
        
        # Check intersection
        return self._calculate_iou(expanded_box1, box2) > 0