#!/usr/bin/env python3
"""Final upload test script"""

import time
import subprocess
import json

print("Waiting for API to start...")
time.sleep(30)

# Check API health
print("\nChecking API health...")
health_cmd = ["curl", "-s", "http://localhost:3001/api/v1/health"]
health_result = subprocess.run(health_cmd, capture_output=True, text=True)

if health_result.returncode == 0:
    print("✓ API is healthy")
else:
    print("✗ API health check failed")
    print(health_result.stderr)
    exit(1)

# Create test PDF
print("\nCreating test PDF...")
pdf_content = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
trailer<</Size 4/Root 1 0 R>>
startxref
190
%%EOF"""

with open("test.pdf", "wb") as f:
    f.write(pdf_content)

# Test upload
print("\nTesting PDF upload...")
upload_cmd = [
    "curl", "-X", "POST",
    "http://localhost:3001/api/v1/documents/upload",
    "-F", "file=@test.pdf",
    "-H", "Accept: application/json",
    "-s"
]

upload_result = subprocess.run(upload_cmd, capture_output=True, text=True)

if upload_result.returncode == 0:
    try:
        response = json.loads(upload_result.stdout)
        print("✓ Upload successful!")
        print(f"  Document ID: {response.get('id')}")
        print(f"  Filename: {response.get('filename')}")
        print(f"  Status: {response.get('processing_status')}")
    except json.JSONDecodeError:
        print("✗ Invalid JSON response:")
        print(upload_result.stdout)
else:
    print("✗ Upload failed:")
    print(upload_result.stderr)

# Cleanup
import os
if os.path.exists("test.pdf"):
    os.remove("test.pdf")
    print("\n✓ Cleaned up test file")