import os
import re
import sys
import sys

def find_outdated_paths(docs_dir, project_root):
    """
    Scans markdown files in docs_dir for potentially outdated file paths.
    """
    outdated_paths_found = []

    # Regex to find potential file paths. This is a broad match and might need refinement.
    # It looks for:
    # 1. Paths in markdown links/images: [text](path) or ![alt](path)
    # 2. Paths in code blocks or shell commands (e.g., cp path/to/file)
    # 3. Python import paths (e.g., from app.services.module)
    # 4. Hardcoded URLs like localhost
    # 5. Specific file names like google-credentials.json
    path_patterns = [
        re.compile(r'\[[^\]]*\]\(([^)]+)\)'),  # Markdown links/images
        re.compile(r'(?:cp|mv|rm|ls|cd|python -c "from)\s+([a-zA-Z0-9_./-]+)'), # Shell commands with paths
        re.compile(r'from\s+([a-zA-Z0-9_.]+)\s+import'), # Python imports
        re.compile(r'http://localhost:3001'), # Hardcoded localhost
        re.compile(r'google-credentials\.json'), # Specific problematic file
        re.compile(r'file_path\s*=\s*["\'](.*?)["\']'), # Python variable assignments
        re.compile(r'path:\s*([a-zA-Z0-9_./-]+)'), # YAML-like path definitions
        re.compile(r'file:\s*([a-zA-Z0-9_./-]+)'), # YAML-like file definitions
        re.compile(r'image:\s*([a-zA-Z0-9_./-]+)'), # Docker image paths
        re.compile(r'src:\s*([a-zA-Z0-9_./-]+)'), # Script src paths
        re.compile(r'gs://([a-zA-Z0-9_./-]+)'), # Google Cloud Storage paths
        re.compile(r'docker-compose\.([a-zA-Z0-9_.]+)\.yml'), # Docker Compose file names
        re.compile(r'k8s/([a-zA-Z0-9_./-]+)\.yaml'), # Kubernetes YAML files
        re.compile(r'monitoring/([a-zA-Z0-9_./-]+)\.yml'), # Monitoring YAML files
        re.compile(r'\.github/workflows/([a-zA-Z0-9_./-]+)\.yml'), # GitHub Actions workflow files
        re.compile(r'app/core/config\.py'), # Specific config file
        re.compile(r'app/core/database\.py'), # Specific database file
        re.compile(r'app/workers/tasks/new_pdf_processing\.py'), # Specific worker file
        re.compile(r'app/alembic/'), # Alembic directory
        re.compile(r'frontend_ux/next\.config\.mjs'), # Frontend config
        re.compile(r'frontend_ux/app/api/proxy/\[\.\.\.path\]/route\.ts'), # Frontend proxy
        re.compile(r'frontend_ux/\.env\.local'), # Frontend env file
        re.compile(r'app/api/v1/endpoints/claude_process\.py'), # Claude process file
        re.compile(r'app/api/v1/endpoints/claude_processing\.py'), # Claude processing file (potential duplicate)
        re.compile(r'app/api/v1/endpoints/document_repository\.py'), # Document repository (potential unused)
        re.compile(r'app/api/v1/endpoints/processing_result_repository\.py'), # Processing result repository (potential unused)
        re.compile(r'app/models/document_old\.py'), # Old document model
        re.compile(r'docker-compose\.yml'), # Docker Compose main file
        re.compile(r'backend\.Dockerfile'), # Backend Dockerfile
        re.compile(r'worker\.Dockerfile'), # Worker Dockerfile
        re.compile(r'package\.json'), # Package.json
        re.compile(r'app/workers/celery_app'), # Celery app reference
        re.compile(r'app/services/google_services'), # Old Google services path
        re.compile(r'app/integrations/gcp_services'), # New Google services path
        re.compile(r'app/core/database'), # Database core module
    ]

    # Specific patterns for known outdated paths from previous analysis
    known_outdated_patterns = {
        re.compile(r'app\.services\.google_services'): "Consider 'app.integrations.gcp_services' based on reorganization.",
        re.compile(r'http://localhost:3001'): "Hardcoded localhost URL. Should be an environment variable.",
        re.compile(r'google-credentials\.json'): "This file is git-ignored and should not be copied directly in Dockerfiles. Use secrets management.",
        re.compile(r'app/api/v1/endpoints/claude_processing\.py'): "Potential duplicate/unused file. Check if 'claude_process.py' is the correct one.",
        re.compile(r'app/api/v1/endpoints/document_repository\.py'): "Potential unused file. Verify if it's still needed.",
        re.compile(r'app/api/v1/endpoints/processing_result_repository\.py'): "Potential unused file. Verify if it's still needed.",
        re.compile(r'app/models/document_old\.py'): "Old document model. Ensure it's not referenced and can be removed.",
        re.compile(r'frontend_ux/next\.config\.mjs.*ignoreBuildErrors:\s*false'): "Frontend build errors are ignored in development, but this is set to false. Consider setting to true for development or fixing errors.",
        re.compile(r'frontend_ux/app/api/proxy/\[\.\.\.path\]/route\.ts.*http://localhost:3001'): "Hardcoded frontend API proxy URL. Must use environment variables for production.",
        re.compile(r'app/alembic/'): "Alembic directory appears empty or improperly initialized. Database migrations might be missing.",
        re.compile(r'http://localhost:3001/api/v1/pipeline/health'): "Health endpoint '/api/v1/pipeline/health' appears to be missing or not implemented.",
    }

    # List of common placeholder values to ignore for existence checks
    placeholders = {
        "your-bucket-name", "your-project-id", "your-processor-id", "your-api-key",
        "your-jwt-token", "your-email@gmail.com", "your-app-password", "your-password",
        "brant-roofing:latest", "brant-roofing:__IMAGE_TAG__", "celery-task-uuid",
        "req-uuid-123", "claude-analysis-uuid", "user@example.com", "recipient@example.com",
        "test@example.com", "<base64-encoded-database-url>", "<base64-encoded-secret-key>",
        "<base64-encoded-api-key>", "your-secret-key-here", "backup.sql"
    }

    findings = []

    for root, _, files in os.walk(docs_dir):
        for file in files:
            if not file.endswith('.md'):
                continue

            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        is_known_issue = False
                        # Check for known problematic patterns first
                        for pattern, suggestion in known_outdated_patterns.items():
                            if pattern.search(line):
                                findings.append({
                                    "file": file_path,
                                    "line_num": line_num,
                                    "line": line.strip(),
                                    "issue": "Known outdated pattern found",
                                    "suggestion": suggestion
                                })
                                is_known_issue = True
                                break # Found one, stop checking for other known issues
                        
                        if is_known_issue:
                            continue # Go to next line in file

                        # Check for general file paths that might not exist
                        for pattern in path_patterns:
                            for match in pattern.finditer(line):
                                # Extract the first non-None group, which is usually the path
                                path_str = next((g for g in match.groups() if g is not None), None)

                                if not path_str:
                                    continue

                                path_str = path_str.strip('\'"()[] ')
                                # Ignore placeholders, URLs, and empty strings
                                if not path_str or path_str in placeholders or path_str.startswith(('http:', 'https:', 'mailto:', 'gs:')):
                                    continue

                                # Heuristic to convert python module to path
                                is_python_module = '.' in path_str and not os.path.sep in path_str and not path_str.endswith(('.yml', '.yaml', '.json', '.mjs', '.ts'))
                                check_str = path_str.replace('.', os.path.sep) if is_python_module else path_str

                                # Check for file/dir existence relative to project root
                                full_path = os.path.join(project_root, check_str)
                                py_file_path = os.path.join(project_root, check_str + '.py')

                                if not (os.path.exists(full_path) or (is_python_module and os.path.exists(py_file_path))):
                                    findings.append({
                                        "file": file_path,
                                        "line_num": line_num,
                                        "line": line.strip(),
                                        "issue": f"Path or resource may not exist: '{path_str}'",
                                        "suggestion": "Verify the path is correct relative to the project root."
                                    })
            except Exception as e:
                print(f"Error reading file {file_path}: {e}", file=sys.stderr)

    return findings

def main():
    # Assumes the script is run from its location in `docs/sharepoint`
    try:
        script_dir = os.path.dirname(__file__)
        project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
        docs_dir = os.path.join(project_root, 'docs', 'sharepoint')
    except NameError:
        # Handle case where __file__ is not defined (e.g., interactive interpreter)
        project_root = os.path.abspath(os.path.join(os.getcwd()))
        docs_dir = os.path.join(project_root, 'docs', 'sharepoint')


    print(f"Scanning for outdated paths in: {docs_dir}")
    print(f"Using project root: {project_root}\n")

    if not os.path.isdir(docs_dir):
        print(f"Error: Documentation directory not found at '{docs_dir}'", file=sys.stderr)
        sys.exit(1)

    results = find_outdated_paths(docs_dir, project_root)

    if not results:
        print("✅ No outdated paths or known issues found in documentation.")
        return

    # Deduplicate and print results
    unique_results = {}
    for res in results:
        key = (res['file'], res['line_num'], res['issue'])
        if key not in unique_results:
            unique_results[key] = res

    print(f"🚨 Found {len(unique_results)} potential issues:\n")

    for file_path in sorted({res['file'] for res in unique_results.values()}):
        print(f"--- {os.path.relpath(file_path, project_root)} ---")
        file_issues = [res for res in unique_results.values() if res['file'] == file_path]
        for issue in sorted(file_issues, key=lambda x: x['line_num']):
            print(f"  L{issue['line_num']}: {issue['issue']}")
            print(f"     Line: `{issue['line']}`")
            print(f"     Suggestion: {issue['suggestion']}")
        print("")

if __name__ == "__main__":
    main()