# Automated Build Fixer

An intelligent system that automatically detects, analyzes, and fixes build errors in your Google Cloud Build pipeline.

## 🚀 Features

- **Automatic Error Detection**: Identifies common build errors including:
  - Poppler/PDF processing errors
  - Import/module errors
  - IAM permission issues
  - Test failures
  - Docker build errors
  - Syntax and indentation errors

- **Intelligent Fix Generation**: Creates targeted fix plans based on error analysis
- **Automated Application**: Applies fixes automatically and commits changes
- **Iterative Process**: Continues until build succeeds or max iterations reached
- **Comprehensive Logging**: Detailed logs for debugging and monitoring

## 📁 Files

- `smart_build_fixer.py` - Main intelligent build fixer
- `build_error_analyzer.py` - Advanced error pattern analysis
- `automated_build_fixer.py` - Basic build fixer (legacy)
- `run_automated_fixer.sh` - Easy-to-use wrapper script

## 🛠️ Setup

### Prerequisites

1. **Google Cloud SDK**: Install and authenticate
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Python 3**: Ensure Python 3 is installed
   ```bash
   python3 --version
   ```

3. **Git**: Ensure git is configured
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

### Installation

1. **Clone the repository** (if not already done)
   ```bash
   git clone <your-repo-url>
   cd brant
   ```

2. **Make the script executable**
   ```bash
   chmod +x run_automated_fixer.sh
   ```

3. **Update project configuration**
   ```bash
   # Edit run_automated_fixer.sh and update PROJECT_ID
   PROJECT_ID="your-project-id"
   ```

## 🚀 Usage

### Quick Start

```bash
# Run the automated fixer
./run_automated_fixer.sh
```

### Manual Usage

```bash
# Run with specific project and region
python3 smart_build_fixer.py your-project-id us-central1
```

### Advanced Usage

```bash
# Run the basic fixer
python3 automated_build_fixer.py your-project-id us-central1

# Run the error analyzer separately
python3 build_error_analyzer.py
```

## 🔧 How It Works

### 1. Error Detection
The system monitors build logs and identifies errors using regex patterns:

- **Poppler Errors**: `PDFInfoNotInstalledError`, `pdfinfo not found`
- **Import Errors**: `ModuleNotFoundError`, `AttributeError`
- **Permission Errors**: `DENIED.*Permission.*artifactregistry`
- **Test Failures**: `FAILED.*test.*`, `ERROR.*test.*`
- **Docker Errors**: `ERROR.*build step.*failed`

### 2. Fix Generation
For each error type, the system generates targeted fixes:

- **Poppler Fixes**: Updates Dockerfiles with poppler-utils installation
- **Import Fixes**: Creates missing modules, updates import paths
- **IAM Fixes**: Adds required permissions for Cloud Build
- **Test Fixes**: Updates test fixtures and compatibility modules

### 3. Fix Application
The system applies fixes automatically:

- Modifies Dockerfiles and Python files
- Runs gcloud commands for IAM permissions
- Creates missing files and directories
- Updates import statements and module exports

### 4. Iterative Process
The process repeats until:
- Build succeeds ✅
- Maximum iterations reached (15)
- Build timeout exceeded (40 minutes)

## 📊 Error Types and Fixes

### Poppler/PDF Processing Errors
**Detection**: `PDFInfoNotInstalledError`, `pdfinfo not found`
**Fixes**:
- Add poppler-utils to Dockerfiles
- Set POPPLER_PATH environment variable
- Update Python code to use poppler_path parameter
- Verify installation with test commands

### Import/Module Errors
**Detection**: `ModuleNotFoundError`, `AttributeError`
**Fixes**:
- Create missing `__init__.py` files
- Update import paths
- Create compatibility modules
- Fix module exports

### IAM Permission Errors
**Detection**: `DENIED.*Permission.*artifactregistry`
**Fixes**:
- Add `roles/artifactregistry.writer` to Cloud Build service account
- Add `roles/cloudbuild.builds.builder` to Cloud Build service account
- Verify service account permissions

### Test Failures
**Detection**: `FAILED.*test.*`, `ERROR.*test.*`
**Fixes**:
- Update test imports
- Create missing test fixtures
- Fix test data and assertions
- Update compatibility modules

## 📝 Configuration

### Environment Variables
```bash
export PROJECT_ID="your-project-id"
export REGION="us-central1"
export MAX_ITERATIONS=15
export BUILD_TIMEOUT=2400
```

### Custom Error Patterns
Edit `build_error_analyzer.py` to add custom error patterns:

```python
ErrorPattern(
    name="custom_error",
    pattern=r"Your custom regex pattern",
    severity="error",
    fix_type="custom_fix",
    fix_template="custom_fix_template",
    confidence=0.8
)
```

## 📋 Monitoring and Logs

### Log Files
- `smart_build_fixer.log` - Main application logs
- `build_fixer.log` - Basic fixer logs (if used)

### Log Levels
- **INFO**: General progress and status updates
- **WARNING**: Non-critical issues and fallbacks
- **ERROR**: Critical failures and errors
- **DEBUG**: Detailed debugging information

### Monitoring Build Status
```bash
# Check recent builds
gcloud builds list --limit=10

# Get specific build details
gcloud builds describe BUILD_ID --region=us-central1

# View build logs
gcloud builds log BUILD_ID --region=us-central1
```

## 🚨 Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

2. **Permission Denied**
   ```bash
   # Check IAM permissions
   gcloud projects get-iam-policy your-project-id
   ```

3. **Python Import Errors**
   ```bash
   # Install required packages
   pip3 install --user subprocess-mock
   ```

4. **Git Push Failures**
   ```bash
   # Check git configuration
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

### Manual Fixes

If the automated fixer fails, you can apply fixes manually:

1. **Poppler Issues**:
   ```bash
   # Add to Dockerfiles
   RUN apt-get update && apt-get install -y poppler-utils
   ENV POPPLER_PATH=/usr/bin
   ENV PATH="/usr/bin:${PATH}"
   ```

2. **IAM Permissions**:
   ```bash
   gcloud projects add-iam-policy-binding $PROJECT_ID \
     --member="serviceAccount:$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')@cloudbuild.gserviceaccount.com" \
     --role="roles/artifactregistry.writer"
   ```

3. **Missing Modules**:
   ```bash
   # Create missing __init__.py files
   touch app/module/__init__.py
   ```

## 🔄 Continuous Integration

### GitHub Actions Integration
```yaml
name: Auto Fix Build Errors
on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  auto-fix:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: google-github-actions/setup-gcloud@v0
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: ${{ secrets.GCP_PROJECT_ID }}
      - name: Run Automated Fixer
        run: ./run_automated_fixer.sh
```

### Cron Job
```bash
# Add to crontab for daily runs
0 2 * * * cd /path/to/project && ./run_automated_fixer.sh
```

## 📈 Performance

### Typical Performance
- **Error Detection**: < 1 second
- **Fix Generation**: 1-5 seconds
- **Fix Application**: 10-30 seconds
- **Build Time**: 5-15 minutes
- **Total Cycle**: 10-20 minutes per iteration

### Optimization Tips
1. **Use specific error patterns** to reduce false positives
2. **Set appropriate timeouts** based on your build complexity
3. **Monitor logs** to identify recurring issues
4. **Update fix strategies** based on your specific error patterns

## 🤝 Contributing

### Adding New Error Patterns
1. Edit `build_error_analyzer.py`
2. Add new `ErrorPattern` with regex and fix template
3. Implement fix logic in `smart_build_fixer.py`
4. Test with sample error logs

### Adding New Fix Types
1. Create fix method in `SmartBuildFixer` class
2. Add fix type to `apply_fix_plan` method
3. Update error patterns to use new fix type
4. Test with real build errors

## 📄 License

This project is part of the Brant Roofing System and follows the same license terms.

## 🆘 Support

For issues and questions:
1. Check the logs for detailed error information
2. Review the troubleshooting section
3. Check Google Cloud Build documentation
4. Create an issue in the project repository
