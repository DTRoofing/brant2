import logging
from typing import Optional
from datetime import datetime
from pathlib import Path

from app.models.processing import (
    ProcessingResult, ProcessingStage, DocumentAnalysis, 
    ExtractedContent, AIInterpretation, ValidatedData, RoofingEstimate
)
from app.services.processing_stages.document_analyzer import DocumentAnalyzer
from app.services.processing_stages.content_extractor import ContentExtractor
from app.services.processing_stages.ai_interpreter import AIInterpreter
from app.services.processing_stages.data_validator import DataValidator

logger = logging.getLogger(__name__)


class PDFProcessingPipeline:
    """Main orchestrator for the multi-stage PDF processing pipeline"""
    
    def __init__(self):
        self.document_analyzer = DocumentAnalyzer()
        self.content_extractor = ContentExtractor()
        self.ai_interpreter = AIInterpreter()
        self.data_validator = DataValidator()
    
    async def process_document(self, file_path: str, document_id: str) -> ProcessingResult:
        """
        Process a PDF document through the complete pipeline
        
        Args:
            file_path: Path to the PDF file
            document_id: Unique document identifier
            
        Returns:
            ProcessingResult with all stage results
        """
        start_time = datetime.now()
        result = ProcessingResult(
            document_id=document_id,
            stages_completed=[],
            current_stage=ProcessingStage.UPLOADED,
            errors=[]
        )
        
        try:
            logger.info(f"Starting pipeline processing for document {document_id}")
            
            # Stage 1: Document Analysis
            result.current_stage = ProcessingStage.ANALYZING
            analysis = await self._run_stage(
                "Document Analysis",
                lambda: self.document_analyzer.analyze_document(file_path),
                result
            )
            result.analysis = analysis
            result.stages_completed.append(ProcessingStage.ANALYZING)
            
            # Stage 2: Content Extraction
            result.current_stage = ProcessingStage.EXTRACTING
            content = await self._run_stage(
                "Content Extraction",
                lambda: self.content_extractor.extract_content(file_path, analysis),
                result
            )
            result.extracted_content = content
            result.stages_completed.append(ProcessingStage.EXTRACTING)
            
            # Stage 3: AI Interpretation
            result.current_stage = ProcessingStage.INTERPRETING
            interpretation = await self._run_stage(
                "AI Interpretation",
                lambda: self.ai_interpreter.interpret_content(content, analysis.document_type),
                result
            )
            result.ai_interpretation = interpretation
            result.stages_completed.append(ProcessingStage.INTERPRETING)
            
            # Stage 4: Data Validation
            result.current_stage = ProcessingStage.VALIDATING
            validated_data = await self._run_stage(
                "Data Validation",
                lambda: self.data_validator.validate_data(interpretation, content),
                result
            )
            result.validated_data = validated_data
            result.stages_completed.append(ProcessingStage.VALIDATING)
            
            # Stage 5: Generate Final Estimate
            result.current_stage = ProcessingStage.COMPLETED
            final_estimate = await self._generate_final_estimate(interpretation, validated_data)
            result.final_estimate = final_estimate
            result.stages_completed.append(ProcessingStage.COMPLETED)
            
            # Calculate processing time
            end_time = datetime.now()
            result.processing_time_seconds = (end_time - start_time).total_seconds()
            
            logger.info(f"Pipeline completed successfully for document {document_id} in {result.processing_time_seconds:.2f}s")
            
        except Exception as e:
            logger.error(f"Pipeline failed for document {document_id}: {e}")
            result.current_stage = ProcessingStage.FAILED
            result.errors.append(str(e))
            result.processing_time_seconds = (datetime.now() - start_time).total_seconds()
        
        return result
    
    async def _run_stage(self, stage_name: str, stage_func, result: ProcessingResult):
        """Run a processing stage with error handling"""
        try:
            logger.info(f"Running {stage_name} stage")
            return await stage_func()
        except Exception as e:
            logger.error(f"{stage_name} stage failed: {e}")
            result.errors.append(f"{stage_name}: {str(e)}")
            raise
    
    async def _generate_final_estimate(self, interpretation: AIInterpretation, validated_data: ValidatedData) -> RoofingEstimate:
        """Generate the final roofing estimate"""
        logger.info("Generating final roofing estimate")
        
        # Check for McDonald's metadata
        is_mcdonalds = interpretation.metadata.get('document_type') == 'mcdonalds_roofing'
        if is_mcdonalds:
            logger.info(f"Generating McDonald's estimate with metadata: {interpretation.metadata}")
        
        # Calculate total area
        total_area = interpretation.roof_area_sqft or 0
        if not total_area and validated_data.validated_measurements:
            area_measurements = [m for m in validated_data.validated_measurements if 'area' in m.get('label', '').lower()]
            if area_measurements:
                total_area = sum(m['value'] for m in area_measurements)
        
        # Get cost estimates
        cost_estimates = validated_data.cost_estimates
        estimated_cost = cost_estimates.get('total_cost', 0)
        
        # Prepare materials list
        materials_needed = []
        if interpretation.materials:
            for material in interpretation.materials:
                materials_needed.append({
                    'type': material.get('type', 'unknown'),
                    'condition': material.get('condition', 'unknown'),
                    'quantity': total_area if total_area else 0,
                    'unit': 'sqft'
                })
        
        # Generate labor estimate
        labor_estimate = {
            'estimated_hours': total_area * 0.1 if total_area else 0,  # Rough estimate
            'crew_size': 3,
            'cost_per_hour': 75,
            'total_labor_cost': cost_estimates.get('total_labor_cost', 0)
        }
        
        # Generate timeline estimate
        timeline_estimate = self._calculate_timeline(total_area, interpretation)
        
        # Calculate overall confidence
        confidence_score = (
            interpretation.confidence * 0.4 +
            validated_data.quality_score * 0.4 +
            (1.0 if total_area > 0 else 0.0) * 0.2
        )
        
        # Include McDonald's metadata in processing metadata
        processing_metadata = {
            'interpretation_confidence': interpretation.confidence,
            'validation_quality_score': validated_data.quality_score,
            'warnings': validated_data.warnings,
            'errors': validated_data.errors
        }
        
        # Add McDonald's specific metadata if present
        if is_mcdonalds:
            processing_metadata.update({
                'document_type': 'mcdonalds_roofing',
                'project_name': interpretation.metadata.get('project_name'),
                'project_number': interpretation.metadata.get('project_number'),
                'store_number': interpretation.metadata.get('store_number'),
                'location': interpretation.metadata.get('location'),
                'address': interpretation.metadata.get('address')
            })
        
        return RoofingEstimate(
            total_area_sqft=total_area,
            estimated_cost=estimated_cost,
            materials_needed=materials_needed,
            labor_estimate=labor_estimate,
            timeline_estimate=timeline_estimate,
            confidence_score=confidence_score,
            created_at=datetime.now(),
            processing_metadata=processing_metadata,
            metadata=interpretation.metadata  # Pass through all metadata
        )
    
    def _calculate_timeline(self, total_area: float, interpretation: AIInterpretation) -> str:
        """Calculate estimated project timeline"""
        if not total_area:
            return "Unable to estimate - no area data"
        
        # Base timeline calculation
        if total_area < 2000:
            base_days = 2
        elif total_area < 5000:
            base_days = 4
        elif total_area < 10000:
            base_days = 7
        else:
            base_days = 10
        
        # Adjust for complexity
        if interpretation.special_requirements:
            base_days += len(interpretation.special_requirements)
        
        if interpretation.damage_assessment and interpretation.damage_assessment.get('severity') == 'high':
            base_days += 2
        
        return f"{base_days}-{base_days + 2} business days"
    
    async def get_processing_status(self, document_id: str) -> dict:
        """Get current processing status for a document"""
        # This would typically query the database for the current status
        # For now, return a placeholder
        return {
            "document_id": document_id,
            "status": "processing",
            "current_stage": "analyzing",
            "progress_percent": 0
        }
    
    async def cancel_processing(self, document_id: str) -> bool:
        """Cancel processing for a document"""
        # This would typically update the database and stop any running tasks
        logger.info(f"Cancelling processing for document {document_id}")
        return True


# Singleton instance
pdf_pipeline = PDFProcessingPipeline()
