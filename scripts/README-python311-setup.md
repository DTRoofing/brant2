# Python 3.11 Environment Setup Scripts

This directory contains comprehensive scripts to set up Python 3.11 as your primary Python environment, including downloading, installing, and configuring Python 3.11.

## Scripts Available

### 1. Windows Batch Script (`setup-python311-environment.bat`)
- **Platform**: Windows Command Prompt
- **Usage**: Double-click or run from command prompt
- **Features**:
  - Downloads and installs Python 3.11
  - Configures Python 3.11 as primary Python
  - Updates environment variables
  - Creates virtual environment
  - Installs essential packages

### 2. PowerShell Script (`setup-python311-environment.ps1`)
- **Platform**: Windows PowerShell
- **Usage**: `.\setup-python311-environment.ps1 [options]`
- **Options**:
  - `-Force`: Force installation even if Python 3.11 exists
  - `-Verbose`: Show detailed output
- **Features**:
  - More robust installation and configuration
  - Better error handling and logging
  - Registry updates for system-wide changes
  - Comprehensive package management

### 3. Shell Script (`setup-python311-environment.sh`)
- **Platform**: Linux/macOS/Git Bash
- **Usage**: `./setup-python311-environment.sh [options]`
- **Options**:
  - `--force`: Force installation even if Python 3.11 exists
  - `--verbose`: Show detailed output
  - `--help`: Show help information
- **Features**:
  - Cross-platform compatibility
  - Package manager integration (apt, yum, dnf, brew)
  - Shell profile updates
  - Comprehensive environment configuration

## What These Scripts Do

### 1. System Analysis
- **Check Existing Python**: Identifies current Python installations
- **Version Detection**: Finds Python 3.11, 3.13, and other versions
- **Path Analysis**: Examines PATH and environment variables

### 2. Python 3.11 Installation
- **Download**: Downloads Python 3.11 installer from python.org
- **Install**: Installs Python 3.11 with proper configuration
- **Package Manager**: Uses system package managers (Linux/macOS)
- **Silent Installation**: Automated installation process

### 3. Environment Configuration
- **Primary Python**: Sets Python 3.11 as the default Python
- **Environment Variables**: Updates PYTHON_HOME, PYTHON_EXECUTABLE
- **PATH Updates**: Prioritizes Python 3.11 in PATH
- **Cleanup**: Removes Python 3.13 paths from PATH

### 4. Package Management
- **pip Upgrade**: Updates pip to latest version
- **Essential Packages**: Installs setuptools, wheel
- **Project Dependencies**: Installs from requirements.txt if present
- **Virtual Environment**: Creates Python 3.11 virtual environment

### 5. Verification
- **Version Check**: Verifies Python 3.11 is working
- **Package Check**: Confirms pip and essential packages
- **Environment Check**: Runs comprehensive verification
- **Summary Report**: Provides detailed setup summary

## Usage Examples

### Windows (Command Prompt)
```cmd
# Run the setup script
scripts\setup-python311-environment.bat
```

### Windows (PowerShell)
```powershell
# Run with verbose output
.\scripts\setup-python311-environment.ps1 -Verbose

# Force installation even if Python 3.11 exists
.\scripts\setup-python311-environment.ps1 -Force

# Run basic setup
.\scripts\setup-python311-environment.ps1
```

### Linux/macOS/Git Bash
```bash
# Make executable (if needed)
chmod +x scripts/setup-python311-environment.sh

# Run with verbose output
./scripts/setup-python311-environment.sh --verbose

# Force installation even if Python 3.11 exists
./scripts/setup-python311-environment.sh --force

# Run basic setup
./scripts/setup-python311-environment.sh
```

## Prerequisites

### Windows
- **Administrator Rights**: Required for system-wide installation
- **Internet Connection**: For downloading Python 3.11
- **PowerShell**: Recommended for best experience

### Linux
- **Package Manager**: apt, yum, dnf, or similar
- **sudo Access**: Required for package installation
- **Internet Connection**: For package downloads

### macOS
- **Homebrew**: Recommended for easy installation
- **Xcode Command Line Tools**: May be required
- **Internet Connection**: For package downloads

## Installation Process

### 1. Pre-Installation Checks
```
[SETUP] Checking current Python installations...
[INFO] Found existing Python installations:
  - C:\Python313\python.exe
    Version: Python 3.13 ✗
  - C:\Python311\python.exe
    Version: Python 3.11 ✓
```

### 2. Python 3.11 Installation
```
[SETUP] Python 3.11 not found. Downloading and installing...
[SETUP] Downloading Python 3.11 installer...
[SUCCESS] Download completed
[SETUP] Installing Python 3.11...
[SUCCESS] Python 3.11 installation completed
```

### 3. Environment Configuration
```
[SETUP] Configuring Python 3.11 as primary Python...
[INFO] Found Python 3.11 at: C:\Python311\python.exe
[INFO] Set PYTHON_HOME to: C:\Python311
[INFO] Set PYTHON_EXECUTABLE to: C:\Python311\python.exe
[SETUP] Updating PATH to prioritize Python 3.11...
[ADDED] Python 3.11 paths to PATH
[INFO] Updated system PATH
```

### 4. Package Installation
```
[SETUP] Installing essential Python packages...
[INFO] Upgrading pip...
[SUCCESS] pip upgraded
[INFO] Installing essential packages...
[SUCCESS] Essential packages installed
[INFO] Installing project dependencies from requirements.txt...
[SUCCESS] Project dependencies installed
```

### 5. Virtual Environment Creation
```
[SETUP] Creating Python 3.11 virtual environment...
[SUCCESS] Created virtual environment: venv
```

### 6. Final Verification
```
[SETUP] Final verification...
[SUCCESS] Python command working: Python 3.11.9
[SUCCESS] pip working: pip 24.0 from C:\Python311\Lib\site-packages\pip
[SUCCESS] All Python environment variables point to Python 3.11 ✓
```

## Post-Installation

### 1. Restart Terminal
- **Windows**: Close and reopen Command Prompt or PowerShell
- **Linux/macOS**: Run `source ~/.bashrc` or restart terminal
- **Git Bash**: Close and reopen Git Bash

### 2. Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. Verify Installation
```bash
# Check Python version
python --version

# Check pip version
pip --version

# Run verification script
scripts\verify-python311-env.bat
```

## Troubleshooting

### Common Issues

#### Installation Fails
- **Check Permissions**: Ensure you have administrator/sudo rights
- **Check Internet**: Verify internet connection for downloads
- **Check Disk Space**: Ensure sufficient disk space
- **Check Antivirus**: Temporarily disable antivirus if needed

#### Python Not Found After Installation
- **Restart Terminal**: Close and reopen terminal
- **Check PATH**: Verify Python 3.11 is in PATH
- **Check Environment**: Run verification script
- **Manual PATH**: Add Python 3.11 to PATH manually

#### Package Installation Fails
- **Check pip**: Ensure pip is working
- **Check Network**: Verify internet connection
- **Check Permissions**: Ensure write permissions
- **Check Dependencies**: Install missing system dependencies

#### Virtual Environment Issues
- **Check Python**: Ensure Python 3.11 is working
- **Check Permissions**: Ensure write permissions
- **Check Path**: Verify virtual environment path
- **Recreate**: Delete and recreate virtual environment

### Getting Help

1. **Check Logs**: Look for error messages in script output
2. **Use Verbose Mode**: Run with verbose output for details
3. **Check Prerequisites**: Verify all requirements are met
4. **Manual Installation**: Install Python 3.11 manually if needed

## Integration with Other Scripts

### With Verification Scripts
```bash
# Setup Python 3.11 environment
./scripts/setup-python311-environment.sh

# Verify the setup
./scripts/verify-python311-env.sh
```

### With Removal Scripts
```bash
# Remove Python 3.13 paths first
./scripts/remove-python313-paths.sh

# Setup Python 3.11 environment
./scripts/setup-python311-environment.sh
```

### With Project Setup
```bash
# Setup Python 3.11 environment
./scripts/setup-python311-environment.sh

# Activate virtual environment
source venv/bin/activate

# Install project dependencies
pip install -r requirements.txt

# Start the project
docker-compose up
```

## Best Practices

### 1. Always Verify Before Setup
```bash
# Check current Python environment
./scripts/verify-python311-env.sh

# Setup Python 3.11 if needed
./scripts/setup-python311-environment.sh
```

### 2. Use Virtual Environments
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install packages in virtual environment
pip install -r requirements.txt
```

### 3. Regular Maintenance
```bash
# Update pip regularly
python -m pip install --upgrade pip

# Update packages
pip install --upgrade -r requirements.txt

# Verify environment
./scripts/verify-python311-env.sh
```

### 4. Backup Configuration
- **Environment Variables**: Document current settings
- **PATH**: Keep backup of PATH before changes
- **Virtual Environments**: Backup virtual environment if needed

## Advanced Configuration

### Custom Python Installation
```bash
# Install Python 3.11 in custom location
./scripts/setup-python311-environment.sh --force

# Set custom PYTHON_HOME
export PYTHON_HOME="/custom/path/python3.11"

# Update PATH
export PATH="/custom/path/python3.11/bin:$PATH"
```

### Multiple Python Versions
```bash
# Use pyenv for multiple Python versions
curl https://pyenv.run | bash

# Install Python 3.11
pyenv install 3.11.9

# Set global Python version
pyenv global 3.11.9
```

### Docker Integration
```dockerfile
# Use Python 3.11 in Docker
FROM python:3.11-slim

# Copy setup scripts
COPY scripts/ /scripts/

# Run setup script
RUN /scripts/setup-python311-environment.sh
```

## Support

If you encounter issues with these scripts:

1. **Check Documentation**: Read this README thoroughly
2. **Check Prerequisites**: Ensure all requirements are met
3. **Use Verbose Mode**: Run with verbose output for details
4. **Check Logs**: Look for error messages in script output
5. **Manual Installation**: Install Python 3.11 manually if needed
6. **Community Support**: Ask for help in relevant forums

## License

These scripts are provided as-is for setting up Python 3.11 environments. Use at your own risk and always test in safe environments before applying to production systems.


