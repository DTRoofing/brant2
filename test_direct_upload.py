import requests
import time

# Test file path
test_file = "c:/Development/Final Build/brant/tests/mcdonalds collection/24-0014_McDonalds042-3271_smallerset.pdf"

# Upload file
print("Uploading file...")
with open(test_file, 'rb') as f:
    files = {'file': ('test.pdf', f, 'application/pdf')}
    response = requests.post('http://localhost:3001/api/v1/documents/upload', files=files)
    
print(f"Response status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 202:
    result = response.json()
    doc_id = result.get('id')
    print(f"\nDocument ID: {doc_id}")
    
    # Check status
    time.sleep(2)
    print("\nChecking pipeline status...")
    status_response = requests.get(f'http://localhost:3001/api/v1/pipeline/status/{doc_id}')
    print(f"Status response: {status_response.status_code}")
    print(f"Status: {status_response.text}")