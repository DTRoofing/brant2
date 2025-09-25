#!/usr/bin/env python3
"""
Comprehensive Testing Script for Missing Components
This script systematically tests all aspects of the application.
"""
import os
import sys
from pathlib import Path

def test_imports():
    """Test critical imports that are likely to fail."""
    print("🔍 Testing Critical Imports...")
    
    # Add the current directory to Python path
    sys.path.insert(0, str(Path.cwd()))
    
    critical_imports = [
        "app.core.config",
        "app.main", 
        "app.models.core",
        "app.services.document_service",
        "app.api.deps",
        "app.schemas.document",
        "app.schemas.claude_process",
        "app.core.timeline",
        "app.db.sync_session",
        "app.models.config"
    ]
    
    failed_imports = []
    
    for module_name in critical_imports:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name}")
        except ImportError as e:
            print(f"  ❌ {module_name}: {e}")
            failed_imports.append((module_name, str(e)))
        except Exception as e:
            print(f"  ⚠️  {module_name}: {e}")
            failed_imports.append((module_name, str(e)))
    
    return failed_imports

def test_settings_attributes():
    """Test that all required settings attributes exist."""
    print("\n🔧 Testing Settings Attributes...")
    
    try:
        from app.core.config import settings
        
        required_attributes = [
            'CORS_ORIGINS',
            'REDIS_URL', 
            'DATABASE_URL',
            'CELERY_BROKER_URL',
            'CELERY_RESULT_BACKEND',
            'SECRET_KEY',
            'MAX_FILE_SIZE',
            'ANTHROPIC_API_KEY',
            'GOOGLE_CLOUD_PROJECT_ID',
            'DOCUMENT_AI_PROCESSOR_ID',
            'DOCUMENT_AI_LOCATION',
            'GOOGLE_CLOUD_STORAGE_BUCKET',
            'CLAUDE_MODEL_VERSION',
            'DB_SSL_MODE'
        ]
        
        missing_attributes = []
        
        for attr in required_attributes:
            if hasattr(settings, attr):
                print(f"  ✅ {attr}")
            else:
                print(f"  ❌ {attr} - MISSING")
                missing_attributes.append(attr)
        
        return missing_attributes
        
    except Exception as e:
        print(f"  ❌ Error loading settings: {e}")
        return ["Settings class failed to load"]

def test_application_startup():
    """Test if the application can start up."""
    print("\n🚀 Testing Application Startup...")
    
    try:
        # Test main app import
        from app.main import app
        print("  ✅ FastAPI app imported successfully")
        
        # Test that app has required attributes
        if hasattr(app, 'middleware'):
            print("  ✅ App has middleware")
        else:
            print("  ⚠️  App missing middleware")
            
        return []
        
    except Exception as e:
        print(f"  ❌ Application startup failed: {e}")
        return [f"App startup: {e}"]

def test_database_connections():
    """Test database connection configurations."""
    print("\n🗄️  Testing Database Configurations...")
    
    try:
        from app.core.config import settings
        from app.db.session import get_db
        from app.db.sync_session import SessionLocal
        
        print("  ✅ Database session modules imported")
        
        # Test that database URL is properly formatted
        db_url = settings.DATABASE_URL
        if db_url and "postgresql" in db_url:
            print("  ✅ Database URL format looks correct")
        else:
            print("  ⚠️  Database URL may be incorrect")
            
        return []
        
    except Exception as e:
        print(f"  ❌ Database configuration error: {e}")
        return [f"Database config: {e}"]

def test_services():
    """Test service layer imports."""
    print("\n🔧 Testing Services...")
    
    services_to_test = [
        "app.services.document_service",
        "app.services.google_services", 
        "app.services.claude_service",
        "app.services.pdf_pipeline",
        "app.services.gcs_service"
    ]
    
    failed_services = []
    
    for service in services_to_test:
        try:
            __import__(service)
            print(f"  ✅ {service}")
        except Exception as e:
            print(f"  ❌ {service}: {e}")
            failed_services.append((service, str(e)))
    
    return failed_services

def generate_report(results):
    """Generate a comprehensive test report."""
    print("\n" + "="*80)
    print("COMPREHENSIVE TEST REPORT")
    print("="*80)
    
    total_tests = 0
    total_failures = 0
    
    for test_name, failures in results.items():
        total_tests += 1
        if failures:
            total_failures += 1
            print(f"\n❌ {test_name.upper()}: {len(failures)} failures")
            for failure in failures:
                if isinstance(failure, tuple):
                    print(f"   - {failure[0]}: {failure[1]}")
                else:
                    print(f"   - {failure}")
        else:
            print(f"\n✅ {test_name.upper()}: All tests passed")
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total test categories: {total_tests}")
    print(f"   Failed categories: {total_failures}")
    print(f"   Success rate: {((total_tests - total_failures) / total_tests * 100):.1f}%")
    
    if total_failures == 0:
        print("\n🎉 ALL TESTS PASSED! Application should be ready for Cloud Build.")
    else:
        print(f"\n⚠️  {total_failures} test categories failed. Fix these before Cloud Build.")

def main():
    """Main testing function."""
    print("🚀 Starting Comprehensive Application Testing...")
    print("="*80)
    
    # Run all tests
    results = {
        "imports": test_imports(),
        "settings": test_settings_attributes(), 
        "startup": test_application_startup(),
        "database": test_database_connections(),
        "services": test_services()
    }
    
    # Generate report
    generate_report(results)
    
    # Return exit code
    total_failures = sum(len(failures) for failures in results.values())
    return 1 if total_failures > 0 else 0

if __name__ == "__main__":
    sys.exit(main())
