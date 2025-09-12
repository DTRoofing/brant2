#!/usr/bin/env python3
"""
Complete test script for the PDF processing flow.
Tests the entire pipeline from upload to results.
"""
import asyncio
import sys
import time
from pathlib import Path
import requests
import json
from typing import Optional

# Configuration
API_BASE_URL = "http://localhost:3001/api/v1"
TEST_PDF_PATH = "tests/mcdonalds collection/ACGARMERE01.pdf"  # Adjust path as needed

class ProcessingFlowTester:
    def __init__(self):
        self.document_id = None
        self.task_id = None
        
    def check_health(self):
        """Check if the API is healthy"""
        print("Checking API health...")
        try:
            response = requests.get(f"{API_BASE_URL}/health")
            if response.status_code == 200:
                print("✓ API is healthy")
                return True
            else:
                print(f"✗ API health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Cannot connect to API: {e}")
            return False
    
    def upload_document(self, file_path: str):
        """Upload a PDF document"""
        print(f"\nUploading document: {file_path}")
        
        if not Path(file_path).exists():
            print(f"✗ File not found: {file_path}")
            return False
            
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (Path(file_path).name, f, 'application/pdf')}
                response = requests.post(
                    f"{API_BASE_URL}/documents/upload",
                    files=files
                )
            
            if response.status_code == 200:
                data = response.json()
                self.document_id = data.get('document_id')
                self.task_id = data.get('task_id')
                print(f"✓ Upload successful!")
                print(f"  Document ID: {self.document_id}")
                print(f"  Task ID: {self.task_id}")
                return True
            else:
                print(f"✗ Upload failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
        except Exception as e:
            print(f"✗ Upload error: {e}")
            return False
    
    def check_processing_status(self):
        """Check the processing status"""
        if not self.task_id:
            print("✗ No task ID available")
            return None
            
        print(f"\nChecking processing status for task: {self.task_id}")
        
        try:
            response = requests.get(f"{API_BASE_URL}/documents/status/{self.task_id}")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'UNKNOWN')
                print(f"  Status: {status}")
                
                if 'result' in data and data['result']:
                    print("  ✓ Processing complete!")
                    return 'SUCCESS'
                elif status == 'FAILURE':
                    print(f"  ✗ Processing failed: {data.get('error', 'Unknown error')}")
                    return 'FAILURE'
                else:
                    print(f"  ⏳ Processing in progress...")
                    return 'PENDING'
            else:
                print(f"✗ Status check failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"✗ Status check error: {e}")
            return None
    
    def test_pipeline_upload(self, file_path: str):
        """Test the new pipeline upload endpoint"""
        print(f"\nTesting pipeline upload: {file_path}")
        
        if not Path(file_path).exists():
            print(f"✗ File not found: {file_path}")
            return False
            
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (Path(file_path).name, f, 'application/pdf')}
                response = requests.post(
                    f"{API_BASE_URL}/pipeline/upload",
                    files=files
                )
            
            if response.status_code == 200:
                data = response.json()
                self.document_id = data.get('document_id')
                print(f"✓ Pipeline upload successful!")
                print(f"  Document ID: {self.document_id}")
                return True
            else:
                print(f"✗ Pipeline upload failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
        except Exception as e:
            print(f"✗ Pipeline upload error: {e}")
            return False
    
    def check_pipeline_status(self):
        """Check pipeline processing status"""
        if not self.document_id:
            print("✗ No document ID available")
            return None
            
        print(f"\nChecking pipeline status for document: {self.document_id}")
        
        try:
            response = requests.get(f"{API_BASE_URL}/pipeline/status/{self.document_id}")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'UNKNOWN')
                stages = data.get('stages', [])
                
                print(f"  Overall Status: {status}")
                print("  Stages:")
                for stage in stages:
                    print(f"    - {stage['name']}: {stage['status']}")
                
                return status
            else:
                print(f"✗ Pipeline status check failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"✗ Pipeline status check error: {e}")
            return None
    
    def get_pipeline_results(self):
        """Get pipeline processing results"""
        if not self.document_id:
            print("✗ No document ID available")
            return None
            
        print(f"\nGetting pipeline results for document: {self.document_id}")
        
        try:
            response = requests.get(f"{API_BASE_URL}/pipeline/results/{self.document_id}")
            
            if response.status_code == 200:
                data = response.json()
                print("✓ Results retrieved successfully!")
                
                # Display summary
                if 'estimate' in data:
                    estimate = data['estimate']
                    print("\n  Estimate Summary:")
                    print(f"    Total Area: {estimate.get('total_area', 'N/A')} sq ft")
                    print(f"    Total Cost: ${estimate.get('total_cost', 'N/A')}")
                    
                if 'sections' in data:
                    print(f"\n  Roof Sections Found: {len(data['sections'])}")
                    
                return data
            else:
                print(f"✗ Failed to get results: {response.status_code}")
                return None
        except Exception as e:
            print(f"✗ Error getting results: {e}")
            return None
    
    def run_complete_test(self):
        """Run a complete test of the processing flow"""
        print("="*60)
        print("PDF PROCESSING FLOW - COMPLETE TEST")
        print("="*60)
        
        # 1. Check API health
        if not self.check_health():
            print("\n❌ API is not running. Please start the backend first.")
            return False
        
        # 2. Test traditional upload endpoint
        print("\n--- Testing Traditional Upload Endpoint ---")
        if self.upload_document(TEST_PDF_PATH):
            # Wait and check status
            for i in range(30):  # Check for up to 5 minutes
                time.sleep(10)
                status = self.check_processing_status()
                if status in ['SUCCESS', 'FAILURE']:
                    break
        
        # 3. Test new pipeline endpoint
        print("\n--- Testing New Pipeline Endpoint ---")
        if self.test_pipeline_upload(TEST_PDF_PATH):
            # Wait and check status
            for i in range(30):  # Check for up to 5 minutes
                time.sleep(10)
                status = self.check_pipeline_status()
                if status == 'completed':
                    # Get results
                    self.get_pipeline_results()
                    break
                elif status == 'failed':
                    print("✗ Pipeline processing failed")
                    break
        
        print("\n" + "="*60)
        print("TEST COMPLETE")
        print("="*60)

def main():
    """Main entry point"""
    tester = ProcessingFlowTester()
    
    # Allow custom PDF path
    if len(sys.argv) > 1:
        global TEST_PDF_PATH
        TEST_PDF_PATH = sys.argv[1]
    
    tester.run_complete_test()

if __name__ == "__main__":
    main()