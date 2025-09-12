#!/usr/bin/env python3
"""Test PDF upload to the API"""

import requests
import os
import json
from datetime import datetime

def test_upload():
    # Configuration
    api_url = "http://localhost:3001/api/v1"
    pdf_file = "test_roofing.pdf"
    
    if not os.path.exists(pdf_file):
        print(f"Error: {pdf_file} not found")
        return False
    
    print(f"Testing PDF upload pipeline")
    print(f"API URL: {api_url}")
    print(f"PDF file: {pdf_file} ({os.path.getsize(pdf_file)} bytes)")
    print("-" * 50)
    
    # Test 1: Check API health
    print("\n1. Testing API health...")
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"   API is healthy: {response.json()}")
        else:
            print(f"   API health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   Cannot connect to API: {e}")
        return False
    
    # Test 2: Upload PDF
    print("\n2. Uploading PDF...")
    try:
        with open(pdf_file, 'rb') as f:
            files = {'file': (pdf_file, f, 'application/pdf')}
            response = requests.post(
                f"{api_url}/uploads/upload",
                files=files,
                timeout=30
            )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"   Upload successful!")
            print(f"   Response: {json.dumps(result, indent=2)}")
            
            # Extract upload ID if available
            upload_id = result.get('id') or result.get('upload_id') or result.get('file_id')
            if upload_id:
                print(f"   Upload ID: {upload_id}")
                return upload_id
            else:
                print("   Warning: No upload ID returned")
                return True
        else:
            print(f"   Upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   Upload error: {e}")
        return False
    except Exception as e:
        print(f"   Unexpected error: {e}")
        return False

def check_processing_status(upload_id):
    """Check the processing status of an upload"""
    api_url = "http://localhost:3001/api/v1"
    
    print(f"\n3. Checking processing status for upload {upload_id}...")
    
    try:
        # Try different possible endpoints
        endpoints = [
            f"/uploads/{upload_id}/status",
            f"/uploads/{upload_id}",
            f"/documents/{upload_id}",
            f"/processing/{upload_id}"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{api_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    result = response.json()
                    print(f"   Status found at {endpoint}")
                    print(f"   Response: {json.dumps(result, indent=2)}")
                    return result
            except:
                continue
        
        print("   Could not retrieve processing status")
        return None
        
    except Exception as e:
        print(f"   Error checking status: {e}")
        return None

if __name__ == "__main__":
    print("=" * 50)
    print("PDF Upload Pipeline Test")
    print("=" * 50)
    
    result = test_upload()
    
    if result:
        print("\n✓ Upload test completed successfully!")
        
        # If we got an upload ID, check processing status
        if isinstance(result, str):
            check_processing_status(result)
    else:
        print("\n✗ Upload test failed!")
        print("\nTroubleshooting:")
        print("1. Check if API container is running: docker ps")
        print("2. Check API logs: docker logs brant-api-1")
        print("3. Verify network connectivity")
        print("4. Check if uploads endpoint is configured")