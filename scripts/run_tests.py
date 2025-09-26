#!/usr/bin/env python3
"""
Comprehensive Test Runner for Brant Roofing System
Provides options for different types of automated tests
"""

import subprocess
import sys
import os
import argparse

def check_system_requirements():
    """Check if system requirements are met"""
    print("🔍 Checking system requirements...")
    
    # Check if Docker is running
    try:
        result = subprocess.run(["docker", "ps"], capture_output=True, text=True, timeout=10)
        if "brant-api-local" not in result.stdout:
            print("❌ Brant containers not running")
            print("Please start with: docker-compose --profile local up -d")
            return False
        print("✅ Docker containers are running")
    except Exception as e:
        print(f"❌ Docker check failed: {e}")
        return False
    
    # Check if test file exists
    test_file = "tests/mcdonalds collection/small_set.pdf"
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return False
    print(f"✅ Test file found: {test_file}")
    
    return True

def run_simple_test():
    """Run the simple API-based test"""
    print("\n🚀 Running Simple API Test...")
    print("=" * 40)
    try:
        result = subprocess.run([sys.executable, "test_upload_simple.py"], 
                              capture_output=True, text=True, timeout=180)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("⏰ Simple test timed out")
        return False
    except Exception as e:
        print(f"❌ Simple test error: {e}")
        return False

def run_browser_test():
    """Run the browser-based test"""
    print("\n🌐 Running Browser Test...")
    print("=" * 40)
    
    # Check if Selenium is available
    try:
        import selenium
        import requests
        print("✅ Browser test dependencies available")
    except ImportError:
        print("❌ Browser test dependencies not available")
        print("Installing dependencies...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "test_requirements.txt"], 
                          check=True, capture_output=True)
            print("✅ Dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    # Use Windows-compatible browser test
    try:
        result = subprocess.run([sys.executable, "test_upload_browser_windows.py"], 
                              capture_output=True, text=True, timeout=300)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("⏰ Browser test timed out")
        return False
    except Exception as e:
        print(f"❌ Browser test error: {e}")
        return False

def run_quick_test():
    """Run a quick test of just the API endpoints"""
    print("\n⚡ Running Quick API Test...")
    print("=" * 40)
    
    try:
        import requests
        
        # Test API health
        response = requests.get("http://localhost:3001/api/v1/health", timeout=5)
        if response.status_code != 200:
            print("❌ API health check failed")
            return False
        print("✅ API health check passed")
        
        # Test upload URL generation
        # This test is updated to reflect the new /generate-signed-url endpoint
        # which requires file_name, content_type, and size, and returns 201.
        response = requests.post("http://localhost:3001/api/v1/documents/generate-signed-url",
                               json={"file_name": "test.pdf", "content_type": "application/pdf", "size": 1024},
                               timeout=5)
        if response.status_code != 201:
            print(f"❌ Upload URL generation failed with status code {response.status_code}")
            try:
                print(f"   Response: {response.json()}")
            except Exception:
                print(f"   Response: {response.text}")
            return False
        print("✅ Upload URL generation passed")
        
        # Test frontend
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code != 200:
            print("❌ Frontend check failed")
            return False
        print("✅ Frontend check passed")
        
        print("🎉 Quick test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Quick test error: {e}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Brant Roofing System Test Runner")
    parser.add_argument("--type", choices=["quick", "simple", "browser", "all"], 
                       default="simple", help="Type of test to run")
    parser.add_argument("--no-check", action="store_true", 
                       help="Skip system requirements check")
    
    args = parser.parse_args()
    
    print("🤖 Brant Roofing System - Automated Test Runner")
    print("=" * 50)
    
    # Check system requirements unless skipped
    if not args.no_check and not check_system_requirements():
        print("❌ System requirements not met")
        sys.exit(1)
    
    success = True
    
    if args.type == "quick":
        success = run_quick_test()
    elif args.type == "simple":
        success = run_simple_test()
    elif args.type == "browser":
        success = run_browser_test()
    elif args.type == "all":
        print("🔄 Running all tests...")
        success = run_quick_test() and run_simple_test() and run_browser_test()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
