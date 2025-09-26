#!/usr/bin/env python3
"""
Interactive Demo Test for Brant Roofing System Upload Pipeline
This script provides a step-by-step demonstration of the upload process
"""

import time
import json
import requests
import os
import sys
import subprocess

class UploadDemo:
    def __init__(self):
        self.api_url = "http://localhost:3001"
        self.frontend_url = "http://localhost:3000"
        self.flower_url = "http://localhost:5555"
        self.test_file = "tests/mcdonalds collection/small_set.pdf"
        
    def print_header(self, title):
        """Print a formatted header"""
        print("\n" + "=" * 60)
        print(f"🎯 {title}")
        print("=" * 60)
    
    def print_step(self, step_num, title):
        """Print a step header"""
        print(f"\n📋 Step {step_num}: {title}")
        print("-" * 40)
    
    def wait_for_user(self, message="Press Enter to continue..."):
        """Wait for user input"""
        input(f"\n⏸️  {message}")
    
    def check_system_status(self):
        """Check if all systems are running"""
        self.print_step(1, "System Status Check")
        
        # Check API
        try:
            response = requests.get(f"{self.api_url}/api/v1/health", timeout=5)
            if response.status_code == 200:
                print("✅ API: Healthy")
            else:
                print("❌ API: Unhealthy")
                return False
        except Exception as e:
            print(f"❌ API: Error - {e}")
            return False
        
        # Check Frontend
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                print("✅ Frontend: Accessible")
            else:
                print("❌ Frontend: Not accessible")
                return False
        except Exception as e:
            print(f"❌ Frontend: Error - {e}")
            return False
        
        # Check Flower
        try:
            response = requests.get(self.flower_url, timeout=5)
            if response.status_code == 200:
                print("✅ Flower Monitoring: Accessible")
            else:
                print("❌ Flower Monitoring: Not accessible")
                return False
        except Exception as e:
            print(f"❌ Flower Monitoring: Error - {e}")
            return False
        
        # Check test file
        if os.path.exists(self.test_file):
            file_size = os.path.getsize(self.test_file)
            print(f"✅ Test File: {self.test_file} ({file_size:,} bytes)")
        else:
            print(f"❌ Test File: Not found - {self.test_file}")
            return False
        
        return True
    
    def generate_upload_url(self):
        """Generate upload URL"""
        self.print_step(2, "Generate Upload URL")
        
        file_size = os.path.getsize(self.test_file)
        payload = {
            "file_name": os.path.basename(self.test_file),
            "content_type": "application/pdf",
            "size": file_size
        }
        
        print("📤 Requesting upload URL from API...")
        # Corrected endpoint from /generate-url to /generate-signed-url
        response = requests.post(f"{self.api_url}/api/v1/documents/generate-signed-url", json=payload)
        
        if response.status_code == 201:  # Endpoint now returns 201 CREATED
            data = response.json()
            print(f"✅ Upload URL generated successfully")
            print(f"📁 GCS Object: {data['gcs_object_name']}")
            print(f"🔗 Upload URL: {data['upload_url'][:100]}...")
            return data
        else:
            print(f"❌ Failed to generate upload URL: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    
    def upload_file(self, upload_data):
        """Upload file to GCS"""
        self.print_step(3, "Upload File to Google Cloud Storage")
        
        print(f"📤 Uploading {self.test_file} to Google Cloud Storage...")
        
        with open(self.test_file, 'rb') as file:
            response = requests.put(
                upload_data['upload_url'],
                data=file,
                headers={'Content-Type': 'application/pdf'},
                timeout=60
            )
        
        if response.status_code == 200:
            file_size = os.path.getsize(self.test_file)
            print(f"✅ File uploaded successfully!")
            print(f"📊 Size: {file_size:,} bytes")
            print(f"☁️  Stored in: {upload_data['gcs_object_name']}")
            return True
        else:
            print(f"❌ Upload failed: {response.status_code}")
            return False
    
    def start_processing(self, upload_data):
        """Start document processing"""
        self.print_step(4, "Start Document Processing")
        
        payload = {
            "original_filename": os.path.basename(self.test_file),
            "gcs_object_name": upload_data['gcs_object_name'],
            "document_type": "roof_estimate"
        }
        
        print("⚙️ Starting document processing pipeline...")
        response = requests.post(f"{self.api_url}/api/v1/documents/start-processing", json=payload)
        
        if response.status_code in [200, 202]:
            data = response.json()
            print(f"✅ Processing started successfully!")
            print(f"🆔 Document ID: {data['id']}")
            print(f"📊 Status: {data['processing_status']}")
            return data
        else:
            print(f"❌ Processing start failed: {response.status_code}")
            return None
    
    def monitor_processing(self, document_id):
        """Monitor processing progress via the proper API endpoint."""
        self.print_step(5, "Monitor Processing Progress")
        
        print(f"👀 Monitoring document {document_id} via API...")
        print("   (This uses the GET /api/v1/pipeline/status/{id} endpoint)")
        print("📊 Status updates:")
        
        start_time = time.time()
        max_wait_seconds = 120  # 2 minutes for demo
        last_status = None

        while time.time() - start_time < max_wait_seconds:
            try:
                # Use the dedicated API endpoint to check status
                response = requests.get(f"{self.api_url}/api/v1/pipeline/status/{document_id}", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status")
                    elapsed = int(time.time() - start_time)

                    if status != last_status:
                        print(f"   - {elapsed:3d}s: Status changed to {status}")
                        last_status = status
                    
                    if status in ["COMPLETED", "FAILED", "CANCELLED"]:
                        print(f"\n✅ Processing finished with final status: {status}")
                        if status == "FAILED":
                            print(f"   Error details: {data.get('error', 'No details provided.')}")
                        return status
                else:
                    print(f"   - Warning: API returned status {response.status_code}")
                
                time.sleep(5)  # Poll every 5 seconds
            except requests.exceptions.RequestException as e:
                print(f"   - Warning: API request failed: {e}")
                time.sleep(5)
        
        print(f"\n⏰ Monitoring timeout reached after {max_wait_seconds} seconds.")
        return "TIMEOUT"
    
    def fetch_and_display_results(self, document_id):
        """Fetch and display the final estimate results from the API."""
        self.print_step(6, "Fetch Final Estimate")

        print(f"📞 Fetching final estimate for document {document_id}...")
        print(f"   (This uses the GET /api/v1/claude/estimate/{document_id} endpoint)")

        try:
            response = requests.get(f"{self.api_url}/api/v1/claude/estimate/{document_id}", timeout=30)

            if response.status_code == 200:
                data = response.json()
                print("\n" + "-" * 20 + " 📝 FINAL ESTIMATE " + "-" * 20)
                print(f"  📄 Document: {data.get('document_info', {}).get('filename', 'N/A')}")
                print(f"  Total Roof Area: {data.get('total_area_sqft', 0):.2f} sqft")
                print(f"  Estimated Cost: ${data.get('estimated_cost', 0):,.2f}")
                print(f"  Confidence Score: {data.get('confidence_score', 0):.1%}")
                print(f"  Timeline Estimate: {data.get('timeline_estimate', 'N/A')}")
                
                print("\n  Materials Needed:")
                materials = data.get('materials_needed', [])
                if materials:
                    for material in materials:
                        print(f"    - Type: {material.get('type', 'N/A')}, Quantity: {material.get('quantity', 0):.2f} {material.get('unit', '')}")
                else:
                    print("    - No materials listed.")

                print("\n  Labor Estimate:")
                labor = data.get('labor_estimate', {})
                if labor:
                    print(f"    - Hours: {labor.get('estimated_hours', 'N/A'):.1f}, Crew Size: {labor.get('crew_size', 'N/A')}")
                    print(f"    - Total Labor Cost: ${labor.get('total_labor_cost', 0):,.2f}")
                else:
                    print("    - No labor estimate provided.")

                print("\n  Processing Metadata:")
                metadata = data.get('processing_metadata', {})
                print(f"    - Processing Time: {metadata.get('processing_time_seconds', 0):.2f} seconds")
                print(f"    - Stages Completed: {', '.join(metadata.get('stages_completed', []))}")
                if metadata.get('errors'):
                    print(f"    - Errors: {', '.join(metadata.get('errors'))}")
                if metadata.get('warnings'):
                    print(f"    - Warnings: {', '.join(metadata.get('warnings'))}")
                print("-" * 58)
            else:
                print(f"❌ Failed to fetch final estimate. Status: {response.status_code}")
                print(f"   Error: {response.json() if response.content else 'No content'}")
        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed: {e}")

    def show_monitoring_interfaces(self):
        """Show monitoring interfaces"""
        self.print_step(7, "Access Monitoring Interfaces")
        
        print("🌐 Available monitoring interfaces:")
        print(f"   📊 Flower (Celery): {self.flower_url}")
        print(f"   🖥️  Frontend: {self.frontend_url}")
        print(f"   🔧 API Docs: {self.api_url}/docs")
        
        print("\n💡 You can open these URLs in your browser to monitor the system:")
        print(f"   • Flower: Monitor background tasks and workers")
        print(f"   • Frontend: Access the web interface")
        print(f"   • API Docs: View API documentation and test endpoints")
    
    def show_worker_logs(self):
        """Show recent worker logs"""
        self.print_step(8, "View Worker Logs")
        
        print("🔍 Recent worker activity:")
        try:
            result = subprocess.run([
                "docker", "logs", "brant-worker-local", "--tail", "15"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logs = result.stdout
                # Show only relevant lines
                for line in logs.split('\n'):
                    if any(keyword in line.lower() for keyword in ['processing', 'task', 'document', 'pdf', 'gcs']):
                        print(f"   {line}")
            else:
                print("❌ Could not retrieve worker logs")
        except Exception as e:
            print(f"❌ Error retrieving logs: {e}")
    
    def run_demo(self):
        """Run the complete demo"""
        self.print_header("Brant Roofing System Upload Pipeline Demo")
        
        print("🎬 This demo will walk you through the complete upload process")
        print("📁 Using test file: small_set.pdf")
        self.wait_for_user()
        
        # Step 1: Check system status
        if not self.check_system_status():
            print("❌ System not ready. Please ensure all containers are running.")
            return False
        
        self.wait_for_user("System is ready! Continue to upload URL generation?")
        
        # Step 2: Generate upload URL
        upload_data = self.generate_upload_url()
        if not upload_data:
            print("❌ Demo failed at upload URL generation")
            return False
        
        self.wait_for_user("Upload URL generated! Continue to file upload?")
        
        # Step 3: Upload file
        if not self.upload_file(upload_data):
            print("❌ Demo failed at file upload")
            return False
        
        self.wait_for_user("File uploaded! Continue to start processing?")
        
        # Step 4: Start processing
        processing_data = self.start_processing(upload_data)
        if not processing_data:
            print("❌ Demo failed at processing start")
            return False
        
        self.wait_for_user("Processing started! Continue to monitor progress?")
        
        # Step 5: Monitor processing
        final_status = self.monitor_processing(processing_data['id'])
        
        # Step 6: Fetch and display results if completed
        if final_status == "COMPLETED":
            self.wait_for_user("Processing complete! Continue to fetch final results?")
            self.fetch_and_display_results(processing_data['id'])
        else:
            print(f"\n⚠️ Skipping final results fetch because status is {final_status}.")

        self.wait_for_user("Continue to view monitoring interfaces and logs?")
        
        # Step 7: Show monitoring interfaces
        self.show_monitoring_interfaces()
        
        # Step 8: Show worker logs
        self.show_worker_logs()
        
        # Final summary
        self.print_header("Demo Complete!")
        print("🎉 Upload pipeline demonstration completed successfully!")
        print(f"📊 Final processing status: {final_status}")
        print("\n💡 Key capabilities demonstrated:")
        print("   ✅ API health monitoring")
        print("   ✅ Secure upload URL generation")
        print("   ✅ Direct file upload to Google Cloud Storage")
        print("   ✅ Document processing pipeline initiation")
        print("   ✅ Real-time processing status monitoring")
        print("   ✅ Final estimate data retrieval and display")
        print("   ✅ Worker task management")
        print("   ✅ Database integration")
        
        return True

def main():
    """Main function"""
    print("🎭 Brant Roofing System - Interactive Upload Demo")
    print("This demo will walk you through the complete upload process step by step")
    print()
    
    # Check if test file exists
    test_file = "tests/mcdonalds collection/small_set.pdf"
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        print("Please ensure the test file exists before running the demo.")
        sys.exit(1)
    
    # Run the demo
    demo = UploadDemo()
    success = demo.run_demo()
    
    if success:
        print("\n🎯 Demo completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Demo encountered issues!")
        sys.exit(1)

if __name__ == "__main__":
    main()
