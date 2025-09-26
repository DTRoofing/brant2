#!/usr/bin/env python3
"""
Build Error Analyzer - Advanced error detection and fix generation
"""
import re
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

@dataclass
class ErrorPattern:
    """Represents a specific error pattern with fix suggestions"""
    name: str
    pattern: str
    severity: str
    fix_type: str
    fix_template: str
    confidence: float

class BuildErrorAnalyzer:
    """Advanced build error analyzer with specific fix templates"""
    
    def __init__(self):
        self.error_patterns = self._load_advanced_patterns()
    
    def _load_advanced_patterns(self) -> List[ErrorPattern]:
        """Load advanced error patterns with specific fix templates"""
        return [
            # Poppler/PDF processing errors
            ErrorPattern(
                name="poppler_not_found",
                pattern=r"PDFInfoNotInstalledError|pdfinfo.*not found|poppler.*not found",
                severity="error",
                fix_type="dockerfile_update",
                fix_template="poppler_dockerfile_fix",
                confidence=0.95
            ),
            
            # Import errors
            ErrorPattern(
                name="missing_module",
                pattern=r"ModuleNotFoundError: No module named '([^']+)'",
                severity="error",
                fix_type="import_fix",
                fix_template="missing_module_fix",
                confidence=0.9
            ),
            
            ErrorPattern(
                name="attribute_error",
                pattern=r"AttributeError: module '([^']+)' has no attribute '([^']+)'",
                severity="error",
                fix_type="import_fix",
                fix_template="attribute_error_fix",
                confidence=0.8
            ),
            
            # Permission errors
            ErrorPattern(
                name="artifact_registry_permission",
                pattern=r"DENIED.*Permission.*artifactregistry\.repositories\.uploadArtifacts",
                severity="error",
                fix_type="iam_fix",
                fix_template="artifact_registry_permission_fix",
                confidence=0.95
            ),
            
            # Test failures
            ErrorPattern(
                name="test_import_failure",
                pattern=r"FAILED.*test.*ImportError|ERROR.*test.*ModuleNotFoundError",
                severity="error",
                fix_type="test_fix",
                fix_template="test_import_fix",
                confidence=0.8
            ),
            
            ErrorPattern(
                name="test_attribute_error",
                pattern=r"FAILED.*test.*AttributeError.*has no attribute",
                severity="error",
                fix_type="test_fix",
                fix_template="test_attribute_fix",
                confidence=0.8
            ),
            
            # Docker build errors
            ErrorPattern(
                name="docker_build_failure",
                pattern=r"ERROR.*build step.*failed|failed to build.*Dockerfile",
                severity="error",
                fix_type="dockerfile_fix",
                fix_template="dockerfile_build_fix",
                confidence=0.7
            ),
            
            # Syntax errors
            ErrorPattern(
                name="syntax_error",
                pattern=r"SyntaxError: (.+)",
                severity="error",
                fix_type="syntax_fix",
                fix_template="syntax_error_fix",
                confidence=0.6
            ),
            
            # Indentation errors
            ErrorPattern(
                name="indentation_error",
                pattern=r"IndentationError: (.+)",
                severity="error",
                fix_type="syntax_fix",
                fix_template="indentation_fix",
                confidence=0.8
            )
        ]
    
    def analyze_logs(self, logs: str) -> List[Dict]:
        """Analyze build logs and return detailed error information"""
        errors = []
        
        for pattern in self.error_patterns:
            matches = re.finditer(pattern.pattern, logs, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                error_info = {
                    "type": pattern.name,
                    "severity": pattern.severity,
                    "message": match.group(0),
                    "fix_type": pattern.fix_type,
                    "fix_template": pattern.fix_template,
                    "confidence": pattern.confidence,
                    "groups": match.groups(),
                    "context": self._extract_context(logs, match.start(), match.end())
                }
                errors.append(error_info)
        
        return errors
    
    def _extract_context(self, logs: str, start: int, end: int, context_lines: int = 3) -> str:
        """Extract context around an error"""
        lines = logs.split('\n')
        error_line = logs[:start].count('\n')
        
        start_line = max(0, error_line - context_lines)
        end_line = min(len(lines), error_line + context_lines + 1)
        
        context_lines_list = lines[start_line:end_line]
        return '\n'.join(context_lines_list)
    
    def generate_fix_plan(self, errors: List[Dict]) -> Dict:
        """Generate a comprehensive fix plan for all errors"""
        fix_plan = {
            "total_errors": len(errors),
            "fixes": [],
            "priority_order": [],
            "estimated_time": 0
        }
        
        # Group errors by type
        error_groups = {}
        for error in errors:
            error_type = error["type"]
            if error_type not in error_groups:
                error_groups[error_type] = []
            error_groups[error_type].append(error)
        
        # Generate fixes for each error type
        for error_type, error_list in error_groups.items():
            fix = self._generate_fix_for_type(error_type, error_list)
            if fix:
                fix_plan["fixes"].append(fix)
        
        # Sort by priority (highest confidence first)
        fix_plan["fixes"].sort(key=lambda x: x["confidence"], reverse=True)
        fix_plan["priority_order"] = [fix["type"] for fix in fix_plan["fixes"]]
        
        # Estimate time (5 minutes per fix)
        fix_plan["estimated_time"] = len(fix_plan["fixes"]) * 5
        
        return fix_plan
    
    def _generate_fix_for_type(self, error_type: str, errors: List[Dict]) -> Optional[Dict]:
        """Generate fix for a specific error type"""
        if error_type == "poppler_not_found":
            return self._generate_poppler_fix(errors)
        elif error_type == "missing_module":
            return self._generate_missing_module_fix(errors)
        elif error_type == "attribute_error":
            return self._generate_attribute_error_fix(errors)
        elif error_type == "artifact_registry_permission":
            return self._generate_artifact_registry_fix(errors)
        elif error_type == "test_import_failure":
            return self._generate_test_import_fix(errors)
        elif error_type == "test_attribute_error":
            return self._generate_test_attribute_fix(errors)
        elif error_type == "docker_build_failure":
            return self._generate_dockerfile_fix(errors)
        elif error_type == "syntax_error":
            return self._generate_syntax_fix(errors)
        elif error_type == "indentation_error":
            return self._generate_indentation_fix(errors)
        
        return None
    
    def _generate_poppler_fix(self, errors: List[Dict]) -> Dict:
        """Generate fix for poppler errors"""
        return {
            "type": "poppler_fix",
            "description": "Fix poppler-utils installation and PATH configuration",
            "confidence": 0.95,
            "files_to_modify": ["backend.Dockerfile", "worker.Dockerfile"],
            "commands": [
                "echo 'RUN apt-get update && apt-get install -y poppler-utils' >> backend.Dockerfile",
                "echo 'RUN which pdfinfo && which pdftoppm && which pdftocairo' >> backend.Dockerfile",
                "echo 'ENV POPPLER_PATH=/usr/bin' >> backend.Dockerfile",
                "echo 'ENV PATH=\"/usr/bin:${PATH}\"' >> backend.Dockerfile"
            ],
            "python_fixes": [
                "Add poppler_path parameter to all convert_from_path calls",
                "Update import statements to use correct poppler utilities"
            ]
        }
    
    def _generate_missing_module_fix(self, errors: List[Dict]) -> Dict:
        """Generate fix for missing module errors"""
        missing_modules = set()
        for error in errors:
            if error["groups"]:
                missing_modules.add(error["groups"][0])
        
        return {
            "type": "missing_module_fix",
            "description": f"Fix missing modules: {', '.join(missing_modules)}",
            "confidence": 0.9,
            "files_to_modify": [],
            "commands": [],
            "python_fixes": [
                f"Create missing __init__.py files for: {', '.join(missing_modules)}",
                "Add proper import statements",
                "Check for typos in module names"
            ]
        }
    
    def _generate_attribute_error_fix(self, errors: List[Dict]) -> Dict:
        """Generate fix for attribute errors"""
        return {
            "type": "attribute_error_fix",
            "description": "Fix missing attributes in modules",
            "confidence": 0.8,
            "files_to_modify": [],
            "commands": [],
            "python_fixes": [
                "Check if the attribute exists in the module",
                "Add missing attributes or fix import paths",
                "Update module exports in __init__.py files"
            ]
        }
    
    def _generate_artifact_registry_fix(self, errors: List[Dict]) -> Dict:
        """Generate fix for artifact registry permission errors"""
        return {
            "type": "artifact_registry_fix",
            "description": "Fix IAM permissions for Artifact Registry",
            "confidence": 0.95,
            "files_to_modify": [],
            "commands": [
                "gcloud projects add-iam-policy-binding $PROJECT_ID --member='serviceAccount:$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')@cloudbuild.gserviceaccount.com' --role='roles/artifactregistry.writer'",
                "gcloud projects add-iam-policy-binding $PROJECT_ID --member='serviceAccount:$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')@cloudbuild.gserviceaccount.com' --role='roles/cloudbuild.builds.builder'"
            ],
            "python_fixes": []
        }
    
    def _generate_test_import_fix(self, errors: List[Dict]) -> Dict:
        """Generate fix for test import failures"""
        return {
            "type": "test_import_fix",
            "description": "Fix test import issues",
            "confidence": 0.8,
            "files_to_modify": ["tests/conftest.py", "app/workers/tasks/pdf_processing.py"],
            "commands": [],
            "python_fixes": [
                "Add missing imports to test files",
                "Create compatibility modules for backward compatibility",
                "Update test fixtures and mocks"
            ]
        }
    
    def _generate_test_attribute_fix(self, errors: List[Dict]) -> Dict:
        """Generate fix for test attribute errors"""
        return {
            "type": "test_attribute_fix",
            "description": "Fix missing attributes in test modules",
            "confidence": 0.8,
            "files_to_modify": [],
            "commands": [],
            "python_fixes": [
                "Add missing attributes to modules",
                "Update module exports",
                "Fix import paths in test files"
            ]
        }
    
    def _generate_dockerfile_fix(self, errors: List[Dict]) -> Dict:
        """Generate fix for dockerfile build failures"""
        return {
            "type": "dockerfile_fix",
            "description": "Fix Dockerfile build issues",
            "confidence": 0.7,
            "files_to_modify": ["backend.Dockerfile", "worker.Dockerfile"],
            "commands": [],
            "python_fixes": [
                "Check Dockerfile syntax",
                "Verify all dependencies are installed",
                "Update build steps and environment variables"
            ]
        }
    
    def _generate_syntax_fix(self, errors: List[Dict]) -> Dict:
        """Generate fix for syntax errors"""
        return {
            "type": "syntax_fix",
            "description": "Fix Python syntax errors",
            "confidence": 0.6,
            "files_to_modify": [],
            "commands": [],
            "python_fixes": [
                "Check Python syntax in all files",
                "Fix missing colons, parentheses, or brackets",
                "Verify indentation consistency"
            ]
        }
    
    def _generate_indentation_fix(self, errors: List[Dict]) -> Dict:
        """Generate fix for indentation errors"""
        return {
            "type": "indentation_fix",
            "description": "Fix Python indentation errors",
            "confidence": 0.8,
            "files_to_modify": [],
            "commands": [],
            "python_fixes": [
                "Fix indentation consistency (use 4 spaces)",
                "Check for mixed tabs and spaces",
                "Verify proper block structure"
            ]
        }
