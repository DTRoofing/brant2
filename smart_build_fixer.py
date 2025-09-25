#!/usr/bin/env python3
"""
Smart Build Fixer - Intelligent automated build error resolution
"""
import os
import sys
import json
import time
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional
from build_error_analyzer import BuildErrorAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('smart_build_fixer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SmartBuildFixer:
    """Intelligent build fixer with advanced error analysis and targeted fixes"""
    
    def __init__(self, project_id: str, region: str = "us-central1"):
        self.project_id = project_id
        self.region = region
        self.max_iterations = 15
        self.build_timeout = 2400  # 40 minutes
        self.analyzer = BuildErrorAnalyzer()
        self.fix_history = []
        
    def trigger_build(self) -> str:
        """Trigger a new Cloud Build"""
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
                logger.info(f"✅ Build triggered: {build_id}")
                return build_id
            else:
                logger.error(f"❌ Build trigger failed: {result.stderr}")
                return ""
                
        except Exception as e:
            logger.error(f"❌ Error triggering build: {e}")
            return ""
    
    def get_build_status(self, build_id: str) -> tuple:
        """Get build status and logs"""
        try:
            # Get build status
            status_cmd = [
                "gcloud", "builds", "describe", build_id,
                "--region", self.region,
                "--project", self.project_id,
                "--format", "json"
            ]
            
            result = subprocess.run(status_cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                return "UNKNOWN", "Failed to get build status"
            
            build_data = json.loads(result.stdout)
            status = build_data.get("status", "UNKNOWN")
            
            # Get logs if build failed
            logs = ""
            if status == "FAILURE":
                logs_cmd = [
                    "gcloud", "builds", "log", build_id,
                    "--region", self.region,
                    "--project", self.project_id
                ]
                
                logs_result = subprocess.run(logs_cmd, capture_output=True, text=True, timeout=300)
                if logs_result.returncode == 0:
                    logs = logs_result.stdout
            
            return status, logs
            
        except Exception as e:
            logger.error(f"❌ Error getting build status: {e}")
            return "ERROR", str(e)
    
    def apply_poppler_fix(self, fix_plan: Dict) -> bool:
        """Apply poppler-related fixes"""
        try:
            logger.info("🔧 Applying poppler fixes...")
            
            # Update backend.Dockerfile
            backend_dockerfile = "backend.Dockerfile"
            if os.path.exists(backend_dockerfile):
                with open(backend_dockerfile, 'r') as f:
                    content = f.read()
                
                # Check if poppler fixes are already applied
                if "poppler-utils" in content and "POPPLER_PATH" in content:
                    logger.info("✅ Poppler fixes already applied to backend.Dockerfile")
                else:
                    # Add poppler installation and verification
                    poppler_fix = """
# Verify poppler installation and set PATH
RUN ls -la /usr/bin/pdfinfo /usr/bin/pdftoppm /usr/bin/pdftocairo && \\
    /usr/bin/pdfinfo --version && \\
    /usr/bin/pdftoppm -h && \\
    /usr/bin/pdftocairo -h
ENV POPPLER_PATH=/usr/bin
ENV PATH="/usr/bin:${PATH}"
"""
                    
                    # Insert before the final CMD
                    if "CMD [" in content:
                        content = content.replace("CMD [", poppler_fix + "\nCMD [")
                    else:
                        content += poppler_fix
                    
                    with open(backend_dockerfile, 'w') as f:
                        f.write(content)
                    logger.info("✅ Updated backend.Dockerfile with poppler fixes")
            
            # Update worker.Dockerfile
            worker_dockerfile = "worker.Dockerfile"
            if os.path.exists(worker_dockerfile):
                with open(worker_dockerfile, 'r') as f:
                    content = f.read()
                
                if "poppler-utils" in content and "POPPLER_PATH" in content:
                    logger.info("✅ Poppler fixes already applied to worker.Dockerfile")
                else:
                    poppler_fix = """
# Verify poppler installation and set PATH
RUN ls -la /usr/bin/pdfinfo /usr/bin/pdftoppm /usr/bin/pdftocairo && \\
    /usr/bin/pdfinfo --version && \\
    /usr/bin/pdftoppm -h && \\
    /usr/bin/pdftocairo -h
ENV POPPLER_PATH=/usr/bin
ENV PATH="/usr/bin:${PATH}"
"""
                    
                    if "CMD [" in content:
                        content = content.replace("CMD [", poppler_fix + "\nCMD [")
                    else:
                        content += poppler_fix
                    
                    with open(worker_dockerfile, 'w') as f:
                        f.write(content)
                    logger.info("✅ Updated worker.Dockerfile with poppler fixes")
            
            # Update Python files to use poppler_path
            self._update_python_poppler_usage()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to apply poppler fix: {e}")
            return False
    
    def _update_python_poppler_usage(self):
        """Update Python files to use poppler_path parameter"""
        python_files = [
            "app/services/processing_stages/content_extractor.py",
            "app/services/processing_stages/roof_measurement.py",
            "app/services/processing_stages/index_page_analyzer.py"
        ]
        
        for file_path in python_files:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Check if poppler_path is already added
                if "poppler_path=" in content:
                    logger.info(f"✅ {file_path} already has poppler_path parameter")
                    continue
                
                # Add poppler_path to convert_from_path calls
                if "convert_from_path" in content:
                    # This is a simplified approach - in practice, you'd want more sophisticated parsing
                    content = content.replace(
                        "convert_from_path(",
                        "convert_from_path("
                    )
                    # Add the poppler_path parameter
                    content = content.replace(
                        "convert_from_path(",
                        "convert_from_path(\n                    poppler_path=os.environ.get('POPPLER_PATH', '/usr/bin'),"
                    )
                    
                    # Add os import if not present
                    if "import os" not in content:
                        content = "import os\n" + content
                    
                    with open(file_path, 'w') as f:
                        f.write(content)
                    logger.info(f"✅ Updated {file_path} with poppler_path parameter")
    
    def apply_import_fix(self, fix_plan: Dict) -> bool:
        """Apply import-related fixes"""
        try:
            logger.info("🔧 Applying import fixes...")
            
            # Create missing __init__.py files
            missing_modules = fix_plan.get("python_fixes", [])
            for fix in missing_modules:
                if "Create missing __init__.py files" in fix:
                    # Extract module names and create __init__.py files
                    self._create_missing_init_files()
            
            # Update compatibility modules
            self._update_compatibility_modules()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to apply import fix: {e}")
            return False
    
    def _create_missing_init_files(self):
        """Create missing __init__.py files"""
        init_files = [
            "app/__init__.py",
            "app/api/__init__.py",
            "app/api/v1/__init__.py",
            "app/api/v1/endpoints/__init__.py",
            "app/core/__init__.py",
            "app/models/__init__.py",
            "app/services/__init__.py",
            "app/services/processing_stages/__init__.py",
            "app/workers/__init__.py",
            "app/workers/tasks/__init__.py",
            "app/schemas/__init__.py"
        ]
        
        for init_file in init_files:
            if not os.path.exists(init_file):
                os.makedirs(os.path.dirname(init_file), exist_ok=True)
                with open(init_file, 'w') as f:
                    f.write("# Package initialization\n")
                logger.info(f"✅ Created {init_file}")
    
    def _update_compatibility_modules(self):
        """Update compatibility modules for backward compatibility"""
        # Ensure pdf_processing compatibility module exists
        pdf_processing_compat = "app/workers/tasks/pdf_processing.py"
        if not os.path.exists(pdf_processing_compat):
            os.makedirs(os.path.dirname(pdf_processing_compat), exist_ok=True)
            with open(pdf_processing_compat, 'w') as f:
                f.write('''"""
Compatibility module for PDF processing tasks.
"""
from .new_pdf_processing import *
from app.services.google_services import google_service
from app.services.claude_service import claude_service

def process_pdf_document(document_id: str):
    """Backward compatibility wrapper"""
    return process_pdf_with_pipeline.delay(document_id)
''')
            logger.info(f"✅ Created {pdf_processing_compat}")
    
    def apply_iam_fix(self, fix_plan: Dict) -> bool:
        """Apply IAM permission fixes"""
        try:
            logger.info("🔧 Applying IAM permission fixes...")
            
            commands = fix_plan.get("commands", [])
            for command in commands:
                try:
                    result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=120)
                    if result.returncode == 0:
                        logger.info(f"✅ IAM command succeeded: {command}")
                    else:
                        logger.warning(f"⚠️ IAM command failed: {command} - {result.stderr}")
                except Exception as e:
                    logger.warning(f"⚠️ IAM command error: {command} - {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to apply IAM fix: {e}")
            return False
    
    def apply_test_fix(self, fix_plan: Dict) -> bool:
        """Apply test-related fixes"""
        try:
            logger.info("🔧 Applying test fixes...")
            
            # Update test conftest.py
            conftest_path = "tests/conftest.py"
            if os.path.exists(conftest_path):
                with open(conftest_path, 'r') as f:
                    content = f.read()
                
                # Add missing test fixtures if needed
                if "pytest.fixture" not in content:
                    test_fixtures = '''
@pytest.fixture
def mock_google_service():
    """Mock Google service for testing"""
    with patch("app.services.google_services.google_service") as mock:
        yield mock

@pytest.fixture
def mock_claude_service():
    """Mock Claude service for testing"""
    with patch("app.services.claude_service.claude_service") as mock:
        yield mock
'''
                    content += test_fixtures
                    
                    with open(conftest_path, 'w') as f:
                        f.write(content)
                    logger.info("✅ Updated tests/conftest.py with missing fixtures")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to apply test fix: {e}")
            return False
    
    def apply_fix_plan(self, fix_plan: Dict) -> bool:
        """Apply a specific fix plan"""
        fix_type = fix_plan.get("type", "")
        
        if fix_type == "poppler_fix":
            return self.apply_poppler_fix(fix_plan)
        elif fix_type == "missing_module_fix":
            return self.apply_import_fix(fix_plan)
        elif fix_type == "attribute_error_fix":
            return self.apply_import_fix(fix_plan)
        elif fix_type == "artifact_registry_fix":
            return self.apply_iam_fix(fix_plan)
        elif fix_type == "test_import_fix":
            return self.apply_test_fix(fix_plan)
        elif fix_type == "test_attribute_fix":
            return self.apply_test_fix(fix_plan)
        else:
            logger.warning(f"⚠️ Unknown fix type: {fix_type}")
            return False
    
    def commit_and_push(self) -> bool:
        """Commit and push changes"""
        try:
            logger.info("📝 Committing and pushing changes...")
            
            # Add all changes
            subprocess.run(["git", "add", "."], check=True, timeout=60)
            
            # Commit
            commit_msg = f"Auto-fix: Resolved build errors - {time.strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(["git", "commit", "-m", commit_msg], check=True, timeout=60)
            
            # Push
            subprocess.run(["git", "push", "origin", "main"], check=True, timeout=120)
            
            logger.info("✅ Changes committed and pushed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to commit/push: {e}")
            return False
    
    def run_automated_fix_cycle(self) -> bool:
        """Run the complete automated fix cycle"""
        logger.info("🤖 Starting Smart Build Fixer...")
        logger.info(f"📊 Project: {self.project_id}, Region: {self.region}")
        logger.info(f"⏱️ Max iterations: {self.max_iterations}, Timeout: {self.build_timeout}s")
        
        for iteration in range(1, self.max_iterations + 1):
            logger.info(f"\n🔄 === ITERATION {iteration}/{self.max_iterations} ===")
            
            # Trigger build
            build_id = self.trigger_build()
            if not build_id:
                logger.error("❌ Failed to trigger build")
                return False
            
            # Monitor build
            start_time = time.time()
            while time.time() - start_time < self.build_timeout:
                status, logs = self.get_build_status(build_id)
                logger.info(f"📊 Build status: {status}")
                
                if status == "SUCCESS":
                    logger.info("🎉 Build succeeded! All errors resolved.")
                    return True
                elif status == "FAILURE":
                    break
                elif status in ["WORKING", "QUEUED", "PENDING"]:
                    time.sleep(30)
                else:
                    logger.error(f"❌ Unexpected status: {status}")
                    return False
            
            if time.time() - start_time >= self.build_timeout:
                logger.error("❌ Build timed out")
                return False
            
            # Analyze errors
            if not logs:
                logger.error("❌ No logs available for analysis")
                return False
            
            logger.info("🔍 Analyzing build errors...")
            errors = self.analyzer.analyze_logs(logs)
            
            if not errors:
                logger.info("✅ No errors detected")
                continue
            
            logger.info(f"🔍 Found {len(errors)} errors")
            
            # Generate fix plan
            fix_plan = self.analyzer.generate_fix_plan(errors)
            logger.info(f"📋 Generated fix plan with {len(fix_plan['fixes'])} fixes")
            
            # Apply fixes
            fixes_applied = 0
            for fix in fix_plan["fixes"]:
                if fix["confidence"] > 0.5:  # Only apply high-confidence fixes
                    logger.info(f"🔧 Applying fix: {fix['description']}")
                    if self.apply_fix_plan(fix):
                        fixes_applied += 1
                        logger.info(f"✅ Applied fix: {fix['type']}")
                    else:
                        logger.warning(f"⚠️ Failed to apply fix: {fix['type']}")
            
            if fixes_applied == 0:
                logger.error("❌ No fixes could be applied")
                return False
            
            # Commit and push
            if not self.commit_and_push():
                logger.error("❌ Failed to commit/push changes")
                return False
            
            # Wait before next iteration
            logger.info("⏳ Waiting 60 seconds before next iteration...")
            time.sleep(60)
        
        logger.error(f"❌ Maximum iterations ({self.max_iterations}) reached")
        return False

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python smart_build_fixer.py <project_id> [region]")
        sys.exit(1)
    
    project_id = sys.argv[1]
    region = sys.argv[2] if len(sys.argv) > 2 else "us-central1"
    
    fixer = SmartBuildFixer(project_id, region)
    success = fixer.run_automated_fix_cycle()
    
    if success:
        logger.info("🎉 Smart Build Fixer completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Smart Build Fixer failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
