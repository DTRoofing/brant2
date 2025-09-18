#!/usr/bin/env python3
"""Create Document AI processor for OCR"""

import os
from google.cloud import documentai_v1
from google.oauth2 import service_account

# Set up credentials
credentials_path = "google-credentials.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

# Load credentials
credentials = service_account.Credentials.from_service_account_file(
    credentials_path
)

project_id = "brant-roofing-system-2025"
location = "us"

def create_processor():
    """Create an OCR processor"""
    
    # Create client
    client = documentai_v1.DocumentProcessorServiceClient(credentials=credentials)
    
    # The parent resource name
    parent = f"projects/{project_id}/locations/{location}"
    
    # Create processor
    processor = documentai_v1.Processor(
        display_name="Brant OCR Processor",
        type_="OCR_PROCESSOR"  # For general OCR
    )
    
    try:
        # Create the processor
        response = client.create_processor(
            parent=parent,
            processor=processor
        )
        
        print(f"Created processor: {response.name}")
        print(f"Processor ID: {response.name.split('/')[-1]}")
        return response.name.split('/')[-1]
        
    except Exception as e:
        print(f"Error creating processor: {e}")
        
        # Try to list existing processors
        try:
            processors = client.list_processors(parent=parent)
            for proc in processors:
                if "OCR" in proc.display_name or "ocr" in proc.type_:
                    print(f"Found existing OCR processor: {proc.name}")
                    print(f"Processor ID: {proc.name.split('/')[-1]}")
                    return proc.name.split('/')[-1]
        except Exception as list_error:
            print(f"Could not list processors: {list_error}")
    
    return None

if __name__ == "__main__":
    # Install required package if needed
    try:
        import google.cloud.documentai_v1
    except ImportError:
        print("Installing google-cloud-documentai...")
        import subprocess
        subprocess.check_call(["pip", "install", "google-cloud-documentai"])
        print("Package installed. Please run the script again.")
        exit(1)
    
    processor_id = create_processor()
    if processor_id:
        print(f"\nAdd this to your .env file:")
        print(f"DOCUMENT_AI_PROCESSOR_ID={processor_id}")
    else:
        print("\nFailed to create or find processor")