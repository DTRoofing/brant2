#!/usr/bin/env python3
"""Simple upload test using curl"""

import subprocess
import json
import os

# First, let's create a minimal PDF using echo and hexdump
print("Creating minimal test PDF...")

# Minimal PDF content
pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>
endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
trailer
<< /Size 4 /Root 1 0 R >>
startxref
190
%%EOF"""

with open("test_minimal.pdf", "wb") as f:
    f.write(pdf_content)

print("Created test_minimal.pdf")

# Test upload using curl
print("\nTesting upload using curl...")

cmd = [
    "curl", "-X", "POST",
    "http://localhost:3001/api/v1/documents/upload",
    "-F", "file=@test_minimal.pdf",
    "-H", "Accept: application/json"
]

try:
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(f"Status: {result.returncode}")
    
    if result.stdout:
        try:
            response = json.loads(result.stdout)
            print(f"\nUpload successful!")
            print(json.dumps(response, indent=2))
            
            doc_id = response.get('id')
            if doc_id:
                print(f"\nDocument ID: {doc_id}")
                
                # Check status
                print("\nChecking document status...")
                status_cmd = ["curl", "-s", f"http://localhost:3001/api/v1/documents/{doc_id}"]
                status_result = subprocess.run(status_cmd, capture_output=True, text=True)
                
                if status_result.stdout:
                    status_response = json.loads(status_result.stdout)
                    print(json.dumps(status_response, indent=2))
                    
        except json.JSONDecodeError:
            print(f"Raw response: {result.stdout}")
    
    if result.stderr:
        print(f"Errors: {result.stderr}")
        
except Exception as e:
    print(f"Error running test: {e}")
    
# Cleanup
if os.path.exists("test_minimal.pdf"):
    os.remove("test_minimal.pdf")
    print("\nCleaned up test file")