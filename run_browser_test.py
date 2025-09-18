#!/usr/bin/env python3
"""
Browser-based automated test runner for Brant Roofing System
This script will run the full browser automation test
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import selenium
        import requests
        print("✅ All dependencies are available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Installing required packages...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "test_requirements.txt"], check=True)
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False

def run_browser_test():
    """Run the browser-based test"""
    print("🌐 Starting browser-based automated test...")
    try:
        result = subprocess.run([sys.executable, "test_upload_automation.py"], 
                              capture_output=True, text=True, timeout=300)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("⏰ Browser test timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Browser test error: {e}")
        return False

def main():
    """Main function"""
    print("🤖 Brant Roofing System - Browser Test Runner")
    print("=" * 50)
    
    # Check if test file exists
    test_file = "tests/mcdonalds collection/small_set.pdf"
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        print("Please ensure the test file exists before running the test.")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Cannot proceed without dependencies")
        sys.exit(1)
    
    # Run browser test
    success = run_browser_test()
    
    if success:
        print("\n🎉 Browser test completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Browser test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
