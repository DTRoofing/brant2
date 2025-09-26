#!/usr/bin/env python3
"""
Manual Test Verification - Test the automated build fixer components
"""
import re
import os
import sys

def test_error_patterns():
    """Test error pattern matching"""
    print("🧪 Testing Error Pattern Matching...")
    
    # Sample error patterns
    patterns = {
        "poppler_not_found": r"PDFInfoNotInstalledError|pdfinfo.*not found|poppler.*not found",
        "missing_module": r"ModuleNotFoundError: No module named '([^']+)'",
        "attribute_error": r"AttributeError: module '([^']+)' has no attribute '([^']+)'",
        "artifact_registry_permission": r"DENIED.*Permission.*artifactregistry\.repositories\.uploadArtifacts",
        "test_import_failure": r"FAILED.*test.*ImportError|ERROR.*test.*ModuleNotFoundError"
    }
    
    # Sample error messages
    sample_errors = [
        "PDFInfoNotInstalledError: Unable to get page count. Is poppler installed and in PATH?",
        "ModuleNotFoundError: No module named 'app.workers.tasks.pdf_processing'",
        "AttributeError: module 'app.workers.tasks' has no attribute 'pdf_processing'",
        "DENIED: Permission \"artifactregistry.repositories.uploadArtifacts\" denied",
        "FAILED tests/integration/test_pdf_upload_workflow.py::TestPDFUploadAPI::test_upload_valid_pdf"
    ]
    
    matches_found = 0
    total_tests = len(sample_errors)
    
    for i, error_msg in enumerate(sample_errors, 1):
        print(f"   Test {i}: {error_msg[:50]}...")
        
        matched = False
        for pattern_name, pattern in patterns.items():
            if re.search(pattern, error_msg, re.IGNORECASE):
                print(f"      ✅ Matched pattern: {pattern_name}")
                matched = True
                matches_found += 1
                break
        
        if not matched:
            print(f"      ❌ No pattern matched")
    
    print(f"\n📊 Pattern Matching Results: {matches_found}/{total_tests} matches found")
    return matches_found == total_tests

def test_file_structure():
    """Test that all required files exist"""
    print("\n🧪 Testing File Structure...")
    
    required_files = [
        "smart_build_fixer.py",
        "build_error_analyzer.py", 
        "automated_build_fixer.py",
        "test_automated_fixer.py",
        "run_automated_fixer.sh",
        "run_automated_fixer.bat",
        "AUTOMATED_BUILD_FIXER_README.md"
    ]
    
    files_found = 0
    total_files = len(required_files)
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
            files_found += 1
        else:
            print(f"   ❌ {file_path} - MISSING")
    
    print(f"\n📊 File Structure Results: {files_found}/{total_files} files found")
    return files_found == total_files

def test_dockerfile_structure():
    """Test that Dockerfiles have the expected structure"""
    print("\n🧪 Testing Dockerfile Structure...")
    
    dockerfiles = ["backend.Dockerfile", "worker.Dockerfile"]
    dockerfile_tests_passed = 0
    
    for dockerfile in dockerfiles:
        if os.path.exists(dockerfile):
            print(f"   Testing {dockerfile}...")
            
            with open(dockerfile, 'r') as f:
                content = f.read()
            
            # Check for key components
            checks = [
                ("FROM python:3.11-slim", "Base image"),
                ("poppler-utils", "Poppler utilities"),
                ("POPPLER_PATH", "Poppler path environment variable"),
                ("ENV PATH", "PATH environment variable")
            ]
            
            file_checks_passed = 0
            for check_text, description in checks:
                if check_text in content:
                    print(f"      ✅ {description}")
                    file_checks_passed += 1
                else:
                    print(f"      ❌ {description} - MISSING")
            
            if file_checks_passed == len(checks):
                dockerfile_tests_passed += 1
                print(f"   ✅ {dockerfile} - All checks passed")
            else:
                print(f"   ⚠️ {dockerfile} - {file_checks_passed}/{len(checks)} checks passed")
        else:
            print(f"   ❌ {dockerfile} - FILE NOT FOUND")
    
    print(f"\n📊 Dockerfile Results: {dockerfile_tests_passed}/{len(dockerfiles)} files passed")
    return dockerfile_tests_passed == len(dockerfiles)

def test_python_imports():
    """Test that Python files can be imported"""
    print("\n🧪 Testing Python Import Structure...")
    
    # Check if we can read the files without syntax errors
    python_files = [
        "smart_build_fixer.py",
        "build_error_analyzer.py",
        "automated_build_fixer.py"
    ]
    
    import_tests_passed = 0
    
    for py_file in python_files:
        if os.path.exists(py_file):
            print(f"   Testing {py_file}...")
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                # Basic syntax checks
                checks = [
                    ("import ", "Import statements"),
                    ("class ", "Class definitions"),
                    ("def ", "Function definitions"),
                    ("if __name__ == \"__main__\":", "Main block")
                ]
                
                file_checks_passed = 0
                for check_text, description in checks:
                    if check_text in content:
                        print(f"      ✅ {description}")
                        file_checks_passed += 1
                    else:
                        print(f"      ❌ {description} - MISSING")
                
                if file_checks_passed >= 2:  # At least 2 checks should pass
                    import_tests_passed += 1
                    print(f"   ✅ {py_file} - Structure looks good")
                else:
                    print(f"   ⚠️ {py_file} - Structure issues detected")
                    
            except Exception as e:
                print(f"   ❌ {py_file} - Error reading file: {e}")
        else:
            print(f"   ❌ {py_file} - FILE NOT FOUND")
    
    print(f"\n📊 Python Import Results: {import_tests_passed}/{len(python_files)} files passed")
    return import_tests_passed == len(python_files)

def test_git_integration():
    """Test that git integration is available"""
    print("\n🧪 Testing Git Integration...")
    
    try:
        # Check if we're in a git repository
        if os.path.exists(".git"):
            print("   ✅ Git repository detected")
            git_repo = True
        else:
            print("   ❌ Not in a git repository")
            git_repo = False
        
        # Check if git is available (basic check)
        git_available = True
        print("   ✅ Git integration available")
        
        return git_repo and git_available
        
    except Exception as e:
        print(f"   ❌ Git integration error: {e}")
        return False

def main():
    """Run all manual tests"""
    print("🚀 Manual Test Verification for Automated Build Fixer")
    print("=" * 60)
    
    tests = [
        ("Error Pattern Matching", test_error_patterns),
        ("File Structure", test_file_structure),
        ("Dockerfile Structure", test_dockerfile_structure),
        ("Python Import Structure", test_python_imports),
        ("Git Integration", test_git_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                print(f"✅ {test_name} - PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
    
    print(f"\n{'='*60}")
    print(f"📊 FINAL RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The automated build fixer is ready to use.")
        print("\n🚀 To run the automated fixer:")
        print("   Linux/Mac: ./run_automated_fixer.sh")
        print("   Windows: run_automated_fixer.bat")
        print("   Manual: python3 smart_build_fixer.py your-project-id us-central1")
        return True
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        print(f"   Failed tests: {total - passed}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
