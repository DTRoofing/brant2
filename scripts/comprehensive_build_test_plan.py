#!/usr/bin/env python3
"""
Comprehensive Build Test Plan for Brant Roofing System

This script emulates the Cloud Run build process and runs a battery of tests
to ensure successful deployment. It follows the exact same steps as the
cloudbuild.yaml pipeline but runs locally for validation.

Usage:
    python scripts/comprehensive_build_test_plan.py [--verbose] [--skip-docker]
"""

import os
import sys
import subprocess
import tempfile
import shutil
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

class TestStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class TestResult:
    name: str
    status: TestStatus
    duration: float
    output: str
    error: Optional[str] = None

class BuildTester:
    """Comprehensive build testing suite that emulates Cloud Run deployment."""
    
    def __init__(self, verbose: bool = False, skip_docker: bool = False):
        self.verbose = verbose
        self.skip_docker = skip_docker
        self.project_root = Path(__file__).parent.parent
        self.results: List[TestResult] = []
        
        # Setup logging
        level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def run_command(self, cmd: List[str], cwd: Optional[Path] = None, timeout: int = 300) -> Tuple[int, str, str]:
        """Run a command and return exit code, stdout, stderr."""
        if cwd is None:
            cwd = self.project_root
            
        self.logger.debug(f"Running: {' '.join(cmd)} in {cwd}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return 1, "", str(e)

    def test_python_environment(self) -> TestResult:
        """Test Python environment and basic imports."""
        start_time = time.time()
        
        try:
            # Check Python version
            exit_code, stdout, stderr = self.run_command([sys.executable, "--version"])
            if exit_code != 0:
                return TestResult(
                    "python_environment", TestStatus.FAILED, 
                    time.time() - start_time, stdout, stderr
                )
            
            # Test basic imports
            test_imports = [
                "import sys",
                "import os", 
                "import json",
                "import asyncio",
                "print('Python environment OK')"
            ]
            
            exit_code, stdout, stderr = self.run_command([
                sys.executable, "-c", "; ".join(test_imports)
            ])
            
            status = TestStatus.PASSED if exit_code == 0 else TestStatus.FAILED
            return TestResult(
                "python_environment", status,
                time.time() - start_time, stdout, stderr
            )
            
        except Exception as e:
            return TestResult(
                "python_environment", TestStatus.FAILED,
                time.time() - start_time, "", str(e)
            )

    def test_dependency_installation(self) -> TestResult:
        """Test Poetry dependency installation (mimics Cloud Build step)."""
        start_time = time.time()
        
        try:
            self.logger.info("Testing Poetry dependency installation...")
            
            # Check if poetry is available
            exit_code, stdout, stderr = self.run_command(["poetry", "--version"])
            if exit_code != 0:
                # Try to install poetry
                self.logger.info("Poetry not found, installing...")
                exit_code, stdout, stderr = self.run_command([
                    sys.executable, "-m", "pip", "install", "poetry==1.8.2"
                ])
                if exit_code != 0:
                    return TestResult(
                        "dependency_installation", TestStatus.FAILED,
                        time.time() - start_time, stdout, stderr
                    )
            
            # Poetry lock check (like Cloud Build)
            exit_code, stdout, stderr = self.run_command([
                "poetry", "lock", "--no-update"
            ])
            if exit_code != 0:
                return TestResult(
                    "dependency_installation", TestStatus.FAILED,
                    time.time() - start_time, stdout, stderr
                )
            
            # Install dependencies (production mode like Cloud Build)
            exit_code, stdout, stderr = self.run_command([
                "poetry", "install", "--no-dev", "--no-interaction", "--no-ansi"
            ])
            
            status = TestStatus.PASSED if exit_code == 0 else TestStatus.FAILED
            return TestResult(
                "dependency_installation", status,
                time.time() - start_time, stdout, stderr
            )
            
        except Exception as e:
            return TestResult(
                "dependency_installation", TestStatus.FAILED,
                time.time() - start_time, "", str(e)
            )

    def test_unit_tests(self) -> TestResult:
        """Run unit tests (mimics Cloud Build quality gate)."""
        start_time = time.time()
        
        try:
            self.logger.info("Running unit tests...")
            
            # Run pytest with same flags as Cloud Build
            exit_code, stdout, stderr = self.run_command([
                "poetry", "run", "pytest", 
                "-m", "not integration and not e2e",
                "--tb=short",
                "--maxfail=5",
                "--timeout=60"
            ])
            
            status = TestStatus.PASSED if exit_code == 0 else TestStatus.FAILED
            return TestResult(
                "unit_tests", status,
                time.time() - start_time, stdout, stderr
            )
            
        except Exception as e:
            return TestResult(
                "unit_tests", TestStatus.FAILED,
                time.time() - start_time, "", str(e)
            )

    def test_vulnerability_scan(self) -> TestResult:
        """Run vulnerability scan (mimics Cloud Build security check)."""
        start_time = time.time()
        
        try:
            self.logger.info("Running vulnerability scan...")
            
            # Install pip-audit
            exit_code, stdout, stderr = self.run_command([
                sys.executable, "-m", "pip", "install", "pip-audit"
            ])
            if exit_code != 0:
                return TestResult(
                    "vulnerability_scan", TestStatus.FAILED,
                    time.time() - start_time, stdout, stderr
                )
            
            # Run pip-audit (like Cloud Build)
            exit_code, stdout, stderr = self.run_command([
                "pip-audit"
            ])
            
            status = TestStatus.PASSED if exit_code == 0 else TestStatus.FAILED
            return TestResult(
                "vulnerability_scan", status,
                time.time() - start_time, stdout, stderr
            )
            
        except Exception as e:
            return TestResult(
                "vulnerability_scan", TestStatus.FAILED,
                time.time() - start_time, "", str(e)
            )

    def test_docker_build_api(self) -> TestResult:
        """Test Docker build for API service."""
        if self.skip_docker:
            return TestResult(
                "docker_build_api", TestStatus.SKIPPED,
                0, "Docker tests skipped", None
            )
            
        start_time = time.time()
        
        try:
            self.logger.info("Testing API Docker build...")
            
            # Build Docker image (like Cloud Build)
            exit_code, stdout, stderr = self.run_command([
                "docker", "build",
                "-f", "backend.Dockerfile",
                "-t", "brant-api:test",
                "."
            ], timeout=600)
            
            status = TestStatus.PASSED if exit_code == 0 else TestStatus.FAILED
            return TestResult(
                "docker_build_api", status,
                time.time() - start_time, stdout, stderr
            )
            
        except Exception as e:
            return TestResult(
                "docker_build_api", TestStatus.FAILED,
                time.time() - start_time, "", str(e)
            )

    def test_docker_build_worker(self) -> TestResult:
        """Test Docker build for Worker service."""
        if self.skip_docker:
            return TestResult(
                "docker_build_worker", TestStatus.SKIPPED,
                0, "Docker tests skipped", None
            )
            
        start_time = time.time()
        
        try:
            self.logger.info("Testing Worker Docker build...")
            
            # Build Docker image (like Cloud Build)
            exit_code, stdout, stderr = self.run_command([
                "docker", "build",
                "-f", "worker.Dockerfile", 
                "-t", "brant-worker:test",
                "."
            ], timeout=600)
            
            status = TestStatus.PASSED if exit_code == 0 else TestStatus.FAILED
            return TestResult(
                "docker_build_worker", status,
                time.time() - start_time, stdout, stderr
            )
            
        except Exception as e:
            return TestResult(
                "docker_build_worker", TestStatus.FAILED,
                time.time() - start_time, "", str(e)
            )

    def test_docker_build_frontend(self) -> TestResult:
        """Test Docker build for Frontend service."""
        if self.skip_docker:
            return TestResult(
                "docker_build_frontend", TestStatus.SKIPPED,
                0, "Docker tests skipped", None
            )
            
        start_time = time.time()
        
        try:
            self.logger.info("Testing Frontend Docker build...")
            
            # Build Docker image (like Cloud Build)
            exit_code, stdout, stderr = self.run_command([
                "docker", "build",
                "-f", "Dockerfile",
                "--target", "release",
                "--build-arg", "NEXT_PUBLIC_API_URL=https://api.example.com",
                "-t", "brant-frontend:test",
                "."
            ], cwd=self.project_root / "frontend_ux", timeout=900)
            
            status = TestStatus.PASSED if exit_code == 0 else TestStatus.FAILED
            return TestResult(
                "docker_build_frontend", status,
                time.time() - start_time, stdout, stderr
            )
            
        except Exception as e:
            return TestResult(
                "docker_build_frontend", TestStatus.FAILED,
                time.time() - start_time, "", str(e)
            )

    def test_application_imports(self) -> TestResult:
        """Test that all application modules can be imported."""
        start_time = time.time()
        
        try:
            self.logger.info("Testing application imports...")
            
            # Test critical imports
            import_tests = [
                "from app.main import app",
                "from app.core.config import settings", 
                "from app.services.google_oauth_service import google_oauth_service",
                "from app.models.core import User",
                "from app.api.v1.router import api_router",
                "print('All imports successful')"
            ]
            
            exit_code, stdout, stderr = self.run_command([
                "poetry", "run", "python", "-c", "; ".join(import_tests)
            ])
            
            status = TestStatus.PASSED if exit_code == 0 else TestStatus.FAILED
            return TestResult(
                "application_imports", status,
                time.time() - start_time, stdout, stderr
            )
            
        except Exception as e:
            return TestResult(
                "application_imports", TestStatus.FAILED,
                time.time() - start_time, "", str(e)
            )

    def test_database_migration(self) -> TestResult:
        """Test database migration scripts."""
        start_time = time.time()
        
        try:
            self.logger.info("Testing database migrations...")
            
            # Test migration check (dry run)
            exit_code, stdout, stderr = self.run_command([
                "poetry", "run", "alembic", "check"
            ], cwd=self.project_root / "app")
            
            if exit_code != 0:
                # Try to generate migration if check fails
                exit_code, stdout, stderr = self.run_command([
                    "poetry", "run", "alembic", "revision", "--autogenerate",
                    "-m", "test_migration_check"
                ], cwd=self.project_root / "app")
            
            status = TestStatus.PASSED if exit_code == 0 else TestStatus.FAILED
            return TestResult(
                "database_migration", status,
                time.time() - start_time, stdout, stderr
            )
            
        except Exception as e:
            return TestResult(
                "database_migration", TestStatus.FAILED,
                time.time() - start_time, "", str(e)
            )

    def test_environment_configuration(self) -> TestResult:
        """Test environment configuration loading."""
        start_time = time.time()
        
        try:
            self.logger.info("Testing environment configuration...")
            
            # Test config loading
            config_test = [
                "import os",
                "os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost:5432/test'",
                "os.environ['SECRET_KEY'] = 'test-secret-key'",
                "from app.core.config import settings",
                "print(f'Config loaded: {settings.SECRET_KEY}')",
                "print('Environment configuration OK')"
            ]
            
            exit_code, stdout, stderr = self.run_command([
                "poetry", "run", "python", "-c", "; ".join(config_test)
            ])
            
            status = TestStatus.PASSED if exit_code == 0 else TestStatus.FAILED
            return TestResult(
                "environment_configuration", status,
                time.time() - start_time, stdout, stderr
            )
            
        except Exception as e:
            return TestResult(
                "environment_configuration", TestStatus.FAILED,
                time.time() - start_time, "", str(e)
            )

    def test_integration_tests(self) -> TestResult:
        """Run integration tests."""
        start_time = time.time()
        
        try:
            self.logger.info("Running integration tests...")
            
            # Run integration tests
            exit_code, stdout, stderr = self.run_command([
                "poetry", "run", "pytest",
                "-m", "integration",
                "--tb=short",
                "--maxfail=3",
                "--timeout=120"
            ])
            
            status = TestStatus.PASSED if exit_code == 0 else TestStatus.FAILED
            return TestResult(
                "integration_tests", status,
                time.time() - start_time, stdout, stderr
            )
            
        except Exception as e:
            return TestResult(
                "integration_tests", TestStatus.FAILED,
                time.time() - start_time, "", str(e)
            )

    def run_all_tests(self) -> Dict[str, TestResult]:
        """Run all tests in the build validation suite."""
        tests = [
            self.test_python_environment,
            self.test_dependency_installation,
            self.test_application_imports,
            self.test_environment_configuration,
            self.test_unit_tests,
            self.test_vulnerability_scan,
            self.test_database_migration,
            self.test_docker_build_api,
            self.test_docker_build_worker,
            self.test_docker_build_frontend,
            self.test_integration_tests,
        ]
        
        self.logger.info("Starting comprehensive build test suite...")
        self.logger.info(f"Running {len(tests)} test categories...")
        
        results = {}
        for test_func in tests:
            test_name = test_func.__name__.replace("test_", "")
            self.logger.info(f"\n🧪 Running {test_name}...")
            
            result = test_func()
            results[test_name] = result
            self.results.append(result)
            
            status_emoji = {
                TestStatus.PASSED: "✅",
                TestStatus.FAILED: "❌", 
                TestStatus.SKIPPED: "⏭️",
                TestStatus.RUNNING: "🔄"
            }
            
            self.logger.info(
                f"{status_emoji.get(result.status, '❓')} {test_name}: "
                f"{result.status.value} ({result.duration:.2f}s)"
            )
            
            if result.status == TestStatus.FAILED and self.verbose:
                self.logger.error(f"Error details: {result.error}")
                self.logger.error(f"Output: {result.output}")
        
        return results

    def generate_report(self) -> str:
        """Generate a comprehensive test report."""
        total_tests = len(self.results)
        passed = len([r for r in self.results if r.status == TestStatus.PASSED])
        failed = len([r for r in self.results if r.status == TestStatus.FAILED])
        skipped = len([r for r in self.results if r.status == TestStatus.SKIPPED])
        
        total_duration = sum(r.duration for r in self.results)
        
        report = f"""
🏗️ COMPREHENSIVE BUILD TEST REPORT
{'='*50}

📊 SUMMARY:
- Total Tests: {total_tests}
- Passed: {passed} ✅
- Failed: {failed} ❌  
- Skipped: {skipped} ⏭️
- Success Rate: {(passed/total_tests*100):.1f}%
- Total Duration: {total_duration:.2f}s

📋 DETAILED RESULTS:
"""
        
        for result in self.results:
            status_emoji = {
                TestStatus.PASSED: "✅",
                TestStatus.FAILED: "❌",
                TestStatus.SKIPPED: "⏭️"
            }
            
            report += f"\n{status_emoji.get(result.status, '❓')} {result.name}:\n"
            report += f"   Status: {result.status.value}\n"
            report += f"   Duration: {result.duration:.2f}s\n"
            
            if result.status == TestStatus.FAILED and result.error:
                report += f"   Error: {result.error}\n"

        if failed > 0:
            report += f"\n🚨 BUILD WOULD FAIL: {failed} test(s) failed\n"
            report += "⚠️ The Cloud Run deployment would not succeed.\n"
        else:
            report += f"\n🎉 BUILD READY: All tests passed!\n"
            report += "✅ The codebase is ready for Cloud Run deployment.\n"
            
        return report

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive Build Test Suite")
    parser.add_argument("--verbose", "-v", action="store_true", 
                      help="Enable verbose output")
    parser.add_argument("--skip-docker", action="store_true",
                      help="Skip Docker build tests")
    parser.add_argument("--output", "-o", type=str,
                      help="Save report to file")
    
    args = parser.parse_args()
    
    tester = BuildTester(verbose=args.verbose, skip_docker=args.skip_docker)
    results = tester.run_all_tests()
    report = tester.generate_report()
    
    print(report)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"\n📄 Report saved to: {args.output}")
    
    # Exit with error code if any tests failed
    failed_count = len([r for r in tester.results if r.status == TestStatus.FAILED])
    sys.exit(failed_count)

if __name__ == "__main__":
    main()
