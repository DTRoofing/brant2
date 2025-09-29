# Python 3.11 Environment Verification Scripts

This directory contains scripts to verify that all Python-related environment variables point to Python 3.11 installations and not Python 3.13 or other versions.

## Scripts Available

### 1. Windows Batch Script (`verify-python311-env.bat`)
- **Platform**: Windows Command Prompt
- **Usage**: Double-click or run from command prompt
- **Features**:
  - Checks all Python executables in PATH
  - Verifies Python-related environment variables
  - Checks virtual environments and Conda environments
  - Provides detailed summary with color-coded results

### 2. PowerShell Script (`verify-python311-env.ps1`)
- **Platform**: Windows PowerShell
- **Usage**: `.\verify-python311-env.ps1 [options]`
- **Options**:
  - `-Verbose`: Show detailed output
- **Features**:
  - More robust Python version detection
  - Better error handling and logging
  - Comprehensive environment variable checking
  - Cross-session environment verification

### 3. Shell Script (`verify-python311-env.sh`)
- **Platform**: Linux/macOS/Git Bash
- **Usage**: `./verify-python311-env.sh [options]`
- **Options**:
  - `--verbose`: Show detailed output
  - `--help`: Show help information
- **Features**:
  - Cross-platform compatibility
  - Color-coded output
  - Comprehensive Python version detection
  - Virtual environment and Conda support

## What These Scripts Check

### Python Executables
- **python**: Checks all `python` commands in PATH
- **python3**: Checks all `python3` commands in PATH
- **Version Detection**: Identifies Python 3.11, 3.13, and other versions
- **Path Analysis**: Shows full paths to Python executables

### Environment Variables
- **PYTHONPATH**: Checks for Python 3.11 and 3.13 library paths
- **PYTHON_HOME**: Verifies points to Python 3.11 installation
- **PYTHON_ROOT**: Verifies points to Python 3.11 installation
- **PYTHON_INSTALL_DIR**: Verifies points to Python 3.11 installation
- **PYTHON_EXECUTABLE**: Verifies points to Python 3.11 executable

### Virtual Environments
- **VIRTUAL_ENV**: Checks active virtual environment Python version
- **CONDA_DEFAULT_ENV**: Checks active Conda environment
- **Version Verification**: Ensures virtual environments use Python 3.11

### PATH Analysis
- **Python 3.11 Paths**: Counts and lists Python 3.11 paths in PATH
- **Python 3.13 Paths**: Counts and lists Python 3.13 paths in PATH
- **Other Python Paths**: Counts and lists other Python version paths

## Usage Examples

### Windows (Command Prompt)
```cmd
# Run the batch script
scripts\verify-python311-env.bat
```

### Windows (PowerShell)
```powershell
# Run with verbose output
.\scripts\verify-python311-env.ps1 -Verbose

# Run basic verification
.\scripts\verify-python311-env.ps1
```

### Linux/macOS/Git Bash
```bash
# Make executable (if needed)
chmod +x scripts/verify-python311-env.sh

# Run with verbose output
./scripts/verify-python311-env.sh --verbose

# Run basic verification
./scripts/verify-python311-env.sh
```

## Expected Output

### Success Case
```
[VERIFY] Starting Python 3.11 environment verification...
[VERIFY] Checking Python executables in PATH...
[INFO] Found 'python' command:
  - C:\Python311\python.exe
    Version: Python 3.11 ✓
[VERIFY] Checking Python-related environment variables...
[INFO] PYTHONPATH is set:
  C:\Python311\Lib;C:\Python311\Lib\site-packages
  Contains Python 3.11 paths ✓
  No Python 3.13 paths found ✓
[VERIFY] Verification Summary:
[RESULT] Python 3.11 executables found ✓
[RESULT] No Python 3.13 executables found ✓
[RESULT] No other Python versions found ✓
[SUCCESS] All Python environment variables point to Python 3.11 ✓
```

### Warning Case
```
[VERIFY] Starting Python 3.11 environment verification...
[VERIFY] Checking Python executables in PATH...
[INFO] Found 'python' command:
  - C:\Python311\python.exe
    Version: Python 3.11 ✓
  - C:\Python310\python.exe
    Version: Python 3.10 ⚠
[VERIFY] Verification Summary:
[RESULT] Python 3.11 executables found ✓
[RESULT] No Python 3.13 executables found ✓
[RESULT] Other Python versions found ⚠
[WARNING] Python 3.11 found but other Python versions also present ⚠
```

### Error Case
```
[VERIFY] Starting Python 3.11 environment verification...
[VERIFY] Checking Python executables in PATH...
[INFO] Found 'python' command:
  - C:\Python313\python.exe
    Version: Python 3.13 ✗
[VERIFY] Verification Summary:
[RESULT] Python 3.11 executables NOT found ✗
[RESULT] Python 3.13 executables found ✗
[ERROR] Python 3.13 found in environment ✗
```

## Troubleshooting

### If Python 3.11 Is Not Found
1. **Check Installation**: Verify Python 3.11 is installed
2. **Check PATH**: Ensure Python 3.11 is in PATH
3. **Check Environment**: Run the verification script in the same environment where you work
4. **Check Virtual Environment**: Activate the correct virtual environment

### If Python 3.13 Is Found
1. **Remove Python 3.13**: Use the removal scripts in this directory
2. **Update PATH**: Remove Python 3.13 paths from PATH
3. **Check Environment Variables**: Clear Python 3.13 related environment variables
4. **Restart Terminal**: Restart your terminal after making changes

### If Other Python Versions Are Found
1. **Check if Acceptable**: Some projects may require multiple Python versions
2. **Use Virtual Environments**: Isolate different Python versions in virtual environments
3. **Update PATH Order**: Ensure Python 3.11 comes first in PATH
4. **Check IDE Settings**: Verify your IDE is using the correct Python version

## Integration with Other Scripts

### With Python 3.13 Removal Scripts
```bash
# First, remove Python 3.13 paths
./scripts/remove-python313-paths.sh

# Then, verify Python 3.11 environment
./scripts/verify-python311-env.sh
```

### With Project Setup
```bash
# Verify Python 3.11 environment before starting project
./scripts/verify-python311-env.sh

# If verification passes, start the project
docker-compose up
```

## Color Coding

- **Green (✓)**: Python 3.11 found, correct configuration
- **Red (✗)**: Python 3.13 found, incorrect configuration
- **Yellow (⚠)**: Other Python versions found, warning
- **Cyan**: Informational messages
- **Gray**: Detailed output and paths

## Exit Codes

The scripts use the following exit codes:
- **0**: Success - All Python environment variables point to Python 3.11
- **1**: Warning - Python 3.11 found but other versions also present
- **2**: Error - Python 3.11 not found or Python 3.13 found

## Best Practices

1. **Run Before Development**: Always verify Python environment before starting development
2. **Use Virtual Environments**: Isolate Python versions in virtual environments
3. **Regular Verification**: Run verification scripts regularly to catch environment drift
4. **Document Dependencies**: Keep track of required Python versions for your project
5. **Automate Checks**: Integrate verification into CI/CD pipelines

## Common Issues

### PATH Order Problems
- **Issue**: Python 3.13 comes before Python 3.11 in PATH
- **Solution**: Reorder PATH or use virtual environments

### Virtual Environment Issues
- **Issue**: Virtual environment uses wrong Python version
- **Solution**: Recreate virtual environment with correct Python version

### IDE Configuration
- **Issue**: IDE uses wrong Python interpreter
- **Solution**: Update IDE settings to use Python 3.11

### Conda Environment Issues
- **Issue**: Conda environment uses wrong Python version
- **Solution**: Create new Conda environment with Python 3.11

## Support

If you encounter issues with these scripts:
1. Check the verbose output for detailed information
2. Verify your Python installation
3. Check environment variable settings
4. Ensure you have the necessary permissions
5. Try running the scripts as administrator (Windows) or with sudo (Linux/macOS)


