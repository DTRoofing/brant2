"""
Combined Qwen and YOLO processing pipeline for schematic and blueprint analysis.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
import asyncio
from datetime import datetime
import json
import io
from PIL import Image
import fitz  # PyMuPDF
import tempfile
import os

from app.services.ai_models.qwen_service import QwenService, QwenExtractionResult
from app.services.ai_models.yolo_service import YOLOService, YOLODetectionResult
from app.models.core import ProcessingResult, ProcessingStage
from app.core.config import settings

logger = logging.getLogger(__name__)


class QwenYOLOProcessor:
    """Combined processor for Qwen text extraction and YOLO visual detection"""
    
    def __init__(self):
        self.qwen_service = QwenService(api_key=settings.QWEN_API_KEY)
        self.yolo_service = YOLOService()
        self.initialized = False
        
    async def initialize(self):
        """Initialize both AI services"""
        if not self.initialized:
            await self.yolo_service.initialize()
            self.initialized = True
            logger.info("QwenYOLO processor initialized")
    
    async def process_schematic_pdf(
        self,
        pdf_content: bytes,
        document_id: str,
        document_type: str = "schematic",
        processing_options: Optional[Dict[str, Any]] = None
    ) -> ProcessingResult:
        """
        Process schematic or blueprint PDF using both Qwen and YOLO.
        
        Args:
            pdf_content: PDF file content
            document_id: Document identifier
            document_type: Type of document (schematic, blueprint, etc.)
            processing_options: Additional processing options
            
        Returns:
            ProcessingResult with combined analysis
        """
        start_time = datetime.now()
        processing_stages = []
        errors = []
        warnings = []
        
        try:
            # Initialize services if needed
            await self.initialize()
            
            # Stage 1: Qwen Text Extraction
            logger.info(f"Starting Qwen text extraction for document {document_id}")
            processing_stages.append({
                "stage": "qwen_text_extraction",
                "status": "in_progress",
                "started_at": datetime.now().isoformat()
            })
            
            qwen_result = await self.qwen_service.extract_text_from_document(
                pdf_content,
                document_type=document_type,
                extract_measurements=True,
                extract_specifications=True,
                extract_annotations=True
            )
            
            processing_stages[-1].update({
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "result_summary": {
                    "text_extracted": len(qwen_result.text_content) > 0,
                    "measurements_found": len(qwen_result.measurements),
                    "specifications_found": len(qwen_result.specifications),
                    "annotations_found": len(qwen_result.annotations)
                }
            })
            
            # Stage 2: Convert PDF to Images for YOLO
            logger.info(f"Converting PDF to images for YOLO processing")
            processing_stages.append({
                "stage": "pdf_to_image_conversion",
                "status": "in_progress",
                "started_at": datetime.now().isoformat()
            })
            
            images = await self._convert_pdf_to_images(pdf_content)
            
            processing_stages[-1].update({
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "result_summary": {
                    "pages_converted": len(images)
                }
            })
            
            # Stage 3: YOLO Visual Detection
            logger.info(f"Starting YOLO visual detection on {len(images)} pages")
            processing_stages.append({
                "stage": "yolo_detection",
                "status": "in_progress",
                "started_at": datetime.now().isoformat()
            })
            
            yolo_results = []
            for idx, image_data in enumerate(images):
                yolo_result = await self.yolo_service.detect_elements(
                    image_data,
                    confidence_threshold=0.6,
                    target_elements=None  # Detect all elements
                )
                yolo_results.append({
                    "page": idx + 1,
                    "result": yolo_result
                })
            
            total_detections = sum(len(r["result"].detected_elements) for r in yolo_results)
            processing_stages[-1].update({
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "result_summary": {
                    "total_elements_detected": total_detections,
                    "pages_analyzed": len(yolo_results)
                }
            })
            
            # Stage 4: Extract Measurements from Visual Detections
            logger.info("Extracting measurements from visual detections")
            processing_stages.append({
                "stage": "measurement_extraction",
                "status": "in_progress",
                "started_at": datetime.now().isoformat()
            })
            
            visual_measurements = []
            for page_result in yolo_results:
                measurements = await self.yolo_service.extract_measurements_from_detections(
                    page_result["result"],
                    scale_info=self._extract_scale_info(qwen_result)
                )
                if measurements["dimensions"] or measurements["areas"] or measurements["slopes"]:
                    visual_measurements.append({
                        "page": page_result["page"],
                        "measurements": measurements
                    })
            
            processing_stages[-1].update({
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "result_summary": {
                    "measurements_extracted": len(visual_measurements)
                }
            })
            
            # Stage 5: Data Synthesis
            logger.info("Synthesizing data from Qwen and YOLO results")
            processing_stages.append({
                "stage": "data_synthesis",
                "status": "in_progress",
                "started_at": datetime.now().isoformat()
            })
            
            synthesized_data = await self._synthesize_results(
                qwen_result,
                yolo_results,
                visual_measurements
            )
            
            processing_stages[-1].update({
                "status": "completed",
                "completed_at": datetime.now().isoformat()
            })
            
            # Stage 6: Generate Roofing Analysis
            logger.info("Generating comprehensive roofing analysis")
            processing_stages.append({
                "stage": "roofing_analysis",
                "status": "in_progress",
                "started_at": datetime.now().isoformat()
            })
            
            roofing_analysis = await self._generate_roofing_analysis(synthesized_data)
            
            processing_stages[-1].update({
                "status": "completed",
                "completed_at": datetime.now().isoformat()
            })
            
            # Calculate overall confidence
            confidence_scores = [
                qwen_result.confidence_score,
                *[r["result"].confidence_score for r in yolo_results]
            ]
            overall_confidence = sum(confidence_scores) / len(confidence_scores)
            
            # Prepare final result
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ProcessingResult(
                document_id=document_id,
                status="completed",
                stage="qwen_yolo_analysis_complete",
                result={
                    "document_type": document_type,
                    "text_extraction": {
                        "content": qwen_result.text_content,
                        "technical_terms": qwen_result.technical_terms,
                        "measurements": qwen_result.measurements,
                        "specifications": qwen_result.specifications,
                        "annotations": qwen_result.annotations
                    },
                    "visual_detection": {
                        "total_pages": len(yolo_results),
                        "total_elements": total_detections,
                        "element_summary": self._summarize_detections(yolo_results),
                        "visual_measurements": visual_measurements
                    },
                    "synthesized_data": synthesized_data,
                    "roofing_analysis": roofing_analysis,
                    "confidence_score": overall_confidence,
                    "processing_stages": processing_stages,
                    "processing_time": processing_time
                },
                confidence_score=overall_confidence,
                processing_time_seconds=processing_time,
                errors=errors,
                warnings=warnings,
                metadata={
                    "processor": "qwen_yolo",
                    "qwen_version": qwen_result.metadata.get("model_version"),
                    "yolo_version": yolo_results[0]["result"].metadata.get("model_version") if yolo_results else None,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Error in QwenYOLO processing: {str(e)}")
            errors.append({
                "stage": "qwen_yolo_processing",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            
            return ProcessingResult(
                document_id=document_id,
                status="failed",
                stage="qwen_yolo_processing",
                result={},
                confidence_score=0.0,
                processing_time_seconds=(datetime.now() - start_time).total_seconds(),
                errors=errors,
                warnings=warnings,
                metadata={"error": str(e)}
            )
    
    async def _convert_pdf_to_images(self, pdf_content: bytes) -> List[bytes]:
        """Convert PDF pages to images for YOLO processing"""
        images = []
        
        try:
            # Create temporary file for PDF
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                tmp_file.write(pdf_content)
                tmp_path = tmp_file.name
            
            # Open PDF with PyMuPDF
            pdf_document = fitz.open(tmp_path)
            
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                
                # Render page at high resolution (300 DPI)
                mat = fitz.Matrix(300/72, 300/72)
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image and then to bytes
                img_data = pix.tobytes("png")
                images.append(img_data)
            
            pdf_document.close()
            
            # Clean up temporary file
            os.unlink(tmp_path)
            
            logger.info(f"Converted {len(images)} PDF pages to images")
            
        except Exception as e:
            logger.error(f"Error converting PDF to images: {str(e)}")
            raise
        
        return images
    
    def _extract_scale_info(self, qwen_result: QwenExtractionResult) -> Dict[str, Any]:
        """Extract scale information from Qwen results"""
        scale_info = {
            "scale": None,
            "scale_factor": 1.0,
            "unit": "ft"
        }
        
        # Look for scale in annotations
        for annotation in qwen_result.annotations:
            text = annotation.get("text", "").lower()
            if "scale" in text and "=" in text:
                # Parse scale like "1/4\" = 1'-0\""
                try:
                    parts = text.split("=")
                    if len(parts) == 2:
                        scale_info["scale"] = text
                        # Simple scale factor calculation (would be more sophisticated in production)
                        if "1/4" in parts[0]:
                            scale_info["scale_factor"] = 48  # 1/4" = 1' means 48x scale
                        elif "1/8" in parts[0]:
                            scale_info["scale_factor"] = 96  # 1/8" = 1' means 96x scale
                except Exception:
                    pass
        
        # Also check technical terms
        for term in qwen_result.technical_terms:
            if "scale" in term.get("term", "").lower():
                context = term.get("context", "")
                if "=" in context:
                    scale_info["scale"] = context
        
        return scale_info
    
    def _summarize_detections(self, yolo_results: List[Dict[str, Any]]) -> Dict[str, int]:
        """Summarize detection counts by element type"""
        summary = {}
        
        for page_result in yolo_results:
            for element in page_result["result"].detected_elements:
                element_type = element.element_type
                summary[element_type] = summary.get(element_type, 0) + 1
        
        return summary
    
    async def _synthesize_results(
        self,
        qwen_result: QwenExtractionResult,
        yolo_results: List[Dict[str, Any]],
        visual_measurements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Synthesize results from both Qwen and YOLO"""
        
        # Combine measurements from both sources
        all_measurements = {
            "text_based": qwen_result.measurements,
            "visual_based": visual_measurements,
            "combined": []
        }
        
        # Merge measurements with confidence weighting
        measurement_map = {}
        
        # Add text-based measurements
        for measurement in qwen_result.measurements:
            key = f"{measurement['type']}_{measurement.get('description', '')}"
            measurement_map[key] = measurement
        
        # Add or update with visual measurements
        for page_data in visual_measurements:
            for mtype, mlist in page_data["measurements"].items():
                if isinstance(mlist, list):
                    for measurement in mlist:
                        # Create a standardized measurement format
                        std_measurement = {
                            "type": mtype.rstrip("s"),  # Remove plural
                            "value": measurement.get("value"),
                            "unit": measurement.get("unit", ""),
                            "confidence": measurement.get("confidence", 0.5),
                            "source": "visual",
                            "page": page_data["page"]
                        }
                        
                        # Check if we have a similar measurement from text
                        key = f"{std_measurement['type']}_{std_measurement.get('value', '')}"
                        if key in measurement_map:
                            # Average the confidence if we have both sources
                            existing = measurement_map[key]
                            existing["confidence"] = (existing["confidence"] + std_measurement["confidence"]) / 2
                            existing["source"] = "combined"
                        else:
                            measurement_map[key] = std_measurement
        
        all_measurements["combined"] = list(measurement_map.values())
        
        # Extract roof components
        roof_components = {
            "primary_structure": self._identify_primary_structure(qwen_result, yolo_results),
            "features": self._extract_roof_features(yolo_results),
            "materials": qwen_result.specifications,
            "special_elements": self._identify_special_elements(yolo_results)
        }
        
        # Generate relationships between elements
        element_relationships = []
        for page_result in yolo_results:
            relationships = await self.yolo_service.generate_element_relationships(
                page_result["result"]
            )
            element_relationships.extend(relationships)
        
        return {
            "measurements": all_measurements,
            "roof_components": roof_components,
            "element_relationships": element_relationships,
            "annotations": qwen_result.annotations,
            "technical_summary": self._generate_technical_summary(qwen_result, yolo_results)
        }
    
    def _identify_primary_structure(
        self,
        qwen_result: QwenExtractionResult,
        yolo_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Identify primary roof structure from combined results"""
        
        structure = {
            "type": "unknown",
            "complexity": "medium",
            "sections": 0
        }
        
        # Check YOLO detections for roof outlines
        for page_result in yolo_results:
            roof_outlines = [
                e for e in page_result["result"].detected_elements 
                if e.element_type == "roof_outline"
            ]
            for outline in roof_outlines:
                if "shape" in outline.attributes:
                    structure["type"] = outline.attributes["shape"]
                if "sections" in outline.attributes:
                    structure["sections"] = max(structure["sections"], outline.attributes["sections"])
        
        # Check Qwen technical terms
        roof_types = ["hip", "gable", "mansard", "flat", "shed", "gambrel"]
        for term in qwen_result.technical_terms:
            term_lower = term["term"].lower()
            for roof_type in roof_types:
                if roof_type in term_lower:
                    structure["type"] = roof_type
                    break
        
        # Assess complexity based on features
        complex_features = ["valley", "dormer", "turret", "cricket"]
        complexity_score = 0
        
        for page_result in yolo_results:
            for element in page_result["result"].detected_elements:
                if element.element_type in complex_features:
                    complexity_score += 1
        
        if complexity_score >= 3:
            structure["complexity"] = "high"
        elif complexity_score >= 1:
            structure["complexity"] = "medium"
        else:
            structure["complexity"] = "low"
        
        return structure
    
    def _extract_roof_features(self, yolo_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract all roof features from YOLO results"""
        features = []
        feature_types = [
            "ridge", "valley", "hip", "gable", "dormer", 
            "skylight", "vent", "chimney", "flashing", "gutter"
        ]
        
        for page_result in yolo_results:
            for element in page_result["result"].detected_elements:
                if element.element_type in feature_types:
                    features.append({
                        "type": element.element_type,
                        "page": page_result["page"],
                        "location": element.bounding_box.center,
                        "attributes": element.attributes,
                        "confidence": element.confidence
                    })
        
        return features
    
    def _identify_special_elements(self, yolo_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify special or unique elements"""
        special_elements = []
        special_types = ["turret", "cupola", "widow_walk", "parapet", "clerestory"]
        
        for page_result in yolo_results:
            for element in page_result["result"].detected_elements:
                # Check if it's a special type or has special attributes
                if (element.element_type in special_types or 
                    element.attributes.get("special", False)):
                    special_elements.append({
                        "type": element.element_type,
                        "page": page_result["page"],
                        "description": element.related_text or element.element_type,
                        "attributes": element.attributes,
                        "confidence": element.confidence
                    })
        
        return special_elements
    
    def _generate_technical_summary(
        self,
        qwen_result: QwenExtractionResult,
        yolo_results: List[Dict[str, Any]]
    ) -> str:
        """Generate a technical summary of the document"""
        
        # Count key elements
        total_measurements = len(qwen_result.measurements)
        total_specifications = len(qwen_result.specifications)
        total_visual_elements = sum(
            len(r["result"].detected_elements) for r in yolo_results
        )
        
        # Find key measurements
        areas = [m for m in qwen_result.measurements if m["type"] == "area"]
        total_area = sum(m["value"] for m in areas) if areas else 0
        
        summary = f"""Technical Document Analysis Summary:
- Document Pages: {len(yolo_results)}
- Text-based Measurements: {total_measurements}
- Material Specifications: {total_specifications}
- Visual Elements Detected: {total_visual_elements}
"""
        
        if total_area > 0:
            summary += f"- Total Roof Area: {total_area} sq ft\n"
        
        # Add roof type if identified
        for term in qwen_result.technical_terms:
            if "roof" in term["term"].lower():
                summary += f"- Roof Type: {term['term']}\n"
                break
        
        return summary
    
    async def _generate_roofing_analysis(self, synthesized_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive roofing analysis from synthesized data"""
        
        measurements = synthesized_data["measurements"]["combined"]
        components = synthesized_data["roof_components"]
        
        # Calculate total area
        area_measurements = [m for m in measurements if m["type"] == "area"]
        total_area = sum(m["value"] for m in area_measurements) if area_measurements else 0
        
        # Determine primary pitch
        slope_measurements = [m for m in measurements if m["type"] == "slope"]
        primary_pitch = slope_measurements[0]["value"] if slope_measurements else "Unknown"
        
        # Count key features
        feature_counts = {}
        for feature in components["features"]:
            ftype = feature["type"]
            feature_counts[ftype] = feature_counts.get(ftype, 0) + 1
        
        # Generate material recommendations based on specifications
        material_recommendations = []
        for spec in components["materials"]:
            if spec["category"] == "shingles":
                material_recommendations.append({
                    "category": "Primary Roofing",
                    "recommendation": spec["specification"],
                    "details": spec["details"]
                })
        
        # Calculate complexity factor
        complexity_factors = {
            "low": 1.0,
            "medium": 1.15,
            "high": 1.3
        }
        complexity = components["primary_structure"]["complexity"]
        complexity_factor = complexity_factors.get(complexity, 1.15)
        
        # Estimate quantities
        shingle_squares = (total_area / 100) * 1.1 if total_area > 0 else 0  # 10% waste
        
        return {
            "roof_characteristics": {
                "type": components["primary_structure"]["type"],
                "complexity": complexity,
                "total_area": total_area,
                "primary_pitch": primary_pitch,
                "sections": components["primary_structure"]["sections"]
            },
            "feature_summary": feature_counts,
            "material_analysis": {
                "recommendations": material_recommendations,
                "estimated_quantities": {
                    "shingles": {
                        "squares": round(shingle_squares, 1),
                        "bundles": int(shingle_squares * 3) + 1
                    },
                    "underlayment": {
                        "rolls": int(shingle_squares / 10) + 1
                    }
                }
            },
            "special_considerations": [
                annotation["text"] 
                for annotation in synthesized_data["annotations"] 
                if annotation.get("importance") == "high"
            ],
            "complexity_factor": complexity_factor,
            "confidence_metrics": {
                "measurement_confidence": sum(m["confidence"] for m in measurements) / len(measurements) if measurements else 0,
                "feature_detection_confidence": sum(f["confidence"] for f in components["features"]) / len(components["features"]) if components["features"] else 0
            }
        }