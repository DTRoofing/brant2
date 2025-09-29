# All Scripts Overview

This directory contains comprehensive scripts for managing Python environment variables and ensuring proper Python 3.11 configuration.

## Script Categories

### 1. Python 3.13 Removal Scripts
Remove Python 3.13 paths from environment variables to prevent conflicts.

#### Files:
- `remove-python313-paths.bat` - Windows batch script
- `remove-python313-paths.ps1` - PowerShell script
- `remove-python313-paths.sh` - Cross-platform shell script
- `test-python313-removal.bat` - Test script for removal functionality

#### Features:
- Removes Python 3.13 paths from PATH and PYTHONPATH
- Clears Python 3.13 related environment variables
- Creates backup files before making changes
- Supports what-if mode for safe testing
- Cross-platform compatibility

### 2. Python 3.11 Verification Scripts
Verify that all Python environment variables point to Python 3.11 installations.

#### Files:
- `verify-python311-env.bat` - Windows batch script
- `verify-python311-env.ps1` - PowerShell script
- `verify-python311-env.sh` - Cross-platform shell script
- `test-python311-verification.bat` - Test script for verification functionality

#### Features:
- Checks all Python executables in PATH
- Verifies Python-related environment variables
- Checks virtual environments and Conda environments
- Provides detailed summary with color-coded results
- Comprehensive error detection and reporting

### 3. Documentation
Comprehensive documentation for all scripts.

#### Files:
- `README-python313-removal.md` - Documentation for Python 3.13 removal
- `README-python311-verification.md` - Documentation for Python 3.11 verification
- `README-all-scripts.md` - This overview file

## Quick Start Guide

### 1. Verify Current Python Environment
```bash
# Windows (Command Prompt)
scripts\verify-python311-env.bat

# Windows (PowerShell)
.\scripts\verify-python311-env.ps1

# Linux/macOS/Git Bash
./scripts/verify-python311-env.sh
```

### 2. Remove Python 3.13 Paths (if needed)
```bash
# Windows (Command Prompt)
scripts\remove-python313-paths.bat

# Windows (PowerShell)
.\scripts\remove-python313-paths.ps1

# Linux/macOS/Git Bash
./scripts/remove-python313-paths.sh
```

### 3. Verify Python 3.11 Environment Again
```bash
# Run the verification script again to confirm changes
scripts\verify-python311-env.bat
```

## Script Features Comparison

| Feature | Batch Scripts | PowerShell Scripts | Shell Scripts |
|---------|---------------|-------------------|---------------|
| **Platform** | Windows CMD | Windows PowerShell | Linux/macOS/Git Bash |
| **Color Output** | Basic | Full | Full |
| **Error Handling** | Basic | Advanced | Advanced |
| **What-If Mode** | No | Yes | Yes |
| **Verbose Output** | No | Yes | Yes |
| **Backup Creation** | Yes | Yes | Yes |
| **Cross-Platform** | No | No | Yes |

## Common Use Cases

### 1. Development Environment Setup
```bash
# Verify Python 3.11 environment before starting development
./scripts/verify-python311-env.sh

# If Python 3.13 is found, remove it
./scripts/remove-python313-paths.sh

# Verify again
./scripts/verify-python311-env.sh
```

### 2. CI/CD Pipeline Integration
```bash
# Add to your CI/CD pipeline to ensure correct Python version
./scripts/verify-python311-env.sh
if [ $? -ne 0 ]; then
    echo "Python 3.11 environment verification failed"
    exit 1
fi
```

### 3. Troubleshooting Python Issues
```bash
# Check what Python versions are in your environment
./scripts/verify-python311-env.sh --verbose

# Remove conflicting Python 3.13 paths
./scripts/remove-python313-paths.sh --what-if
./scripts/remove-python313-paths.sh
```

### 4. Team Environment Standardization
```bash
# Ensure all team members have Python 3.11 environment
./scripts/verify-python311-env.sh
./scripts/remove-python313-paths.sh
```

## Testing

### Run Test Scripts
```bash
# Test Python 3.13 removal functionality
scripts\test-python313-removal.bat

# Test Python 3.11 verification functionality
scripts\test-python311-verification.bat
```

### Manual Testing
1. Set up different Python environment scenarios
2. Run the appropriate verification script
3. Verify the output matches expected results
4. Test the removal scripts if needed

## Best Practices

### 1. Always Verify Before Making Changes
```bash
# Check current state first
./scripts/verify-python311-env.sh

# Use what-if mode for removal scripts
./scripts/remove-python313-paths.sh --what-if
```

### 2. Create Backups
- All removal scripts create automatic backups
- Keep backup files for potential restoration
- Document your environment before making changes

### 3. Test in Safe Environment
- Use virtual machines or containers for testing
- Test scripts before running on production systems
- Verify changes don't break existing functionality

### 4. Regular Verification
- Run verification scripts regularly
- Integrate into development workflow
- Monitor for environment drift

## Troubleshooting

### Common Issues

#### Scripts Not Found
- Ensure you're in the correct directory
- Check file permissions
- Verify script files exist

#### Permission Denied
- Run as administrator (Windows)
- Use sudo (Linux/macOS)
- Check file permissions

#### Environment Variables Not Persisting
- Restart terminal after running scripts
- Check if scripts are updating correct profile files
- Verify environment variable syntax

#### Python Versions Not Detected
- Check if Python is in PATH
- Verify Python installation
- Run scripts in the same environment where you work

### Getting Help

1. **Check Documentation**: Read the specific README files for each script
2. **Use Verbose Mode**: Run scripts with verbose output for detailed information
3. **Test Scripts**: Use the test scripts to verify functionality
4. **Check Logs**: Look for error messages and warnings in script output

## Integration Examples

### Docker Integration
```dockerfile
# Add to Dockerfile
COPY scripts/ /scripts/
RUN chmod +x /scripts/*.sh
RUN /scripts/verify-python311-env.sh
```

### GitHub Actions
```yaml
# Add to GitHub Actions workflow
- name: Verify Python 3.11 Environment
  run: ./scripts/verify-python311-env.sh
```

### Makefile Integration
```makefile
# Add to Makefile
verify-python:
	./scripts/verify-python311-env.sh

clean-python313:
	./scripts/remove-python313-paths.sh
```

## Contributing

When adding new scripts or modifying existing ones:

1. **Follow Naming Conventions**: Use descriptive names with platform suffixes
2. **Add Documentation**: Create README files for new script categories
3. **Include Tests**: Add test scripts for new functionality
4. **Cross-Platform**: Consider creating versions for all platforms
5. **Error Handling**: Include comprehensive error handling and logging
6. **Backup Support**: Always create backups before making changes

## License

These scripts are provided as-is for managing Python environment variables. Use at your own risk and always test in safe environments before applying to production systems.


