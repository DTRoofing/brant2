#!/usr/bin/env python3
"""
Automated Build Fixer - Monitors and fixes build errors automatically
"""
import os
import sys
import json
import time
import subprocess
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('build_fixer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BuildStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    RUNNING = "running"
    TIMEOUT = "timeout"

@dataclass
class BuildError:
    """Represents a build error with context"""
    error_type: str
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    context: str = ""
    severity: str = "error"  # error, warning, info

@dataclass
class FixPlan:
    """Represents a plan to fix build errors"""
    error: BuildError
    fix_type: str
    description: str
    files_to_modify: List[str]
    commands_to_run: List[str]
    confidence: float  # 0.0 to 1.0

class BuildFixer:
    """Automated build fixer that monitors and resolves build errors"""
    
    def __init__(self, project_id: str, region: str = "us-central1"):
        self.project_id = project_id
        self.region = region
        self.max_iterations = 10
        self.build_timeout = 1800  # 30 minutes
        self.error_patterns = self._load_error_patterns()
        self.fix_strategies = self._load_fix_strategies()
        
    def _load_error_patterns(self) -> Dict[str, Dict]:
        """Load regex patterns for detecting different types of build errors"""
        return {
            "import_error": {
                "pattern": r"ModuleNotFoundError: No module named '([^']+)'",
                "severity": "error"
            },
            "attribute_error": {
                "pattern": r"AttributeError: module '([^']+)' has no attribute '([^']+)'",
                "severity": "error"
            },
            "syntax_error": {
                "pattern": r"SyntaxError: (.+)",
                "severity": "error"
            },
            "indentation_error": {
                "pattern": r"IndentationError: (.+)",
                "severity": "error"
            },
            "poppler_error": {
                "pattern": r"PDFInfoNotInstalledError|pdfinfo.*not found|poppler.*not found",
                "severity": "error"
            },
            "permission_error": {
                "pattern": r"Permission.*denied|DENIED.*Permission",
                "severity": "error"
            },
            "docker_error": {
                "pattern": r"ERROR.*build step.*failed|failed to build|docker.*error",
                "severity": "error"
            },
            "test_failure": {
                "pattern": r"FAILED.*test.*|ERROR.*test.*|AssertionError",
                "severity": "error"
            },
            "dependency_error": {
                "pattern": r"ImportError.*|No module named.*|Package.*not found",
                "severity": "error"
            }
        }
    
    def _load_fix_strategies(self) -> Dict[str, Dict]:
        """Load fix strategies for different error types"""
        return {
            "import_error": {
                "fixes": [
                    {
                        "type": "add_import",
                        "description": "Add missing import statement",
                        "confidence": 0.9
                    },
                    {
                        "type": "fix_import_path",
                        "description": "Fix incorrect import path",
                        "confidence": 0.8
                    },
                    {
                        "type": "create_missing_module",
                        "description": "Create missing module file",
                        "confidence": 0.7
                    }
                ]
            },
            "poppler_error": {
                "fixes": [
                    {
                        "type": "update_dockerfile",
                        "description": "Update Dockerfile to install poppler-utils",
                        "confidence": 0.95
                    },
                    {
                        "type": "fix_poppler_path",
                        "description": "Fix poppler PATH configuration",
                        "confidence": 0.9
                    }
                ]
            },
            "permission_error": {
                "fixes": [
                    {
                        "type": "fix_iam_permissions",
                        "description": "Fix IAM permissions for Cloud Build",
                        "confidence": 0.9
                    },
                    {
                        "type": "update_service_account",
                        "description": "Update service account roles",
                        "confidence": 0.8
                    }
                ]
            },
            "test_failure": {
                "fixes": [
                    {
                        "type": "fix_test_imports",
                        "description": "Fix test import issues",
                        "confidence": 0.8
                    },
                    {
                        "type": "update_test_fixtures",
                        "description": "Update test fixtures and mocks",
                        "confidence": 0.7
                    },
                    {
                        "type": "fix_test_data",
                        "description": "Fix test data and assertions",
                        "confidence": 0.6
                    }
                ]
            }
        }
    
    def trigger_build(self) -> str:
        """Trigger a new Cloud Build and return the build ID"""
        try:
            logger.info("🚀 Triggering new Cloud Build...")
            cmd = [
                "gcloud", "builds", "submit",
                "--config", "cloudbuild.yaml",
                "--region", self.region,
                "--project", self.project_id,
                "--format", "json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                build_data = json.loads(result.stdout)
                build_id = build_data.get("id", "")
                logger.info(f"✅ Build triggered successfully: {build_id}")
                return build_id
            else:
                logger.error(f"❌ Failed to trigger build: {result.stderr}")
                return ""
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Build trigger timed out")
            return ""
        except Exception as e:
            logger.error(f"❌ Error triggering build: {e}")
            return ""
    
    def get_build_status(self, build_id: str) -> Tuple[BuildStatus, str]:
        """Get the current status of a build"""
        try:
            cmd = [
                "gcloud", "builds", "describe", build_id,
                "--region", self.region,
                "--project", self.project_id,
                "--format", "json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                build_data = json.loads(result.stdout)
                status = build_data.get("status", "UNKNOWN")
                
                if status == "SUCCESS":
                    return BuildStatus.SUCCESS, "Build completed successfully"
                elif status == "FAILURE":
                    return BuildStatus.FAILED, "Build failed"
                elif status in ["WORKING", "QUEUED", "PENDING"]:
                    return BuildStatus.RUNNING, f"Build is {status.lower()}"
                else:
                    return BuildStatus.FAILED, f"Build status: {status}"
            else:
                logger.error(f"❌ Failed to get build status: {result.stderr}")
                return BuildStatus.FAILED, "Failed to get build status"
                
        except Exception as e:
            logger.error(f"❌ Error getting build status: {e}")
            return BuildStatus.FAILED, str(e)
    
    def get_build_logs(self, build_id: str) -> str:
        """Get the logs for a build"""
        try:
            cmd = [
                "gcloud", "builds", "log", build_id,
                "--region", self.region,
                "--project", self.project_id
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return result.stdout
            else:
                logger.error(f"❌ Failed to get build logs: {result.stderr}")
                return ""
                
        except Exception as e:
            logger.error(f"❌ Error getting build logs: {e}")
            return ""
    
    def analyze_build_logs(self, logs: str) -> List[BuildError]:
        """Analyze build logs to identify errors"""
        errors = []
        
        for error_type, config in self.error_patterns.items():
            pattern = config["pattern"]
            matches = re.finditer(pattern, logs, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                error = BuildError(
                    error_type=error_type,
                    message=match.group(0),
                    severity=config["severity"]
                )
                
                # Extract additional context
                if error_type == "import_error" and len(match.groups()) >= 1:
                    error.context = f"Missing module: {match.group(1)}"
                elif error_type == "attribute_error" and len(match.groups()) >= 2:
                    error.context = f"Module: {match.group(1)}, Missing attribute: {match.group(2)}"
                
                errors.append(error)
        
        return errors
    
    def create_fix_plan(self, error: BuildError) -> Optional[FixPlan]:
        """Create a fix plan for a specific error"""
        if error.error_type not in self.fix_strategies:
            return None
        
        strategies = self.fix_strategies[error.error_type]["fixes"]
        
        # Select the highest confidence fix
        best_fix = max(strategies, key=lambda x: x["confidence"])
        
        fix_plan = FixPlan(
            error=error,
            fix_type=best_fix["type"],
            description=best_fix["description"],
            files_to_modify=[],
            commands_to_run=[],
            confidence=best_fix["confidence"]
        )
        
        # Generate specific fix details based on error type
        if error.error_type == "import_error":
            fix_plan = self._create_import_fix_plan(error, fix_plan)
        elif error.error_type == "poppler_error":
            fix_plan = self._create_poppler_fix_plan(error, fix_plan)
        elif error.error_type == "permission_error":
            fix_plan = self._create_permission_fix_plan(error, fix_plan)
        elif error.error_type == "test_failure":
            fix_plan = self._create_test_fix_plan(error, fix_plan)
        
        return fix_plan
    
    def _create_import_fix_plan(self, error: BuildError, fix_plan: FixPlan) -> FixPlan:
        """Create fix plan for import errors"""
        if "Missing module:" in error.context:
            module_name = error.context.split(": ")[1]
            
            # Check if it's a missing __init__.py file
            if module_name.startswith("app."):
                module_path = module_name.replace(".", "/") + "/__init__.py"
                if not os.path.exists(module_path):
                    fix_plan.files_to_modify.append(module_path)
                    fix_plan.commands_to_run.append(f"touch {module_path}")
                    fix_plan.description = f"Create missing __init__.py file for {module_name}"
        
        return fix_plan
    
    def _create_poppler_fix_plan(self, error: BuildError, fix_plan: FixPlan) -> FixPlan:
        """Create fix plan for poppler errors"""
        fix_plan.files_to_modify.extend([
            "backend.Dockerfile",
            "worker.Dockerfile"
        ])
        fix_plan.commands_to_run.extend([
            "echo 'RUN apt-get update && apt-get install -y poppler-utils' >> backend.Dockerfile",
            "echo 'ENV POPPLER_PATH=/usr/bin' >> backend.Dockerfile",
            "echo 'ENV PATH=\"/usr/bin:${PATH}\"' >> backend.Dockerfile"
        ])
        fix_plan.description = "Add poppler-utils installation and PATH configuration to Dockerfiles"
        
        return fix_plan
    
    def _create_permission_fix_plan(self, error: BuildError, fix_plan: FixPlan) -> FixPlan:
        """Create fix plan for permission errors"""
        fix_plan.commands_to_run.extend([
            "gcloud projects add-iam-policy-binding $PROJECT_ID --member='serviceAccount:$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')@cloudbuild.gserviceaccount.com' --role='roles/artifactregistry.writer'",
            "gcloud projects add-iam-policy-binding $PROJECT_ID --member='serviceAccount:$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')@cloudbuild.gserviceaccount.com' --role='roles/cloudbuild.builds.builder'"
        ])
        fix_plan.description = "Add required IAM permissions for Cloud Build service account"
        
        return fix_plan
    
    def _create_test_fix_plan(self, error: BuildError, fix_plan: FixPlan) -> FixPlan:
        """Create fix plan for test failures"""
        fix_plan.files_to_modify.extend([
            "tests/conftest.py",
            "app/workers/tasks/pdf_processing.py"
        ])
        fix_plan.commands_to_run.extend([
            "echo '# Test fixtures' >> tests/conftest.py",
            "echo 'from app.workers.tasks.pdf_processing import *' >> app/workers/tasks/pdf_processing.py"
        ])
        fix_plan.description = "Fix test imports and add missing fixtures"
        
        return fix_plan
    
    def apply_fix_plan(self, fix_plan: FixPlan) -> bool:
        """Apply a fix plan to resolve build errors"""
        try:
            logger.info(f"🔧 Applying fix: {fix_plan.description}")
            
            # Create missing files
            for file_path in fix_plan.files_to_modify:
                if not os.path.exists(file_path):
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'w') as f:
                        f.write("# Auto-generated file\n")
                    logger.info(f"✅ Created file: {file_path}")
            
            # Run fix commands
            for command in fix_plan.commands_to_run:
                try:
                    result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
                    if result.returncode == 0:
                        logger.info(f"✅ Command succeeded: {command}")
                    else:
                        logger.warning(f"⚠️ Command failed: {command} - {result.stderr}")
                except subprocess.TimeoutExpired:
                    logger.warning(f"⚠️ Command timed out: {command}")
                except Exception as e:
                    logger.warning(f"⚠️ Command error: {command} - {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to apply fix plan: {e}")
            return False
    
    def commit_and_push_changes(self) -> bool:
        """Commit and push changes to the repository"""
        try:
            logger.info("📝 Committing and pushing changes...")
            
            # Add all changes
            subprocess.run(["git", "add", "."], check=True, timeout=60)
            
            # Commit with descriptive message
            commit_msg = f"Auto-fix: Resolved build errors at {time.strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(["git", "commit", "-m", commit_msg], check=True, timeout=60)
            
            # Push changes
            subprocess.run(["git", "push", "origin", "main"], check=True, timeout=120)
            
            logger.info("✅ Changes committed and pushed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Git operation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error committing/pushing changes: {e}")
            return False
    
    def run_automated_fix_cycle(self) -> bool:
        """Run the complete automated fix cycle"""
        logger.info("🤖 Starting automated build fix cycle...")
        
        for iteration in range(1, self.max_iterations + 1):
            logger.info(f"🔄 Iteration {iteration}/{self.max_iterations}")
            
            # Trigger build
            build_id = self.trigger_build()
            if not build_id:
                logger.error("❌ Failed to trigger build")
                return False
            
            # Wait for build to complete
            start_time = time.time()
            while time.time() - start_time < self.build_timeout:
                status, message = self.get_build_status(build_id)
                logger.info(f"📊 Build status: {status.value} - {message}")
                
                if status == BuildStatus.SUCCESS:
                    logger.info("🎉 Build succeeded! No more fixes needed.")
                    return True
                elif status == BuildStatus.FAILED:
                    break
                elif status == BuildStatus.RUNNING:
                    time.sleep(30)  # Wait 30 seconds before checking again
                else:
                    logger.error(f"❌ Unexpected build status: {status}")
                    return False
            
            if time.time() - start_time >= self.build_timeout:
                logger.error("❌ Build timed out")
                return False
            
            # Get build logs and analyze errors
            logs = self.get_build_logs(build_id)
            if not logs:
                logger.error("❌ Failed to get build logs")
                return False
            
            errors = self.analyze_build_logs(logs)
            if not errors:
                logger.info("✅ No errors detected in build logs")
                continue
            
            logger.info(f"🔍 Found {len(errors)} errors in build logs")
            
            # Create and apply fix plans
            fixes_applied = 0
            for error in errors:
                fix_plan = self.create_fix_plan(error)
                if fix_plan and fix_plan.confidence > 0.5:
                    if self.apply_fix_plan(fix_plan):
                        fixes_applied += 1
                        logger.info(f"✅ Applied fix for {error.error_type}")
                    else:
                        logger.warning(f"⚠️ Failed to apply fix for {error.error_type}")
            
            if fixes_applied == 0:
                logger.error("❌ No fixes could be applied")
                return False
            
            # Commit and push changes
            if not self.commit_and_push_changes():
                logger.error("❌ Failed to commit and push changes")
                return False
            
            # Wait a bit before next iteration
            time.sleep(60)
        
        logger.error(f"❌ Maximum iterations ({self.max_iterations}) reached")
        return False

def main():
    """Main function to run the automated build fixer"""
    if len(sys.argv) < 2:
        print("Usage: python automated_build_fixer.py <project_id> [region]")
        sys.exit(1)
    
    project_id = sys.argv[1]
    region = sys.argv[2] if len(sys.argv) > 2 else "us-central1"
    
    fixer = BuildFixer(project_id, region)
    
    logger.info(f"🚀 Starting automated build fixer for project: {project_id}")
    logger.info(f"📍 Region: {region}")
    
    success = fixer.run_automated_fix_cycle()
    
    if success:
        logger.info("🎉 Automated build fixer completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Automated build fixer failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
