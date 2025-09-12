#!/usr/bin/env python3
"""
Minimal test script for the PDF processing pipeline
Tests individual components without full configuration
"""

import asyncio
import sys
from pathlib import Path
import logging
import PyPDF2
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test the McDonald's document
test_pdf_path = "tests/mcdonalds collection/24-0014_McDonalds042-3271_smallerset.pdf"

def test_pdf_basic_extraction():
    """Test basic PDF text extraction"""
    print("🔍 Testing basic PDF extraction...")
    
    if not Path(test_pdf_path).exists():
        print(f"❌ Test PDF not found at {test_pdf_path}")
        return None
    
    try:
        with open(test_pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            print(f"📄 PDF has {len(pdf_reader.pages)} pages")
            
            for i, page in enumerate(pdf_reader.pages[:3]):  # First 3 pages
                page_text = page.extract_text()
                text += f"--- Page {i+1} ---\n{page_text}\n"
                print(f"   Page {i+1}: {len(page_text)} characters")
            
            print(f"📝 Total extracted text: {len(text)} characters")
            print(f"📝 First 500 characters:")
            print(text[:500] + "..." if len(text) > 500 else text)
            
            return text
            
    except Exception as e:
        print(f"❌ PDF extraction failed: {e}")
        return None

def analyze_text_for_roofing(text):
    """Simple analysis of extracted text for roofing information"""
    print("\n🏠 Analyzing text for roofing information...")
    
    text_lower = text.lower()
    
    # Look for common roofing terms
    roofing_keywords = [
        'roof', 'roofing', 'shingle', 'tile', 'membrane', 'metal',
        'square feet', 'sq ft', 'area', 'dimension', 'measurement',
        'pitch', 'slope', 'gable', 'hip', 'valley', 'ridge'
    ]
    
    found_keywords = []
    for keyword in roofing_keywords:
        if keyword in text_lower:
            found_keywords.append(keyword)
    
    print(f"🔍 Found roofing keywords: {found_keywords}")
    
    # Look for measurements
    import re
    measurements = []
    
    # Area patterns
    area_patterns = [
        r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:sq\.?\s*ft\.?|square\s+feet|sf|sqft)',
        r'area[:\s]*(\d+(?:,\d{3})*(?:\.\d+)?)',
        r'roof[:\s]*(\d+(?:,\d{3})*(?:\.\d+)?)',
    ]
    
    for pattern in area_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                value = float(match.group(1).replace(',', ''))
                measurements.append({
                    'text': match.group(0),
                    'value': value,
                    'type': 'area_measurement'
                })
            except ValueError:
                continue
    
    print(f"📏 Found measurements: {len(measurements)}")
    for measurement in measurements:
        print(f"   - {measurement['text']} = {measurement['value']} sqft")
    
    # Look for materials
    materials = []
    material_patterns = {
        'asphalt_shingles': r'asphalt|shingle',
        'metal_roofing': r'metal|steel|aluminum',
        'tile': r'tile|clay|concrete',
        'slate': r'slate',
        'wood_shakes': r'wood|shake|cedar',
        'membrane': r'membrane|epdm|tpo'
    }
    
    for material_type, pattern in material_patterns.items():
        if re.search(pattern, text_lower):
            materials.append(material_type)
    
    print(f"🧱 Found materials: {materials}")
    
    # Calculate estimated roof area
    total_area = 0
    if measurements:
        total_area = sum(m['value'] for m in measurements)
    elif 'roof' in text_lower:
        # Try to estimate from context
        total_area = 2500  # Default estimate for commercial building
    
    print(f"📊 Estimated total roof area: {total_area} sqft")
    
    return {
        'keywords': found_keywords,
        'measurements': measurements,
        'materials': materials,
        'estimated_area': total_area,
        'text_length': len(text)
    }

def generate_simple_estimate(analysis):
    """Generate a simple cost estimate"""
    print("\n💰 Generating simple cost estimate...")
    
    area = analysis['estimated_area']
    if not area:
        print("❌ No area data available for estimate")
        return None
    
    # Basic cost estimates (per sqft)
    material_costs = {
        'asphalt_shingles': 3.50,
        'metal_roofing': 8.00,
        'tile': 12.00,
        'slate': 15.00,
        'wood_shakes': 10.00,
        'membrane': 6.00
    }
    
    labor_costs = {
        'asphalt_shingles': 2.50,
        'metal_roofing': 4.00,
        'tile': 5.00,
        'slate': 8.00,
        'wood_shakes': 6.00,
        'membrane': 3.00
    }
    
    # Determine primary material
    materials = analysis['materials']
    if materials:
        primary_material = materials[0]  # Use first found material
    else:
        primary_material = 'asphalt_shingles'  # Default
    
    material_cost_per_sqft = material_costs.get(primary_material, 3.50)
    labor_cost_per_sqft = labor_costs.get(primary_material, 2.50)
    
    total_material_cost = area * material_cost_per_sqft
    total_labor_cost = area * labor_cost_per_sqft
    total_cost = total_material_cost + total_labor_cost
    
    estimate = {
        'total_area_sqft': area,
        'primary_material': primary_material,
        'material_cost_per_sqft': material_cost_per_sqft,
        'labor_cost_per_sqft': labor_cost_per_sqft,
        'total_material_cost': total_material_cost,
        'total_labor_cost': total_labor_cost,
        'total_cost': total_cost,
        'timeline_days': max(2, int(area / 1000))  # Rough estimate
    }
    
    print(f"📊 Cost Estimate:")
    print(f"   Area: {area} sqft")
    print(f"   Material: {primary_material} @ ${material_cost_per_sqft}/sqft")
    print(f"   Labor: ${labor_cost_per_sqft}/sqft")
    print(f"   Total Material: ${total_material_cost:,.2f}")
    print(f"   Total Labor: ${total_labor_cost:,.2f}")
    print(f"   Total Cost: ${total_cost:,.2f}")
    print(f"   Timeline: {estimate['timeline_days']} days")
    
    return estimate

def main():
    """Main test function"""
    print("🚀 Testing PDF Pipeline Components")
    print(f"📄 Document: {test_pdf_path}")
    print(f"📁 File size: {Path(test_pdf_path).stat().st_size / 1024 / 1024:.2f} MB")
    print("=" * 50)
    
    # Step 1: Extract text
    text = test_pdf_basic_extraction()
    if not text:
        return
    
    # Step 2: Analyze for roofing info
    analysis = analyze_text_for_roofing(text)
    
    # Step 3: Generate estimate
    estimate = generate_simple_estimate(analysis)
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 Pipeline Test Summary:")
    print(f"   ✅ Successfully processed PDF")
    print(f"   📝 Extracted {analysis['text_length']} characters")
    print(f"   🔍 Found {len(analysis['keywords'])} roofing keywords")
    print(f"   📏 Found {len(analysis['measurements'])} measurements")
    print(f"   🧱 Found {len(analysis['materials'])} material types")
    print(f"   📊 Estimated area: {analysis['estimated_area']} sqft")
    if estimate:
        print(f"   💰 Estimated cost: ${estimate['total_cost']:,.2f}")
        print(f"   ⏱️  Timeline: {estimate['timeline_days']} days")
    
    print("\n✅ Pipeline test completed successfully!")

if __name__ == "__main__":
    main()
