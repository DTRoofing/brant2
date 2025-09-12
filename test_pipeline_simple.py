#!/usr/bin/env python3
"""
Simplified test script for the PDF processing pipeline
This version works without external API dependencies
"""

import asyncio
import sys
from pathlib import Path
import logging

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock the external services for testing
class MockGoogleService:
    def __init__(self):
        self.document_ai_client = None
        self.storage_client = None
        self.vision_client = None
    
    async def process_document_with_ai(self, file_path: str):
        """Mock Document AI processing"""
        logger.info(f"Mock Google Document AI processing: {file_path}")
        return {
            'text': 'Mock extracted text from Document AI',
            'entities': [
                {'text': '2500 sq ft', 'confidence': 0.9, 'type': 'measurement'},
                {'text': 'asphalt shingles', 'confidence': 0.8, 'type': 'material'}
            ],
            'tables': [],
            'measurements': [
                {'text': '2500 sq ft', 'confidence': 0.9}
            ]
        }
    
    async def analyze_image_with_vision(self, file_path: str):
        """Mock Vision API processing"""
        logger.info(f"Mock Google Vision API processing: {file_path}")
        return {
            'text': 'Mock text from Vision API',
            'annotations': []
        }

class MockClaudeService:
    def __init__(self):
        self.client = None
    
    async def analyze_text_for_estimate(self, text: str):
        """Mock Claude AI analysis"""
        logger.info("Mock Claude AI analysis")
        return {
            'roof_area_sqft': 2500.0,
            'roof_pitch': '4/12',
            'materials': [
                {'type': 'asphalt_shingles', 'condition': 'new'}
            ],
            'measurements': [
                {'label': 'main_roof', 'value': 2500, 'unit': 'sqft'}
            ],
            'confidence': 0.85
        }

# Mock the services
import app.services.google_services as google_services
import app.services.claude_service as claude_service

google_services.google_service = MockGoogleService()
claude_service.claude_service = MockClaudeService()

# Now import the pipeline
from services.pdf_pipeline import pdf_pipeline
from models.processing import DocumentType


async def test_pipeline():
    """Test the new pipeline with a sample PDF"""
    
    # Test with the McDonald's document
    test_pdf_path = "tests/mcdonalds collection/24-0014_McDonalds042-3271_smallerset.pdf"
    
    if not Path(test_pdf_path).exists():
        print(f"❌ Test PDF not found at {test_pdf_path}")
        print("Please check the file path and try again.")
        return
    
    print("🚀 Testing new PDF processing pipeline...")
    print(f"📄 Processing: {test_pdf_path}")
    print(f"📁 File size: {Path(test_pdf_path).stat().st_size / 1024 / 1024:.2f} MB")
    
    try:
        # Process the document
        result = await pdf_pipeline.process_document(test_pdf_path, "test-doc-123")
        
        print("\n✅ Pipeline completed!")
        print(f"📊 Stages completed: {[stage.value for stage in result.stages_completed]}")
        print(f"⏱️  Processing time: {result.processing_time_seconds:.2f} seconds")
        
        if result.errors:
            print(f"⚠️  Errors: {result.errors}")
        
        if result.analysis:
            print(f"\n🔍 Document Analysis:")
            print(f"   Type: {result.analysis.document_type.value}")
            print(f"   Confidence: {result.analysis.confidence:.2f}")
            print(f"   Strategy: {result.analysis.processing_strategy}")
        
        if result.extracted_content:
            print(f"\n📝 Content Extraction:")
            print(f"   Text length: {len(result.extracted_content.text)} characters")
            print(f"   Method: {result.extracted_content.extraction_method}")
            print(f"   Confidence: {result.extracted_content.confidence:.2f}")
            print(f"   Measurements found: {len(result.extracted_content.measurements)}")
            if result.extracted_content.measurements:
                for i, measurement in enumerate(result.extracted_content.measurements[:3]):
                    print(f"     {i+1}. {measurement}")
        
        if result.ai_interpretation:
            print(f"\n🤖 AI Interpretation:")
            print(f"   Roof area: {result.ai_interpretation.roof_area_sqft} sqft")
            print(f"   Roof pitch: {result.ai_interpretation.roof_pitch}")
            print(f"   Materials: {len(result.ai_interpretation.materials)}")
            if result.ai_interpretation.materials:
                for material in result.ai_interpretation.materials:
                    print(f"     - {material.get('type', 'unknown')} ({material.get('condition', 'unknown')})")
            print(f"   Confidence: {result.ai_interpretation.confidence:.2f}")
        
        if result.validated_data:
            print(f"\n✅ Data Validation:")
            print(f"   Quality score: {result.validated_data.quality_score:.2f}")
            print(f"   Warnings: {len(result.validated_data.warnings)}")
            print(f"   Errors: {len(result.validated_data.errors)}")
            if result.validated_data.warnings:
                for warning in result.validated_data.warnings[:3]:
                    print(f"     ⚠️  {warning}")
        
        if result.final_estimate:
            print(f"\n💰 Final Estimate:")
            print(f"   Total area: {result.final_estimate.total_area_sqft} sqft")
            print(f"   Estimated cost: ${result.final_estimate.estimated_cost:,.2f}")
            print(f"   Timeline: {result.final_estimate.timeline_estimate}")
            print(f"   Confidence: {result.final_estimate.confidence_score:.2f}")
            if result.final_estimate.materials_needed:
                print(f"   Materials needed:")
                for material in result.final_estimate.materials_needed:
                    print(f"     - {material.get('type', 'unknown')}: {material.get('quantity', 0)} {material.get('unit', 'sqft')}")
        
        print(f"\n🎯 Pipeline Summary:")
        print(f"   ✅ Successfully processed {test_pdf_path}")
        print(f"   📊 Completed {len(result.stages_completed)} stages")
        print(f"   ⏱️  Total time: {result.processing_time_seconds:.2f}s")
        print(f"   🎯 Final confidence: {result.final_estimate.confidence_score:.2f}" if result.final_estimate else "   ❌ No final estimate generated")
        
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_pipeline())
