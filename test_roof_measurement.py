#!/usr/bin/env python3
"""
Test script for roof measurement approaches
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

# Test the McDonald's document
test_pdf_path = "tests/mcdonalds collection/24-0014_McDonalds042-3271_smallerset.pdf"

async def test_roof_measurement():
    """Test both roof measurement approaches"""
    
    print("🏗️  Testing Roof Measurement Approaches")
    print(f"📄 Document: {test_pdf_path}")
    print(f"📁 File size: {Path(test_pdf_path).stat().st_size / 1024 / 1024:.2f} MB")
    print("=" * 70)
    
    try:
        from services.processing_stages.roof_measurement import roof_measurement_service
        
        # Test Approach 1: Computer Vision
        print("\n🔍 Approach 1: Computer Vision + Edge Detection")
        print("-" * 50)
        
        cv_result = await roof_measurement_service.measure_roof_from_blueprint(test_pdf_path)
        
        print(f"📊 Computer Vision Results:")
        print(f"   Total roof area: {cv_result['total_roof_area_sqft']:.0f} sqft")
        print(f"   Scale info: {cv_result['scale_info']}")
        print(f"   Pages processed: {cv_result['pages_processed']}")
        print(f"   Method: {cv_result['method']}")
        print(f"   Confidence: {cv_result['confidence']:.2f}")
        print(f"   Measurements: {len(cv_result['measurements'])}")
        
        for i, measurement in enumerate(cv_result['measurements'][:3]):  # Show first 3
            print(f"     {i+1}. Page {measurement['page']}, Section {measurement['roof_section']}: {measurement['area_sqft']:.0f} sqft")
        
        # Test Approach 2: AI-Powered
        print("\n🤖 Approach 2: AI-Powered Detection")
        print("-" * 50)
        
        ai_result = await roof_measurement_service.measure_roof_with_ai(test_pdf_path)
        
        print(f"📊 AI-Powered Results:")
        print(f"   Total roof area: {ai_result['total_roof_area_sqft']:.0f} sqft")
        print(f"   Scale info: {ai_result['scale_info']}")
        print(f"   Pages processed: {ai_result['pages_processed']}")
        print(f"   Method: {ai_result['method']}")
        print(f"   Confidence: {ai_result['confidence']:.2f}")
        print(f"   Measurements: {len(ai_result['measurements'])}")
        
        for i, measurement in enumerate(ai_result['measurements'][:3]):  # Show first 3
            print(f"     {i+1}. Page {measurement['page']}, Section {measurement['roof_section']}: {measurement['area_sqft']:.0f} sqft")
        
        # Compare approaches
        print("\n📊 Comparison:")
        print("-" * 50)
        print(f"Computer Vision: {cv_result['total_roof_area_sqft']:.0f} sqft (confidence: {cv_result['confidence']:.2f})")
        print(f"AI-Powered:      {ai_result['total_roof_area_sqft']:.0f} sqft (confidence: {ai_result['confidence']:.2f})")
        
        # Calculate cost estimates
        print("\n💰 Cost Estimates:")
        print("-" * 50)
        
        for approach, result in [("Computer Vision", cv_result), ("AI-Powered", ai_result)]:
            area = result['total_roof_area_sqft']
            if area > 0:
                # Commercial roofing costs
                material_cost_per_sqft = 8.00  # Membrane roofing
                labor_cost_per_sqft = 4.00
                total_cost_per_sqft = material_cost_per_sqft + labor_cost_per_sqft
                
                subtotal = area * total_cost_per_sqft
                markup = subtotal * 0.25  # 25% commercial markup
                total_cost = subtotal + markup
                
                print(f"{approach}:")
                print(f"   Area: {area:.0f} sqft")
                print(f"   Cost per sqft: ${total_cost_per_sqft:.2f}")
                print(f"   Subtotal: ${subtotal:,.2f}")
                print(f"   Markup (25%): ${markup:,.2f}")
                print(f"   Total Cost: ${total_cost:,.2f}")
                print()
        
        # Summary
        print("🎯 Summary:")
        print("-" * 50)
        print("✅ Both approaches successfully processed the blueprint")
        print("🔍 Computer Vision: Good for precise measurements when scale is clear")
        print("🤖 AI-Powered: Better for complex layouts and missing scale references")
        print("💡 Recommendation: Use both approaches and compare results for accuracy")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def demonstrate_approaches():
    """Demonstrate the two approaches conceptually"""
    print("\n" + "=" * 70)
    print("📋 ROOF MEASUREMENT APPROACHES")
    print("=" * 70)
    
    print("\n🔍 Approach 1: Computer Vision + Edge Detection")
    print("-" * 50)
    print("Steps:")
    print("1. Convert PDF to images")
    print("2. Use OCR to find scale reference (e.g., '1\" = 20\'-0\"')")
    print("3. Detect roof edges using Canny edge detection")
    print("4. Find contours and filter for roof-like shapes")
    print("5. Measure dimensions in pixels")
    print("6. Convert to feet using scale ratio")
    print("7. Calculate square footage")
    
    print("\n✅ Pros:")
    print("   - Precise measurements when scale is clear")
    print("   - Works with any blueprint format")
    print("   - No AI dependency")
    print("   - Fast processing")
    
    print("\n❌ Cons:")
    print("   - Requires clear scale reference")
    print("   - May miss complex roof shapes")
    print("   - Sensitive to image quality")
    
    print("\n🤖 Approach 2: AI-Powered Detection")
    print("-" * 50)
    print("Steps:")
    print("1. Convert PDF to images")
    print("2. Send images to Claude AI with specialized prompts")
    print("3. AI identifies roof areas and scale")
    print("4. AI measures dimensions and calculates area")
    print("5. Return structured measurement data")
    
    print("\n✅ Pros:")
    print("   - Handles complex roof layouts")
    print("   - Can work without clear scale reference")
    print("   - Understands architectural context")
    print("   - Can identify materials and features")
    
    print("\n❌ Cons:")
    print("   - Requires AI API access")
    print("   - Higher processing cost")
    print("   - May be less precise for simple shapes")
    print("   - Dependent on AI model accuracy")
    
    print("\n💡 Hybrid Approach (Recommended):")
    print("-" * 50)
    print("1. Try Computer Vision first (fast, precise)")
    print("2. If scale not found or low confidence, use AI")
    print("3. Compare results and use the most confident")
    print("4. Combine both approaches for validation")

if __name__ == "__main__":
    print("🚀 Roof Measurement Test")
    demonstrate_approaches()
    
    if Path(test_pdf_path).exists():
        asyncio.run(test_roof_measurement())
    else:
        print(f"\n❌ Test PDF not found: {test_pdf_path}")
        print("Please check the file path and try again.")
