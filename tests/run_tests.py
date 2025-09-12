#!/usr/bin/env python3
"""
Test runner script for BRANT PDF pipeline testing.
Provides convenient commands to run different test suites.
"""
import sys
import subprocess
import argparse
from pathlib import Path


class TestRunner:
    """Test runner with different test suite configurations."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_dir = self.project_root / "tests"
    
    def run_command(self, cmd):
        """Run a command and return the result."""
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=self.project_root)
        return result.returncode
    
    def run_unit_tests(self, verbose=False):
        """Run unit tests."""
        cmd = [
            "python", "-m", "pytest", 
            "tests/unit/",
            "-m", "unit",
            "--tb=short"
        ]
        if verbose:
            cmd.extend(["-v", "-s"])
        
        return self.run_command(cmd)
    
    def run_integration_tests(self, verbose=False):
        """Run integration tests."""
        cmd = [
            "python", "-m", "pytest",
            "tests/integration/",
            "-m", "integration",
            "--tb=short"
        ]
        if verbose:
            cmd.extend(["-v", "-s"])
        
        return self.run_command(cmd)
    
    def run_e2e_tests(self, verbose=False):
        """Run end-to-end tests."""
        cmd = [
            "python", "-m", "pytest",
            "tests/e2e/",
            "-m", "e2e",
            "--tb=short"
        ]
        if verbose:
            cmd.extend(["-v", "-s"])
        
        return self.run_command(cmd)
    
    def run_performance_tests(self, verbose=False):
        """Run performance tests."""
        cmd = [
            "python", "-m", "pytest",
            "tests/performance/",
            "-m", "performance",
            "--tb=short",
            "--timeout=600"  # 10 minute timeout for performance tests
        ]
        if verbose:
            cmd.extend(["-v", "-s"])
        
        return self.run_command(cmd)
    
    def run_pdf_tests(self, verbose=False):
        """Run all PDF-related tests."""
        cmd = [
            "python", "-m", "pytest",
            "-m", "pdf",
            "--tb=short"
        ]
        if verbose:
            cmd.extend(["-v", "-s"])
        
        return self.run_command(cmd)
    
    def run_fast_tests(self, verbose=False):
        """Run fast tests only (exclude slow ones)."""
        cmd = [
            "python", "-m", "pytest",
            "-m", "not slow and not performance",
            "--tb=short"
        ]
        if verbose:
            cmd.extend(["-v", "-s"])
        
        return self.run_command(cmd)
    
    def run_all_tests(self, verbose=False, coverage=True):
        """Run all tests with coverage."""
        cmd = ["python", "-m", "pytest"]
        
        if coverage:
            cmd.extend([
                "--cov=app",
                "--cov-report=html",
                "--cov-report=term-missing"
            ])
        
        cmd.append("--tb=short")
        
        if verbose:
            cmd.extend(["-v", "-s"])
        
        return self.run_command(cmd)
    
    def run_parallel_tests(self, workers=4, verbose=False):
        """Run tests in parallel."""
        cmd = [
            "python", "-m", "pytest",
            f"-n", str(workers),
            "--tb=short"
        ]
        if verbose:
            cmd.extend(["-v"])
        
        return self.run_command(cmd)
    
    def run_specific_test(self, test_path, verbose=False):
        """Run a specific test file or test function."""
        cmd = [
            "python", "-m", "pytest",
            test_path,
            "--tb=short"
        ]
        if verbose:
            cmd.extend(["-v", "-s"])
        
        return self.run_command(cmd)
    
    def generate_coverage_report(self):
        """Generate coverage report."""
        cmd = [
            "python", "-m", "coverage", "html",
            "--directory=htmlcov"
        ]
        return self.run_command(cmd)
    
    def check_test_environment(self):
        """Check if test environment is properly set up."""
        print("Checking test environment...")
        
        # Check if test dependencies are installed
        try:
            import pytest
            import pytest_asyncio
            import pytest_cov
            print("✓ Core test dependencies installed")
        except ImportError as e:
            print(f"✗ Missing test dependency: {e}")
            print("Run: pip install -r tests/test_requirements.txt")
            return False
        
        # Check if application dependencies are available
        try:
            from app.core.pdf_processing import extract_text_from_pdf
            from app.models.core import Document
            print("✓ Application modules accessible")
        except ImportError as e:
            print(f"✗ Cannot import application modules: {e}")
            return False
        
        # Check test directory structure
        required_dirs = ["unit", "integration", "e2e", "performance", "fixtures"]
        for dir_name in required_dirs:
            test_subdir = self.test_dir / dir_name
            if test_subdir.exists():
                print(f"✓ Test directory {dir_name}/ exists")
            else:
                print(f"✗ Missing test directory: {dir_name}/")
        
        print("Test environment check completed")
        return True


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="BRANT PDF Pipeline Test Runner")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--no-coverage", action="store_true", help="Skip coverage reporting")
    
    subparsers = parser.add_subparsers(dest="command", help="Test commands")
    
    # Test suite commands
    subparsers.add_parser("unit", help="Run unit tests")
    subparsers.add_parser("integration", help="Run integration tests")
    subparsers.add_parser("e2e", help="Run end-to-end tests")
    subparsers.add_parser("performance", help="Run performance tests")
    subparsers.add_parser("pdf", help="Run PDF-related tests")
    subparsers.add_parser("fast", help="Run fast tests only")
    subparsers.add_parser("all", help="Run all tests")
    
    # Utility commands
    parallel_parser = subparsers.add_parser("parallel", help="Run tests in parallel")
    parallel_parser.add_argument("--workers", "-w", type=int, default=4, help="Number of workers")
    
    specific_parser = subparsers.add_parser("specific", help="Run specific test")
    specific_parser.add_argument("test_path", help="Path to specific test file or function")
    
    subparsers.add_parser("coverage", help="Generate coverage report")
    subparsers.add_parser("check", help="Check test environment")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.command is None:
        parser.print_help()
        return 0
    
    # Environment check
    if args.command == "check":
        success = runner.check_test_environment()
        return 0 if success else 1
    
    # Coverage report generation
    if args.command == "coverage":
        return runner.generate_coverage_report()
    
    # Test execution commands
    coverage = not args.no_coverage if args.command == "all" else False
    
    command_map = {
        "unit": lambda: runner.run_unit_tests(args.verbose),
        "integration": lambda: runner.run_integration_tests(args.verbose),
        "e2e": lambda: runner.run_e2e_tests(args.verbose),
        "performance": lambda: runner.run_performance_tests(args.verbose),
        "pdf": lambda: runner.run_pdf_tests(args.verbose),
        "fast": lambda: runner.run_fast_tests(args.verbose),
        "all": lambda: runner.run_all_tests(args.verbose, coverage),
        "parallel": lambda: runner.run_parallel_tests(args.workers, args.verbose),
        "specific": lambda: runner.run_specific_test(args.test_path, args.verbose)
    }
    
    if args.command in command_map:
        return command_map[args.command]()
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())