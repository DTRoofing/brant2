#!/usr/bin/env python3
"""
Test script for the new PDF processing pipeline
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

from services.pdf_pipeline import pdf_pipeline
from models.processing import DocumentType


async def test_pipeline():
    """Test the new pipeline with a sample PDF"""
    
    # Test with the McDonald's document
    test_pdf_path = "tests/mcdonalds collection/24-0014_McDonalds042-3271_smallerset.pdf"
    
    if not Path(test_pdf_path).exists():
        print(f"Test PDF not found at {test_pdf_path}")
        print("Please place a test PDF file at this location and try again.")
        return
    
    print("🚀 Testing new PDF processing pipeline...")
    print(f"📄 Processing: {test_pdf_path}")
    
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
        
        if result.ai_interpretation:
            print(f"\n🤖 AI Interpretation:")
            print(f"   Roof area: {result.ai_interpretation.roof_area_sqft} sqft")
            print(f"   Materials: {len(result.ai_interpretation.materials)}")
            print(f"   Confidence: {result.ai_interpretation.confidence:.2f}")
        
        if result.validated_data:
            print(f"\n✅ Data Validation:")
            print(f"   Quality score: {result.validated_data.quality_score:.2f}")
            print(f"   Warnings: {len(result.validated_data.warnings)}")
            print(f"   Errors: {len(result.validated_data.errors)}")
        
        if result.final_estimate:
            print(f"\n💰 Final Estimate:")
            print(f"   Total area: {result.final_estimate.total_area_sqft} sqft")
            print(f"   Estimated cost: ${result.final_estimate.estimated_cost:,.2f}")
            print(f"   Timeline: {result.final_estimate.timeline_estimate}")
            print(f"   Confidence: {result.final_estimate.confidence_score:.2f}")
        
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_pipeline())
