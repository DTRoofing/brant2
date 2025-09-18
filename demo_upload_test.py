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
        
        payload = {
            "filename": "small_set.pdf",
            "content_type": "application/pdf"
        }
        
        print("📤 Requesting upload URL from API...")
        response = requests.post(f"{self.api_url}/api/v1/documents/generate-url", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Upload URL generated successfully")
            print(f"📁 GCS Object: {data['gcs_object_name']}")
            print(f"🔗 Upload URL: {data['upload_url'][:100]}...")
            return data
        else:
            print(f"❌ Failed to generate upload URL: {response.status_code}")
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
            "original_filename": "small_set.pdf",
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
        """Monitor processing progress"""
        self.print_step(5, "Monitor Processing Progress")
        
        print(f"👀 Monitoring document {document_id}...")
        print("📊 Status updates:")
        
        start_time = time.time()
        max_wait = 60  # 1 minute for demo
        
        while time.time() - start_time < max_wait:
            try:
                result = subprocess.run([
                    "docker", "exec", "brant-postgres-local", 
                    "psql", "-U", "brant_user", "-d", "brant_roofing", 
                    "-t", "-c", f"SELECT processing_status FROM documents WHERE id = '{document_id}';"
                ], capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    status = result.stdout.strip()
                    elapsed = int(time.time() - start_time)
                    print(f"   📈 {status} (elapsed: {elapsed}s)")
                    
                    if status in ["COMPLETED", "FAILED"]:
                        print(f"✅ Processing finished: {status}")
                        return status
                
                time.sleep(3)
                
            except Exception as e:
                print(f"⚠️ Error checking status: {e}")
                time.sleep(3)
        
        print("⏰ Monitoring timeout (demo limit reached)")
        return "TIMEOUT"
    
    def show_monitoring_interfaces(self):
        """Show monitoring interfaces"""
        self.print_step(6, "Access Monitoring Interfaces")
        
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
        self.print_step(7, "View Worker Logs")
        
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
        
        # Step 6: Show monitoring interfaces
        self.show_monitoring_interfaces()
        
        # Step 7: Show worker logs
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
