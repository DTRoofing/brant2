#!/usr/bin/env python3
"""
Dependency Verification Suite

Validates all dependencies and potential import issues that could cause
build failures in Cloud Run environment.

Usage:
    python scripts/dependency_verifier.py [--fix-issues] [--verbose]
"""

import os
import sys
import subprocess
import importlib
import pkg_resources
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
import logging

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

@dataclass
class DependencyIssue:
    """Represents a dependency-related issue."""
    package: str
    issue_type: str
    description: str
    severity: str  # "critical", "warning", "info"
    fix_suggestion: Optional[str] = None

class DependencyVerifier:
    """Comprehensive dependency verification for Cloud Run deployment."""
    
    def __init__(self, verbose: bool = False, fix_issues: bool = False):
        self.verbose = verbose
        self.fix_issues = fix_issues
        self.project_root = Path(__file__).parent.parent
        self.issues: List[DependencyIssue] = []
        
        # Setup logging
        level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(level=level, format='%(levelname)s: %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Critical packages for the application
        self.critical_packages = {
            'fastapi', 'uvicorn', 'sqlalchemy', 'alembic', 'celery', 'redis',
            'pydantic', 'asyncpg', 'google-cloud-documentai', 'google-cloud-storage',
            'google-cloud-vision', 'authlib', 'httpx', 'pyjwt'
        }
        
    def log_issue(self, package: str, issue_type: str, description: str, 
                  severity: str, fix_suggestion: str = None):
        """Log a dependency issue."""
        issue = DependencyIssue(package, issue_type, description, severity, fix_suggestion)
        self.issues.append(issue)
        
        severity_emoji = {
            "critical": "🚨",
            "warning": "⚠️", 
            "info": "ℹ️"
        }
        
        self.logger.warning(
            f"{severity_emoji.get(severity, '❓')} {package}: {description}"
        )
        
    def run_command(self, cmd: List[str]) -> Tuple[int, str, str]:
        """Run command and return exit code, stdout, stderr."""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)

    def verify_poetry_configuration(self) -> bool:
        """Verify Poetry configuration and lock file consistency."""
        self.logger.info("🔍 Verifying Poetry configuration...")
        
        # Check if pyproject.toml exists
        pyproject_path = self.project_root / "pyproject.toml"
        if not pyproject_path.exists():
            self.log_issue(
                "poetry", "missing_file", "pyproject.toml not found",
                "critical", "Run 'poetry init' to create pyproject.toml"
            )
            return False
            
        # Check if poetry.lock exists
        lock_path = self.project_root / "poetry.lock"
        if not lock_path.exists():
            self.log_issue(
                "poetry", "missing_file", "poetry.lock not found",
                "critical", "Run 'poetry lock' to generate lock file"
            )
            
            if self.fix_issues:
                self.logger.info("🔧 Attempting to generate poetry.lock...")
                exit_code, stdout, stderr = self.run_command(["poetry", "lock"])
                if exit_code == 0:
                    self.logger.info("✅ Generated poetry.lock successfully")
                else:
                    self.logger.error(f"❌ Failed to generate poetry.lock: {stderr}")
                    return False
            else:
                return False
                
        # Verify lock file is up to date
        exit_code, stdout, stderr = self.run_command(["poetry", "lock", "--check"])
        if exit_code != 0:
            self.log_issue(
                "poetry", "outdated_lock", "poetry.lock is out of sync with pyproject.toml",
                "critical", "Run 'poetry lock --no-update' to update lock file"
            )
            
            if self.fix_issues:
                self.logger.info("🔧 Updating poetry.lock...")
                exit_code, stdout, stderr = self.run_command(["poetry", "lock", "--no-update"])
                if exit_code != 0:
                    self.logger.error(f"❌ Failed to update poetry.lock: {stderr}")
                    return False
            else:
                return False
                
        self.logger.info("✅ Poetry configuration verified")
        return True

    def verify_critical_packages(self) -> bool:
        """Verify all critical packages are available and importable."""
        self.logger.info("🔍 Verifying critical packages...")
        
        success = True
        
        for package in self.critical_packages:
            try:
                # Try to get package info
                try:
                    pkg_resources.get_distribution(package)
                except pkg_resources.DistributionNotFound:
                    self.log_issue(
                        package, "missing_package", f"Critical package {package} not installed",
                        "critical", f"Add {package} to pyproject.toml and run 'poetry install'"
                    )
                    success = False
                    continue
                    
                # Try to import the package
                import_name = package.replace('-', '_').replace('google_cloud_', 'google.cloud.')
                
                # Special cases for import names
                import_mappings = {
                    'google_cloud_documentai': 'google.cloud.documentai',
                    'google_cloud_storage': 'google.cloud.storage', 
                    'google_cloud_vision': 'google.cloud.vision',
                    'pyjwt': 'jwt'
                }
                
                import_name = import_mappings.get(package, import_name)
                
                try:
                    importlib.import_module(import_name)
                    self.logger.debug(f"✅ {package} imports successfully")
                except ImportError as e:
                    self.log_issue(
                        package, "import_error", f"Failed to import {import_name}: {e}",
                        "critical", f"Check {package} installation and dependencies"
                    )
                    success = False
                    
            except Exception as e:
                self.log_issue(
                    package, "verification_error", f"Error verifying {package}: {e}",
                    "warning"
                )
                
        return success

    def verify_application_imports(self) -> bool:
        """Verify all application modules can be imported."""
        self.logger.info("🔍 Verifying application imports...")
        
        # Critical application modules
        app_modules = [
            "app.main",
            "app.core.config", 
            "app.core.auth",
            "app.services.google_oauth_service",
            "app.services.google_services",
            "app.models.core",
            "app.api.v1.router",
            "app.workers.celery_app"
        ]
        
        success = True
        
        for module_name in app_modules:
            try:
                importlib.import_module(module_name)
                self.logger.debug(f"✅ {module_name} imports successfully")
            except ImportError as e:
                self.log_issue(
                    module_name, "import_error", f"Failed to import {module_name}: {e}",
                    "critical", f"Check {module_name} dependencies and syntax"
                )
                success = False
            except Exception as e:
                self.log_issue(
                    module_name, "import_error", f"Error importing {module_name}: {e}",
                    "warning"
                )
                
        return success

    def verify_system_dependencies(self) -> bool:
        """Verify system dependencies are available (for Docker builds)."""
        self.logger.info("🔍 Verifying system dependencies...")
        
        # System dependencies required for the application
        system_deps = [
            ("tesseract", "tesseract --version"),
            ("poppler", "pdfinfo -v"),
            ("curl", "curl --version")
        ]
        
        success = True
        
        for dep_name, test_cmd in system_deps:
            exit_code, stdout, stderr = self.run_command(test_cmd.split())
            if exit_code != 0:
                self.log_issue(
                    dep_name, "missing_system_dep", 
                    f"System dependency {dep_name} not available",
                    "warning", f"Install {dep_name} system package"
                )
                # Don't fail for system deps in local environment
            else:
                self.logger.debug(f"✅ {dep_name} available")
                
        return success

    def check_version_conflicts(self) -> bool:
        """Check for version conflicts in dependencies."""
        self.logger.info("🔍 Checking for version conflicts...")
        
        try:
            # Get installed packages
            exit_code, stdout, stderr = self.run_command(["pip", "list", "--format=json"])
            if exit_code != 0:
                self.log_issue(
                    "pip", "list_error", f"Failed to list packages: {stderr}",
                    "warning"
                )
                return True
                
            packages = json.loads(stdout)
            
            # Check for known problematic combinations
            package_versions = {pkg["name"].lower(): pkg["version"] for pkg in packages}
            
            # Check Python version compatibility
            python_version = sys.version_info
            if python_version < (3, 11):
                self.log_issue(
                    "python", "version_incompatible", 
                    f"Python {python_version.major}.{python_version.minor} may be incompatible. Recommend Python 3.11+",
                    "warning"
                )
                
            # Check for specific version conflicts
            if "sqlalchemy" in package_versions:
                sqlalchemy_version = package_versions["sqlalchemy"]
                if sqlalchemy_version.startswith("1."):
                    self.log_issue(
                        "sqlalchemy", "version_outdated",
                        f"SQLAlchemy {sqlalchemy_version} is v1.x, application requires v2.x",
                        "critical", "Update SQLAlchemy to version 2.x"
                    )
                    
            # Check FastAPI compatibility
            if "fastapi" in package_versions and "uvicorn" in package_versions:
                fastapi_version = package_versions["fastapi"]
                uvicorn_version = package_versions["uvicorn"]
                
                # Basic version checks (can be expanded)
                if fastapi_version.startswith("0.") and not fastapi_version.startswith("0.1"):
                    self.logger.debug(f"✅ FastAPI {fastapi_version} compatible")
                    
        except Exception as e:
            self.log_issue(
                "pip", "check_error", f"Error checking versions: {e}",
                "warning"
            )
            
        return True

    def run_security_audit(self) -> bool:
        """Run security audit on dependencies."""
        self.logger.info("🔍 Running security audit...")
        
        try:
            # Install pip-audit if not available
            exit_code, stdout, stderr = self.run_command([
                sys.executable, "-m", "pip", "install", "pip-audit"
            ])
            
            # Run security audit
            exit_code, stdout, stderr = self.run_command(["pip-audit", "--format=json"])
            
            if exit_code == 0:
                # No vulnerabilities found
                self.logger.info("✅ No security vulnerabilities found")
                return True
            else:
                # Parse vulnerabilities if JSON format
                try:
                    if stdout.strip():
                        vulnerabilities = json.loads(stdout)
                        for vuln in vulnerabilities:
                            self.log_issue(
                                vuln.get("name", "unknown"), "security_vulnerability",
                                f"Security vulnerability: {vuln.get('vulnerability_description', 'Unknown')}",
                                "warning", f"Update to version {vuln.get('fix_versions', ['latest'])[0]}"
                            )
                except json.JSONDecodeError:
                    self.log_issue(
                        "pip-audit", "security_check", f"Security issues found: {stderr}",
                        "warning"
                    )
                    
                return True  # Don't fail build for security warnings
                
        except Exception as e:
            self.log_issue(
                "pip-audit", "audit_error", f"Security audit failed: {e}",
                "info"
            )
            
        return True

    def verify_all_dependencies(self) -> Dict[str, bool]:
        """Run comprehensive dependency verification."""
        self.logger.info("🔍 Starting comprehensive dependency verification...")
        
        checks = {
            "poetry_configuration": self.verify_poetry_configuration,
            "critical_packages": self.verify_critical_packages,
            "application_imports": self.verify_application_imports,
            "system_dependencies": self.verify_system_dependencies,
            "version_conflicts": self.check_version_conflicts,
            "security_audit": self.run_security_audit
        }
        
        results = {}
        for check_name, check_func in checks.items():
            self.logger.info(f"\n🧪 Running {check_name.replace('_', ' ')}...")
            try:
                results[check_name] = check_func()
            except Exception as e:
                self.logger.error(f"❌ {check_name} failed with error: {e}")
                results[check_name] = False
                
        return results

    def generate_report(self) -> str:
        """Generate comprehensive dependency report."""
        critical_issues = [i for i in self.issues if i.severity == "critical"]
        warning_issues = [i for i in self.issues if i.severity == "warning"]
        info_issues = [i for i in self.issues if i.severity == "info"]
        
        report = f"""
🔍 DEPENDENCY VERIFICATION REPORT
{'='*50}

📊 SUMMARY:
- Critical Issues: {len(critical_issues)} 🚨
- Warnings: {len(warning_issues)} ⚠️
- Info: {len(info_issues)} ℹ️
- Total Issues: {len(self.issues)}

"""
        
        if critical_issues:
            report += "🚨 CRITICAL ISSUES (Will cause build failure):\n"
            for issue in critical_issues:
                report += f"  • {issue.package}: {issue.description}\n"
                if issue.fix_suggestion:
                    report += f"    Fix: {issue.fix_suggestion}\n"
            report += "\n"
            
        if warning_issues:
            report += "⚠️ WARNINGS (May cause runtime issues):\n"
            for issue in warning_issues:
                report += f"  • {issue.package}: {issue.description}\n"
                if issue.fix_suggestion:
                    report += f"    Fix: {issue.fix_suggestion}\n"
            report += "\n"
            
        if len(critical_issues) == 0:
            report += "✅ NO CRITICAL ISSUES FOUND\n"
            report += "🚀 Dependencies are ready for Cloud Run deployment!\n"
        else:
            report += f"❌ {len(critical_issues)} CRITICAL ISSUE(S) MUST BE FIXED\n"
            report += "⚠️ Cloud Run deployment will likely fail.\n"
            
        return report

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Dependency Verification Suite")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose output")
    parser.add_argument("--fix-issues", action="store_true",
                       help="Attempt to fix issues automatically")
    parser.add_argument("--output", "-o", type=str,
                       help="Save report to file")
    
    args = parser.parse_args()
    
    verifier = DependencyVerifier(verbose=args.verbose, fix_issues=args.fix_issues)
    results = verifier.verify_all_dependencies()
    report = verifier.generate_report()
    
    print(report)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"\n📄 Report saved to: {args.output}")
        
    # Exit with error code if critical issues found
    critical_count = len([i for i in verifier.issues if i.severity == "critical"])
    sys.exit(critical_count)

if __name__ == "__main__":
    main()
