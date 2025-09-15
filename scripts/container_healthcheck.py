#!/usr/bin/env python3
"""
Container Health Check Script
Verifies all dependencies and services are properly configured
"""
import os
import sys
import subprocess
import json

def check_command(command, name):
    """Check if a command is available"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✓ {name}: OK")
            return True
        else:
            print(f"✗ {name}: FAILED")
            return False
    except Exception as e:
        print(f"✗ {name}: ERROR - {e}")
        return False

def check_file(filepath, name):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✓ {name}: Found at {filepath}")
        return True
    else:
        print(f"✗ {name}: Not found at {filepath}")
        return False

def check_env_var(var_name):
    """Check if an environment variable is set"""
    value = os.environ.get(var_name)
    if value:
        # Mask sensitive values
        if "KEY" in var_name or "PASSWORD" in var_name:
            display_value = value[:10] + "..." if len(value) > 10 else "***"
        else:
            display_value = value
        print(f"✓ {var_name}: {display_value}")
        return True
    else:
        print(f"✗ {var_name}: Not set")
        return False

def main():
    print("="*60)
    print("CONTAINER HEALTH CHECK")
    print("="*60)
    
    all_checks_passed = True
    
    # Check system dependencies
    print("\n1. SYSTEM DEPENDENCIES")
    print("-" * 40)
    
    checks = [
        ("pdftoppm --version 2>&1 | head -n 1", "Poppler (PDF to Image)"),
        ("tesseract --version 2>&1 | head -n 1", "Tesseract OCR"),
        ("python --version", "Python"),
        ("pip --version", "Pip"),
    ]
    
    for command, name in checks:
        if not check_command(command, name):
            all_checks_passed = False
    
    # Check Python packages
    print("\n2. PYTHON PACKAGES")
    print("-" * 40)
    
    packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "celery",
        "redis",
        "pdf2image",
        "pytesseract",
        "PyPDF2",
        "anthropic",
        "google-cloud-documentai",
        "google-cloud-vision",
        "google-cloud-storage"
    ]
    
    for package in packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package}: Installed")
        except ImportError:
            print(f"✗ {package}: Not installed")
            all_checks_passed = False
    
    # Check environment variables
    print("\n3. ENVIRONMENT VARIABLES")
    print("-" * 40)
    
    env_vars = [
        "DATABASE_URL",
        "CELERY_BROKER_URL",
        "GOOGLE_APPLICATION_CREDENTIALS",
        "GOOGLE_CLOUD_PROJECT_ID",
        "DOCUMENT_AI_PROCESSOR_ID",
        "ANTHROPIC_API_KEY",
        "UPLOAD_DIR"
    ]
    
    for var in env_vars:
        if not check_env_var(var):
            all_checks_passed = False
    
    # Check file paths
    print("\n4. FILE PATHS")
    print("-" * 40)
    
    paths = [
        ("/app/uploads", "Upload directory"),
        ("/app/logs", "Logs directory"),
        ("/app/google-credentials.json", "Google credentials"),
        ("/app/app", "Application code")
    ]
    
    for path, name in paths:
        if not check_file(path, name):
            all_checks_passed = False
    
    # Check network connectivity
    print("\n5. NETWORK CONNECTIVITY")
    print("-" * 40)
    
    services = [
        ("nc -zv db 5432 2>&1", "PostgreSQL Database"),
        ("nc -zv redis 6379 2>&1", "Redis"),
    ]
    
    for command, name in services:
        check_command(command, name)
    
    # Summary
    print("\n" + "="*60)
    if all_checks_passed:
        print("✓ HEALTH CHECK PASSED - Container is properly configured")
        sys.exit(0)
    else:
        print("✗ HEALTH CHECK FAILED - Some issues need to be resolved")
        sys.exit(1)

if __name__ == "__main__":
    main()