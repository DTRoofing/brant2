#!/usr/bin/env python3
"""Test the upload API endpoint"""

import requests
from pathlib import Path
import json

# Create a simple test PDF if it doesn't exist
test_pdf_path = Path("test_sample.pdf")

if not test_pdf_path.exists():
    print("Creating test PDF...")
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    c = canvas.Canvas(str(test_pdf_path), pagesize=letter)
    c.drawString(100, 750, "Test PDF Document")
    c.drawString(100, 700, "This is a test PDF for upload testing")
    c.drawString(100, 650, "Generated for testing the upload endpoint")
    c.save()
    print(f"Created test PDF: {test_pdf_path}")

# Test the upload endpoint
url = "http://localhost:3001/api/v1/documents/upload"

with open(test_pdf_path, 'rb') as f:
    files = {'file': ('test_sample.pdf', f, 'application/pdf')}
    
    print(f"\nTesting upload to: {url}")
    
    try:
        response = requests.post(url, files=files)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code in [200, 201, 202]:
            result = response.json()
            print(f"\nUpload successful!")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Extract document ID for status check
            doc_id = result.get('id')
            if doc_id:
                print(f"\nDocument ID: {doc_id}")
                print(f"Check status at: http://localhost:3001/api/v1/documents/{doc_id}")
        else:
            print(f"\nUpload failed!")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"\nError: Could not connect to server at {url}")
        print("Make sure the backend server is running on port 3001")
    except Exception as e:
        print(f"\nUnexpected error: {type(e).__name__}: {e}")