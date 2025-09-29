# Python 3.13 Path Removal Scripts

This directory contains scripts to remove Python 3.13 paths from environment variables to prevent conflicts with other Python versions.

## Scripts Available

### 1. Windows Batch Script (`remove-python313-paths.bat`)
- **Platform**: Windows Command Prompt
- **Usage**: Double-click or run from command prompt
- **Features**:
  - Removes Python 3.13 paths from PATH and PYTHONPATH
  - Creates backup files before making changes
  - Shows detailed progress and verification
  - Updates environment variables for current session

### 2. PowerShell Script (`remove-python313-paths.ps1`)
- **Platform**: Windows PowerShell
- **Usage**: `.\remove-python313-paths.ps1 [options]`
- **Options**:
  - `-WhatIf`: Show what would be changed without making changes
  - `-Verbose`: Show detailed output
- **Features**:
  - More robust path detection and removal
  - Permanent environment variable updates
  - Better error handling and logging
  - Cross-session persistence

### 3. Shell Script (`remove-python313-paths.sh`)
- **Platform**: Linux/macOS/Git Bash
- **Usage**: `./remove-python313-paths.sh [options]`
- **Options**:
  - `--what-if`: Show what would be changed without making changes
  - `--verbose`: Show detailed output
  - `--help`: Show help information
- **Features**:
  - Updates shell profile files (.bashrc, .zshrc, etc.)
  - Cross-platform compatibility
  - Color-coded output
  - Comprehensive Python version detection

## What These Scripts Do

### Environment Variables Cleaned
- **PATH**: Removes directories containing Python 3.13 installations
- **PYTHONPATH**: Removes Python 3.13 library paths
- **PYTHON_HOME**: Clears if pointing to Python 3.13
- **PYTHON_ROOT**: Clears if pointing to Python 3.13
- **PYTHON_INSTALL_DIR**: Clears if pointing to Python 3.13
- **PYTHON_EXECUTABLE**: Clears if pointing to Python 3.13

### Safety Features
- **Backup Creation**: Creates timestamped backup files before making changes
- **Verification**: Checks for remaining Python 3.13 paths after cleanup
- **What-If Mode**: Shows what would be changed without making changes
- **Detailed Logging**: Shows exactly what paths are being removed

## Usage Examples

### Windows (Command Prompt)
```cmd
# Run the batch script
scripts\remove-python313-paths.bat
```

### Windows (PowerShell)
```powershell
# Run with what-if mode first
.\scripts\remove-python313-paths.ps1 -WhatIf

# Run with verbose output
.\scripts\remove-python313-paths.ps1 -Verbose

# Apply changes
.\scripts\remove-python313-paths.ps1
```

### Linux/macOS/Git Bash
```bash
# Make executable (if needed)
chmod +x scripts/remove-python313-paths.sh

# Run with what-if mode first
./scripts/remove-python313-paths.sh --what-if

# Run with verbose output
./scripts/remove-python313-paths.sh --verbose

# Apply changes
./scripts/remove-python313-paths.sh
```

## Before Running

### Check Current Python Installations
```bash
# Check what Python versions are in PATH
where python
python --version

where python3
python3 --version

# Check PYTHONPATH
echo $PYTHONPATH
```

### Identify Python 3.13 Paths
```bash
# Look for Python 3.13 in PATH
echo $PATH | grep -i "python.*3\.13"

# Look for Python 3.13 in PYTHONPATH
echo $PYTHONPATH | grep -i "python.*3\.13"
```

## After Running

### Verify Changes
```bash
# Check that Python 3.13 paths are gone
echo $PATH | grep -i "python.*3\.13"
echo $PYTHONPATH | grep -i "python.*3\.13"

# Check remaining Python installations
where python
python --version
```

### Restart Terminal
- **Windows**: Close and reopen Command Prompt or PowerShell
- **Linux/macOS**: Run `source ~/.bashrc` or restart terminal
- **Git Bash**: Close and reopen Git Bash

## Troubleshooting

### If Python 3.13 Paths Still Exist
1. Check if they're in system-wide environment variables
2. Look for Python 3.13 in other shell profiles
3. Check if they're set in IDE or editor configurations
4. Verify the scripts ran successfully

### If Other Python Versions Are Affected
1. Check the backup files created by the scripts
2. Restore from backup if necessary
3. Run the scripts with `--what-if` or `-WhatIf` first

### If Environment Variables Are Not Persisting
1. Check if you have write permissions to shell profile files
2. Verify the scripts are updating the correct profile files
3. Try running as administrator (Windows) or with sudo (Linux/macOS)

## Backup Files

The scripts create backup files with timestamps:
- `env_backup_YYYYMMDD_HHMMSS_PATH.txt` - Backup of PATH
- `env_backup_YYYYMMDD_HHMMSS_PYTHONPATH.txt` - Backup of PYTHONPATH

These can be used to restore the original environment if needed.

## Why Remove Python 3.13 Paths?

Python 3.13 paths can cause conflicts when:
- Using virtual environments with different Python versions
- Running applications that expect specific Python versions
- Having multiple Python installations on the same system
- Using package managers that depend on specific Python versions

## Safety Notes

- Always run with `--what-if` or `-WhatIf` first to see what will be changed
- The scripts only remove paths containing "python.*3\.13" - they won't affect other Python versions
- Backup files are created automatically before making changes
- Changes are reversible by restoring from backup files

