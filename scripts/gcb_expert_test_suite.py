#!/usr/bin/env python3
"""
Google Cloud Build Expert Test Suite
Comprehensive testing for perfect Cloud Build deployment
"""

import os
import sys
import subprocess
import json
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import importlib.util
import ast
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GCBExpertTestSuite:
    """Google Cloud Build Expert Test Suite"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.test_results = {}
        self.critical_failures = []
        self.warnings = []
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all GCB expert tests"""
        logger.info("🚀 Starting Google Cloud Build Expert Test Suite")
        logger.info("=" * 80)
        
        tests = [
            ("Python Syntax & Imports", self.test_python_syntax_imports),
            ("Docker Configuration", self.test_docker_configuration),
            ("Dependency Resolution", self.test_dependency_resolution),
            ("Configuration Management", self.test_configuration_management),
            ("Database Connectivity", self.test_database_connectivity),
            ("API Endpoints", self.test_api_endpoints),
            ("Cloud Build Config", self.test_cloud_build_config),
            ("Security & Secrets", self.test_security_secrets),
            ("Resource Limits", self.test_resource_limits),
            ("File Structure", self.test_file_structure),
            ("Environment Variables", self.test_environment_variables),
            ("Health Checks", self.test_health_checks),
            ("Error Handling", self.test_error_handling),
            ("Logging Configuration", self.test_logging_configuration),
            ("Performance Metrics", self.test_performance_metrics)
        ]
        
        for test_name, test_func in tests:
            logger.info(f"\n🔍 Running: {test_name}")
            try:
                result = test_func()
                self.test_results[test_name] = result
                if result.get('status') == 'FAILED':
                    self.critical_failures.append(test_name)
                elif result.get('status') == 'WARNING':
                    self.warnings.append(test_name)
            except Exception as e:
                logger.error(f"❌ Test {test_name} crashed: {e}")
                self.test_results[test_name] = {
                    'status': 'FAILED',
                    'error': str(e),
                    'details': 'Test execution crashed'
                }
                self.critical_failures.append(test_name)
        
        return self.generate_final_report()
    
    def test_python_syntax_imports(self) -> Dict[str, Any]:
        """Test Python syntax and import validation"""
        logger.info("  Testing Python syntax and imports...")
        
        issues = []
        python_files = list(self.project_root.rglob("*.py"))
        
        for py_file in python_files:
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue
                
            try:
                # Test syntax
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse AST to check syntax
                ast.parse(content)
                
                # Test imports
                try:
                    spec = importlib.util.spec_from_file_location("test_module", py_file)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                except ImportError as e:
                    issues.append(f"Import error in {py_file}: {e}")
                except Exception as e:
                    issues.append(f"Module loading error in {py_file}: {e}")
                    
            except SyntaxError as e:
                issues.append(f"Syntax error in {py_file}: {e}")
            except Exception as e:
                issues.append(f"Error processing {py_file}: {e}")
        
        status = "PASSED" if not issues else "FAILED"
        return {
            'status': status,
            'files_checked': len(python_files),
            'issues': issues,
            'details': f"Checked {len(python_files)} Python files"
        }
    
    def test_docker_configuration(self) -> Dict[str, Any]:
        """Test Docker configuration files"""
        logger.info("  Testing Docker configuration...")
        
        issues = []
        docker_files = [
            "Dockerfile",
            "backend.Dockerfile", 
            "worker.Dockerfile",
            "docker-compose.yml",
            "docker-compose.test.yml"
        ]
        
        for docker_file in docker_files:
            file_path = self.project_root / docker_file
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # Check for common issues
                    if "COPY" in content and "google-credentials.json" in content:
                        if not (self.project_root / "google-credentials.json").exists():
                            issues.append(f"{docker_file}: References google-credentials.json but file doesn't exist")
                    
                    if "EXPOSE" not in content and docker_file.startswith("Dockerfile"):
                        issues.append(f"{docker_file}: Missing EXPOSE directive")
                    
                    if "HEALTHCHECK" not in content and docker_file.startswith("Dockerfile"):
                        issues.append(f"{docker_file}: Missing HEALTHCHECK directive")
                        
                except Exception as e:
                    issues.append(f"Error reading {docker_file}: {e}")
            else:
                if docker_file in ["Dockerfile", "docker-compose.yml"]:
                    issues.append(f"Missing required file: {docker_file}")
        
        status = "PASSED" if not issues else "WARNING"
        return {
            'status': status,
            'files_checked': len([f for f in docker_files if (self.project_root / f).exists()]),
            'issues': issues,
            'details': "Docker configuration validation"
        }
    
    def test_dependency_resolution(self) -> Dict[str, Any]:
        """Test dependency resolution and requirements"""
        logger.info("  Testing dependency resolution...")
        
        issues = []
        requirements_files = ["requirements.txt", "pyproject.toml", "poetry.lock"]
        
        for req_file in requirements_files:
            file_path = self.project_root / req_file
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # Check for version conflicts
                    if req_file == "requirements.txt":
                        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
                        for line in lines:
                            if '==' in line:
                                package, version = line.split('==')
                                # Check for duplicate packages
                                duplicates = [l for l in lines if l.startswith(package) and l != line]
                                if duplicates:
                                    issues.append(f"Duplicate package {package} in {req_file}")
                    
                    # Check for missing critical dependencies
                    critical_deps = ["fastapi", "uvicorn", "sqlalchemy", "celery", "redis"]
                    for dep in critical_deps:
                        if dep not in content.lower():
                            issues.append(f"Missing critical dependency {dep} in {req_file}")
                            
                except Exception as e:
                    issues.append(f"Error reading {req_file}: {e}")
        
        status = "PASSED" if not issues else "WARNING"
        return {
            'status': status,
            'files_checked': len([f for f in requirements_files if (self.project_root / f).exists()]),
            'issues': issues,
            'details': "Dependency resolution validation"
        }
    
    def test_configuration_management(self) -> Dict[str, Any]:
        """Test configuration management"""
        logger.info("  Testing configuration management...")
        
        issues = []
        
        # Check for .env file
        env_file = self.project_root / ".env"
        if not env_file.exists():
            issues.append("Missing .env file for local development")
        
        # Check settings.py
        settings_file = self.project_root / "app" / "core" / "config.py"
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    content = f.read()
                
                # Check for hardcoded secrets
                hardcoded_secrets = ["password", "secret", "key", "token"]
                for secret in hardcoded_secrets:
                    if f'"{secret}"' in content or f"'{secret}'" in content:
                        issues.append(f"Potential hardcoded secret in config.py: {secret}")
                
                # Check for required settings
                required_settings = ["DATABASE_URL", "SECRET_KEY", "CORS_ORIGINS"]
                for setting in required_settings:
                    if setting not in content:
                        issues.append(f"Missing required setting: {setting}")
                        
            except Exception as e:
                issues.append(f"Error reading config.py: {e}")
        
        status = "PASSED" if not issues else "WARNING"
        return {
            'status': status,
            'issues': issues,
            'details': "Configuration management validation"
        }
    
    def test_database_connectivity(self) -> Dict[str, Any]:
        """Test database connectivity configuration"""
        logger.info("  Testing database connectivity...")
        
        issues = []
        
        # Check database session files
        db_files = [
            "app/db/session.py",
            "app/db/sync_session.py"
        ]
        
        for db_file in db_files:
            file_path = self.project_root / db_file
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # Check for proper error handling
                    if "try:" not in content and "except" not in content:
                        issues.append(f"{db_file}: Missing error handling")
                    
                    # Check for connection pooling
                    if "pool" not in content.lower():
                        issues.append(f"{db_file}: Missing connection pooling configuration")
                        
                except Exception as e:
                    issues.append(f"Error reading {db_file}: {e}")
        
        # Check for Alembic configuration
        alembic_file = self.project_root / "alembic.ini"
        if not alembic_file.exists():
            issues.append("Missing alembic.ini for database migrations")
        
        status = "PASSED" if not issues else "WARNING"
        return {
            'status': status,
            'issues': issues,
            'details': "Database connectivity validation"
        }
    
    def test_api_endpoints(self) -> Dict[str, Any]:
        """Test API endpoints configuration"""
        logger.info("  Testing API endpoints...")
        
        issues = []
        
        # Check main.py
        main_file = self.project_root / "app" / "main.py"
        if main_file.exists():
            try:
                with open(main_file, 'r') as f:
                    content = f.read()
                
                # Check for CORS configuration
                if "CORSMiddleware" not in content:
                    issues.append("Missing CORS middleware configuration")
                
                # Check for health check endpoint
                if "health" not in content.lower():
                    issues.append("Missing health check endpoint")
                
                # Check for error handlers
                if "exception_handler" not in content:
                    issues.append("Missing exception handlers")
                    
            except Exception as e:
                issues.append(f"Error reading main.py: {e}")
        
        # Check API endpoints
        api_dir = self.project_root / "app" / "api" / "v1" / "endpoints"
        if api_dir.exists():
            endpoint_files = list(api_dir.glob("*.py"))
            if not endpoint_files:
                issues.append("No API endpoint files found")
        
        status = "PASSED" if not issues else "WARNING"
        return {
            'status': status,
            'issues': issues,
            'details': "API endpoints validation"
        }
    
    def test_cloud_build_config(self) -> Dict[str, Any]:
        """Test Cloud Build configuration"""
        logger.info("  Testing Cloud Build configuration...")
        
        issues = []
        
        # Check cloudbuild.yaml
        cloudbuild_file = self.project_root / "cloudbuild.yaml"
        if cloudbuild_file.exists():
            try:
                with open(cloudbuild_file, 'r') as f:
                    content = yaml.safe_load(f)
                
                # Check for required steps
                if 'steps' not in content:
                    issues.append("Missing steps in cloudbuild.yaml")
                else:
                    steps = content['steps']
                    if not any('docker' in str(step).lower() for step in steps):
                        issues.append("Missing Docker build step")
                    
                    if not any('push' in str(step).lower() for step in steps):
                        issues.append("Missing image push step")
                
                # Check for timeout configuration
                if 'timeout' not in content:
                    issues.append("Missing timeout configuration")
                
                # Check for substitution variables
                if 'substitutions' not in content:
                    issues.append("Missing substitutions configuration")
                    
            except Exception as e:
                issues.append(f"Error reading cloudbuild.yaml: {e}")
        else:
            issues.append("Missing cloudbuild.yaml file")
        
        status = "PASSED" if not issues else "FAILED"
        return {
            'status': status,
            'issues': issues,
            'details': "Cloud Build configuration validation"
        }
    
    def test_security_secrets(self) -> Dict[str, Any]:
        """Test security and secrets management"""
        logger.info("  Testing security and secrets management...")
        
        issues = []
        
        # Check for hardcoded secrets
        python_files = list(self.project_root.rglob("*.py"))
        for py_file in python_files:
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for hardcoded secrets
                secret_patterns = [
                    r'["\']sk-[a-zA-Z0-9]{20,}["\']',  # API keys
                    r'["\']password["\']\s*[:=]\s*["\'][^"\']+["\']',  # Passwords
                    r'["\']secret["\']\s*[:=]\s*["\'][^"\']+["\']',  # Secrets
                ]
                
                for pattern in secret_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        issues.append(f"Potential hardcoded secret in {py_file}")
                        
            except Exception as e:
                issues.append(f"Error checking {py_file} for secrets: {e}")
        
        # Check for .gitignore
        gitignore_file = self.project_root / ".gitignore"
        if gitignore_file.exists():
            try:
                with open(gitignore_file, 'r') as f:
                    content = f.read()
                
                required_ignores = [".env", "*.json", "__pycache__", "venv"]
                for ignore in required_ignores:
                    if ignore not in content:
                        issues.append(f"Missing {ignore} in .gitignore")
                        
            except Exception as e:
                issues.append(f"Error reading .gitignore: {e}")
        else:
            issues.append("Missing .gitignore file")
        
        status = "PASSED" if not issues else "WARNING"
        return {
            'status': status,
            'issues': issues,
            'details': "Security and secrets validation"
        }
    
    def test_resource_limits(self) -> Dict[str, Any]:
        """Test resource limits and performance"""
        logger.info("  Testing resource limits...")
        
        issues = []
        
        # Check docker-compose.yml for resource limits
        compose_file = self.project_root / "docker-compose.yml"
        if compose_file.exists():
            try:
                with open(compose_file, 'r') as f:
                    content = yaml.safe_load(f)
                
                if 'services' in content:
                    for service_name, service_config in content['services'].items():
                        if 'deploy' in service_config and 'resources' in service_config['deploy']:
                            resources = service_config['deploy']['resources']
                            if 'limits' not in resources:
                                issues.append(f"Service {service_name}: Missing resource limits")
                            else:
                                limits = resources['limits']
                                if 'memory' not in limits:
                                    issues.append(f"Service {service_name}: Missing memory limit")
                                if 'cpus' not in limits:
                                    issues.append(f"Service {service_name}: Missing CPU limit")
                        else:
                            issues.append(f"Service {service_name}: Missing resource configuration")
                            
            except Exception as e:
                issues.append(f"Error reading docker-compose.yml: {e}")
        
        status = "PASSED" if not issues else "WARNING"
        return {
            'status': status,
            'issues': issues,
            'details': "Resource limits validation"
        }
    
    def test_file_structure(self) -> Dict[str, Any]:
        """Test file structure and organization"""
        logger.info("  Testing file structure...")
        
        issues = []
        
        # Check for required directories
        required_dirs = ["app", "app/api", "app/core", "app/models", "app/services"]
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                issues.append(f"Missing required directory: {dir_path}")
        
        # Check for required files
        required_files = [
            "app/main.py",
            "app/core/config.py",
            "requirements.txt",
            "Dockerfile"
        ]
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                issues.append(f"Missing required file: {file_path}")
        
        # Check for proper __init__.py files
        python_dirs = [d for d in self.project_root.rglob("*") if d.is_dir() and "venv" not in str(d)]
        for py_dir in python_dirs:
            if (py_dir / "__init__.py").exists():
                continue
            # Check if it's a Python package directory
            py_files = list(py_dir.glob("*.py"))
            if py_files and "venv" not in str(py_dir):
                issues.append(f"Missing __init__.py in {py_dir.relative_to(self.project_root)}")
        
        status = "PASSED" if not issues else "WARNING"
        return {
            'status': status,
            'issues': issues,
            'details': "File structure validation"
        }
    
    def test_environment_variables(self) -> Dict[str, Any]:
        """Test environment variable configuration"""
        logger.info("  Testing environment variables...")
        
        issues = []
        
        # Check .env file
        env_file = self.project_root / ".env"
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    content = f.read()
                
                # Check for required environment variables
                required_vars = [
                    "DATABASE_URL",
                    "SECRET_KEY",
                    "CORS_ORIGINS",
                    "REDIS_URL"
                ]
                
                for var in required_vars:
                    if f"{var}=" not in content:
                        issues.append(f"Missing required environment variable: {var}")
                
                # Check for placeholder values
                placeholder_patterns = [
                    r'your-.*-key',
                    r'placeholder',
                    r'change-in-production'
                ]
                
                for pattern in placeholder_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        issues.append(f"Found placeholder value in .env: {pattern}")
                        
            except Exception as e:
                issues.append(f"Error reading .env file: {e}")
        else:
            issues.append("Missing .env file")
        
        status = "PASSED" if not issues else "WARNING"
        return {
            'status': status,
            'issues': issues,
            'details': "Environment variables validation"
        }
    
    def test_health_checks(self) -> Dict[str, Any]:
        """Test health check configuration"""
        logger.info("  Testing health checks...")
        
        issues = []
        
        # Check for health check endpoints
        api_dir = self.project_root / "app" / "api" / "v1" / "endpoints"
        if api_dir.exists():
            health_files = list(api_dir.glob("*health*.py"))
            if not health_files:
                issues.append("No health check endpoint files found")
        
        # Check docker-compose.yml for health checks
        compose_file = self.project_root / "docker-compose.yml"
        if compose_file.exists():
            try:
                with open(compose_file, 'r') as f:
                    content = yaml.safe_load(f)
                
                if 'services' in content:
                    for service_name, service_config in content['services'].items():
                        if 'healthcheck' not in service_config:
                            issues.append(f"Service {service_name}: Missing health check configuration")
                        else:
                            healthcheck = service_config['healthcheck']
                            if 'test' not in healthcheck:
                                issues.append(f"Service {service_name}: Health check missing test command")
                            
            except Exception as e:
                issues.append(f"Error reading docker-compose.yml: {e}")
        
        status = "PASSED" if not issues else "WARNING"
        return {
            'status': status,
            'issues': issues,
            'details': "Health checks validation"
        }
    
    def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling configuration"""
        logger.info("  Testing error handling...")
        
        issues = []
        
        # Check main.py for error handlers
        main_file = self.project_root / "app" / "main.py"
        if main_file.exists():
            try:
                with open(main_file, 'r') as f:
                    content = f.read()
                
                if "exception_handler" not in content:
                    issues.append("Missing exception handlers in main.py")
                
                if "HTTPException" not in content:
                    issues.append("Missing HTTP exception handling")
                    
            except Exception as e:
                issues.append(f"Error reading main.py: {e}")
        
        # Check API endpoints for error handling
        api_dir = self.project_root / "app" / "api" / "v1" / "endpoints"
        if api_dir.exists():
            endpoint_files = list(api_dir.glob("*.py"))
            for endpoint_file in endpoint_files:
                try:
                    with open(endpoint_file, 'r') as f:
                        content = f.read()
                    
                    if "try:" not in content and "except" not in content:
                        issues.append(f"Missing error handling in {endpoint_file.name}")
                        
                except Exception as e:
                    issues.append(f"Error reading {endpoint_file}: {e}")
        
        status = "PASSED" if not issues else "WARNING"
        return {
            'status': status,
            'issues': issues,
            'details': "Error handling validation"
        }
    
    def test_logging_configuration(self) -> Dict[str, Any]:
        """Test logging configuration"""
        logger.info("  Testing logging configuration...")
        
        issues = []
        
        # Check for logging configuration
        python_files = list(self.project_root.rglob("*.py"))
        logging_files = [f for f in python_files if "log" in f.name.lower() or "logging" in f.name.lower()]
        
        if not logging_files:
            issues.append("No dedicated logging configuration files found")
        
        # Check main.py for logging setup
        main_file = self.project_root / "app" / "main.py"
        if main_file.exists():
            try:
                with open(main_file, 'r') as f:
                    content = f.read()
                
                if "logging" not in content.lower():
                    issues.append("Missing logging configuration in main.py")
                    
            except Exception as e:
                issues.append(f"Error reading main.py: {e}")
        
        # Check for proper logging usage
        api_files = list((self.project_root / "app" / "api").rglob("*.py"))
        for api_file in api_files:
            try:
                with open(api_file, 'r') as f:
                    content = f.read()
                
                if "logger" not in content and "logging" not in content:
                    issues.append(f"Missing logging in {api_file.relative_to(self.project_root)}")
                    
            except Exception as e:
                issues.append(f"Error reading {api_file}: {e}")
        
        status = "PASSED" if not issues else "WARNING"
        return {
            'status': status,
            'issues': issues,
            'details': "Logging configuration validation"
        }
    
    def test_performance_metrics(self) -> Dict[str, Any]:
        """Test performance metrics and monitoring"""
        logger.info("  Testing performance metrics...")
        
        issues = []
        
        # Check for performance monitoring
        main_file = self.project_root / "app" / "main.py"
        if main_file.exists():
            try:
                with open(main_file, 'r') as f:
                    content = f.read()
                
                if "time" not in content.lower() and "duration" not in content.lower():
                    issues.append("Missing performance timing in main.py")
                    
            except Exception as e:
                issues.append(f"Error reading main.py: {e}")
        
        # Check for database connection pooling
        db_files = ["app/db/session.py", "app/db/sync_session.py"]
        for db_file in db_files:
            file_path = self.project_root / db_file
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    if "pool" not in content.lower():
                        issues.append(f"Missing connection pooling in {db_file}")
                        
                except Exception as e:
                    issues.append(f"Error reading {db_file}: {e}")
        
        status = "PASSED" if not issues else "WARNING"
        return {
            'status': status,
            'issues': issues,
            'details': "Performance metrics validation"
        }
    
    def generate_final_report(self) -> Dict[str, Any]:
        """Generate final test report"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 GOOGLE CLOUD BUILD EXPERT TEST REPORT")
        logger.info("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results.values() if r.get('status') == 'PASSED'])
        warning_tests = len([r for r in self.test_results.values() if r.get('status') == 'WARNING'])
        failed_tests = len([r for r in self.test_results.values() if r.get('status') == 'FAILED'])
        
        logger.info(f"📈 SUMMARY:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   ✅ Passed: {passed_tests}")
        logger.info(f"   ⚠️  Warnings: {warning_tests}")
        logger.info(f"   ❌ Failed: {failed_tests}")
        logger.info(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.critical_failures:
            logger.info(f"\n🚨 CRITICAL FAILURES:")
            for failure in self.critical_failures:
                logger.info(f"   - {failure}")
        
        if self.warnings:
            logger.info(f"\n⚠️  WARNINGS:")
            for warning in self.warnings:
                logger.info(f"   - {warning}")
        
        # Determine overall status
        if failed_tests > 0:
            overall_status = "FAILED"
            logger.info(f"\n❌ OVERALL STATUS: {overall_status}")
            logger.info("   Critical issues must be fixed before Cloud Build deployment")
        elif warning_tests > 0:
            overall_status = "WARNING"
            logger.info(f"\n⚠️  OVERALL STATUS: {overall_status}")
            logger.info("   Warnings should be addressed for optimal deployment")
        else:
            overall_status = "PASSED"
            logger.info(f"\n✅ OVERALL STATUS: {overall_status}")
            logger.info("   Codebase is ready for Cloud Build deployment!")
        
        return {
            'overall_status': overall_status,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'warning_tests': warning_tests,
            'failed_tests': failed_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'critical_failures': self.critical_failures,
            'warnings': self.warnings,
            'test_results': self.test_results
        }

def main():
    """Main function"""
    test_suite = GCBExpertTestSuite()
    report = test_suite.run_all_tests()
    
    # Save report to file
    with open("gcb_expert_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"\n📄 Detailed report saved to: gcb_expert_test_report.json")
    
    # Return exit code
    return 0 if report['overall_status'] == 'PASSED' else 1

if __name__ == "__main__":
    sys.exit(main())
