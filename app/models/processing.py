from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime


class DocumentType(str, Enum):
    """Types of documents we can process"""
    BLUEPRINT = "blueprint"
    INSPECTION_REPORT = "inspection_report"
    PHOTO = "photo"
    ESTIMATE = "estimate"
    MCDONALDS_ROOFING = "mcdonalds_roofing"
    UNKNOWN = "unknown"


class ProcessingStage(str, Enum):
    """Processing pipeline stages"""
    UPLOADED = "uploaded"
    ANALYZING = "analyzing"
    EXTRACTING = "extracting"
    INTERPRETING = "interpreting"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentAnalysis(BaseModel):
    """Results from document analysis stage"""
    document_type: DocumentType
    confidence: float
    processing_strategy: str
    metadata: Dict[str, Any] = {}


class ExtractedContent(BaseModel):
    """Results from content extraction stage"""
    text: str
    images: List[Dict[str, Any]] = []
    measurements: List[Dict[str, Any]] = []
    tables: List[Dict[str, Any]] = []
    entities: List[Dict[str, Any]] = []
    extraction_method: str
    confidence: float
    metadata: Dict[str, Any] = {}  # For document-specific metadata like McDonald's info
    roof_features: List[Dict[str, Any]] = []  # Optional roof features
    verification_result: Dict[str, Any] = {}  # Optional verification data


class AIInterpretation(BaseModel):
    """Results from AI interpretation stage"""
    roof_area_sqft: Optional[float] = None
    roof_pitch: Optional[str] = None
    materials: List[Dict[str, Any]] = []
    measurements: List[Dict[str, Any]] = []
    damage_assessment: Optional[Dict[str, Any]] = None
    special_requirements: List[str] = []
    roof_features: List[Dict[str, Any]] = []
    complexity_factors: List[str] = []
    confidence: float
    interpretation_method: str
    metadata: Dict[str, Any] = {}  # For document-specific metadata like McDonald's info


class ValidatedData(BaseModel):
    """Results from validation stage"""
    validated_measurements: List[Dict[str, Any]] = []
    cost_estimates: Dict[str, float] = {}
    material_recommendations: List[Dict[str, Any]] = []
    quality_score: float
    warnings: List[str] = []
    errors: List[str] = []


class RoofingEstimate(BaseModel):
    """Final roofing estimate result"""
    total_area_sqft: float
    estimated_cost: float
    materials_needed: List[Dict[str, Any]]
    labor_estimate: Dict[str, Any]
    timeline_estimate: str
    confidence_score: float
    created_at: datetime
    processing_metadata: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}  # For document-specific metadata like McDonald's info


class ProcessingResult(BaseModel):
    """Complete processing result"""
    document_id: str
    stages_completed: List[ProcessingStage]
    current_stage: ProcessingStage
    analysis: Optional[DocumentAnalysis] = None
    extracted_content: Optional[ExtractedContent] = None
    ai_interpretation: Optional[AIInterpretation] = None
    validated_data: Optional[ValidatedData] = None
    final_estimate: Optional[RoofingEstimate] = None
    errors: List[str] = []
    processing_time_seconds: Optional[float] = None
