#!/usr/bin/env python3
"""
Comprehensive Import Validation Script
Tests all imports in the application systematically.
"""
import ast
import importlib
import sys
import os
from pathlib import Path
from typing import List, Dict, Set, Tuple

class ImportValidator:
    def __init__(self, app_dir: str = "app"):
        self.app_dir = Path(app_dir)
        self.import_errors = []
        self.missing_modules = set()
        self.circular_dependencies = set()
        
    def find_python_files(self) -> List[Path]:
        """Find all Python files in the app directory."""
        return list(self.app_dir.rglob("*.py"))
    
    def extract_imports(self, file_path: Path) -> List[Tuple[str, str, int]]:
        """Extract all import statements from a Python file."""
        imports = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append((alias.name, "import", node.lineno))
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append((f"{module}.{alias.name}", "from", node.lineno))
        except Exception as e:
            self.import_errors.append(f"Error parsing {file_path}: {e}")
        
        return imports
    
    def test_import(self, module_name: str, file_path: Path, line_num: int) -> bool:
        """Test if an import can be resolved."""
        try:
            # Handle relative imports
            if module_name.startswith('app.'):
                # Add the app directory to the path
                sys.path.insert(0, str(self.app_dir.parent))
                
            # Try to import the module
            importlib.import_module(module_name)
            return True
        except ImportError as e:
            self.missing_modules.add(module_name)
            self.import_errors.append(f"ImportError in {file_path}:{line_num} - {module_name}: {e}")
            return False
        except Exception as e:
            self.import_errors.append(f"Error importing {module_name} in {file_path}:{line_num}: {e}")
            return False
        finally:
            # Clean up sys.path
            if str(self.app_dir.parent) in sys.path:
                sys.path.remove(str(self.app_dir.parent))
    
    def validate_all_imports(self) -> Dict[str, any]:
        """Validate all imports in the application."""
        print("🔍 Scanning Python files...")
        python_files = self.find_python_files()
        print(f"Found {len(python_files)} Python files")
        
        total_imports = 0
        failed_imports = 0
        
        for file_path in python_files:
            print(f"📁 Checking {file_path.relative_to(self.app_dir.parent)}")
            imports = self.extract_imports(file_path)
            
            for module_name, import_type, line_num in imports:
                total_imports += 1
                if not self.test_import(module_name, file_path, line_num):
                    failed_imports += 1
        
        return {
            "total_files": len(python_files),
            "total_imports": total_imports,
            "failed_imports": failed_imports,
            "success_rate": (total_imports - failed_imports) / total_imports * 100 if total_imports > 0 else 0,
            "missing_modules": list(self.missing_modules),
            "errors": self.import_errors
        }
    
    def generate_report(self, results: Dict[str, any]) -> str:
        """Generate a comprehensive report."""
        report = []
        report.append("=" * 80)
        report.append("COMPREHENSIVE IMPORT VALIDATION REPORT")
        report.append("=" * 80)
        report.append(f"Total Python files: {results['total_files']}")
        report.append(f"Total imports tested: {results['total_imports']}")
        report.append(f"Failed imports: {results['failed_imports']}")
        report.append(f"Success rate: {results['success_rate']:.2f}%")
        report.append("")
        
        if results['missing_modules']:
            report.append("MISSING MODULES:")
            report.append("-" * 40)
            for module in sorted(results['missing_modules']):
                report.append(f"  ❌ {module}")
            report.append("")
        
        if results['errors']:
            report.append("DETAILED ERRORS:")
            report.append("-" * 40)
            for error in results['errors'][:20]:  # Show first 20 errors
                report.append(f"  {error}")
            if len(results['errors']) > 20:
                report.append(f"  ... and {len(results['errors']) - 20} more errors")
        
        return "\n".join(report)

def main():
    """Main function to run the import validation."""
    print("🚀 Starting Comprehensive Import Validation...")
    
    validator = ImportValidator()
    results = validator.validate_all_imports()
    
    report = validator.generate_report(results)
    print("\n" + report)
    
    # Save report to file
    with open("import_validation_report.txt", "w") as f:
        f.write(report)
    
    print(f"\n📄 Full report saved to: import_validation_report.txt")
    
    # Return exit code based on results
    if results['failed_imports'] > 0:
        print(f"\n❌ Validation failed with {results['failed_imports']} import errors")
        return 1
    else:
        print(f"\n✅ All imports validated successfully!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
