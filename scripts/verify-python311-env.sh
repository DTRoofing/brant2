#!/bin/bash
# ===================================================================
# VERIFY PYTHON 3.11 ENVIRONMENT VARIABLES
# ===================================================================
# This shell script verifies that all Python-related environment 
# variables point to Python 3.11 installations and not Python 3.13 or other versions.

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Default values
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--verbose]"
            echo "  --verbose    Show detailed output"
            echo "  -h, --help   Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

log_info() {
    echo -e "${GREEN}[VERIFY]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_verbose() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${GRAY}[VERBOSE]${NC} $1"
    fi
}

log_info "Starting Python 3.11 environment verification..."

# ===================================================================
# CHECK PYTHON EXECUTABLES IN PATH
# ===================================================================
log_info "Checking Python executables in PATH..."

PythonFound=false
Python311Found=false
Python313Found=false
OtherPythonFound=false

# Check for python command
if command -v python >/dev/null 2>&1; then
    PythonFound=true
    echo -e "${CYAN}[INFO]${NC} Found 'python' command:"
    for python_cmd in $(which -a python 2>/dev/null); do
        echo -e "${GRAY}  - $python_cmd${NC}"
        version=$($python_cmd --version 2>/dev/null || echo "Unable to determine")
        if echo "$version" | grep -qi "3\.11"; then
            echo -e "${GREEN}    Version: Python 3.11 ✓${NC}"
            Python311Found=true
        elif echo "$version" | grep -qi "3\.13"; then
            echo -e "${RED}    Version: Python 3.13 ✗${NC}"
            Python313Found=true
        else
            echo -e "${YELLOW}    Version: $version ⚠${NC}"
            OtherPythonFound=true
        fi
    done
else
    log_warning "No 'python' command found in PATH"
fi

# Check for python3 command
if command -v python3 >/dev/null 2>&1; then
    PythonFound=true
    echo -e "${CYAN}[INFO]${NC} Found 'python3' command:"
    for python3_cmd in $(which -a python3 2>/dev/null); do
        echo -e "${GRAY}  - $python3_cmd${NC}"
        version=$($python3_cmd --version 2>/dev/null || echo "Unable to determine")
        if echo "$version" | grep -qi "3\.11"; then
            echo -e "${GREEN}    Version: Python 3.11 ✓${NC}"
            Python311Found=true
        elif echo "$version" | grep -qi "3\.13"; then
            echo -e "${RED}    Version: Python 3.13 ✗${NC}"
            Python313Found=true
        else
            echo -e "${YELLOW}    Version: $version ⚠${NC}"
            OtherPythonFound=true
        fi
    done
else
    log_warning "No 'python3' command found in PATH"
fi

# ===================================================================
# CHECK PYTHON-RELATED ENVIRONMENT VARIABLES
# ===================================================================
log_info "Checking Python-related environment variables..."

# Check PYTHONPATH
if [ -n "$PYTHONPATH" ]; then
    echo -e "${CYAN}[INFO]${NC} PYTHONPATH is set:"
    echo -e "${GRAY}  $PYTHONPATH${NC}"
    
    if echo "$PYTHONPATH" | grep -qi "python.*3\.11"; then
        echo -e "${GREEN}  Contains Python 3.11 paths ✓${NC}"
    else
        echo -e "${YELLOW}  No Python 3.11 paths found ⚠${NC}"
    fi
    
    if echo "$PYTHONPATH" | grep -qi "python.*3\.13"; then
        echo -e "${RED}  Contains Python 3.13 paths ✗${NC}"
    else
        echo -e "${GREEN}  No Python 3.13 paths found ✓${NC}"
    fi
else
    echo -e "${CYAN}[INFO]${NC} PYTHONPATH is not set"
fi

# Check PYTHON_HOME
if [ -n "$PYTHON_HOME" ]; then
    echo -e "${CYAN}[INFO]${NC} PYTHON_HOME is set:"
    echo -e "${GRAY}  $PYTHON_HOME${NC}"
    
    if echo "$PYTHON_HOME" | grep -qi "python.*3\.11"; then
        echo -e "${GREEN}  Points to Python 3.11 ✓${NC}"
    elif echo "$PYTHON_HOME" | grep -qi "python.*3\.13"; then
        echo -e "${RED}  Points to Python 3.13 ✗${NC}"
    else
        echo -e "${YELLOW}  Points to other Python version ⚠${NC}"
    fi
else
    echo -e "${CYAN}[INFO]${NC} PYTHON_HOME is not set"
fi

# Check PYTHON_ROOT
if [ -n "$PYTHON_ROOT" ]; then
    echo -e "${CYAN}[INFO]${NC} PYTHON_ROOT is set:"
    echo -e "${GRAY}  $PYTHON_ROOT${NC}"
    
    if echo "$PYTHON_ROOT" | grep -qi "python.*3\.11"; then
        echo -e "${GREEN}  Points to Python 3.11 ✓${NC}"
    elif echo "$PYTHON_ROOT" | grep -qi "python.*3\.13"; then
        echo -e "${RED}  Points to Python 3.13 ✗${NC}"
    else
        echo -e "${YELLOW}  Points to other Python version ⚠${NC}"
    fi
else
    echo -e "${CYAN}[INFO]${NC} PYTHON_ROOT is not set"
fi

# Check PYTHON_INSTALL_DIR
if [ -n "$PYTHON_INSTALL_DIR" ]; then
    echo -e "${CYAN}[INFO]${NC} PYTHON_INSTALL_DIR is set:"
    echo -e "${GRAY}  $PYTHON_INSTALL_DIR${NC}"
    
    if echo "$PYTHON_INSTALL_DIR" | grep -qi "python.*3\.11"; then
        echo -e "${GREEN}  Points to Python 3.11 ✓${NC}"
    elif echo "$PYTHON_INSTALL_DIR" | grep -qi "python.*3\.13"; then
        echo -e "${RED}  Points to Python 3.13 ✗${NC}"
    else
        echo -e "${YELLOW}  Points to other Python version ⚠${NC}"
    fi
else
    echo -e "${CYAN}[INFO]${NC} PYTHON_INSTALL_DIR is not set"
fi

# Check PYTHON_EXECUTABLE
if [ -n "$PYTHON_EXECUTABLE" ]; then
    echo -e "${CYAN}[INFO]${NC} PYTHON_EXECUTABLE is set:"
    echo -e "${GRAY}  $PYTHON_EXECUTABLE${NC}"
    
    if echo "$PYTHON_EXECUTABLE" | grep -qi "python.*3\.11"; then
        echo -e "${GREEN}  Points to Python 3.11 ✓${NC}"
    elif echo "$PYTHON_EXECUTABLE" | grep -qi "python.*3\.13"; then
        echo -e "${RED}  Points to Python 3.13 ✗${NC}"
    else
        echo -e "${YELLOW}  Points to other Python version ⚠${NC}"
    fi
else
    echo -e "${CYAN}[INFO]${NC} PYTHON_EXECUTABLE is not set"
fi

# ===================================================================
# CHECK PATH FOR PYTHON INSTALLATIONS
# ===================================================================
log_info "Checking PATH for Python installations..."

Python311PathsFound=0
Python313PathsFound=0
OtherPythonPathsFound=0

# Check each path in PATH for Python installations
IFS=':' read -ra PATH_ARRAY <<< "$PATH"
for PathItem in "${PATH_ARRAY[@]}"; do
    if echo "$PathItem" | grep -qi "python.*3\.11"; then
        echo -e "${GREEN}[FOUND]${NC} Python 3.11 path: $PathItem ✓"
        ((Python311PathsFound++))
    elif echo "$PathItem" | grep -qi "python.*3\.13"; then
        echo -e "${RED}[FOUND]${NC} Python 3.13 path: $PathItem ✗"
        ((Python313PathsFound++))
    elif echo "$PathItem" | grep -qi "python"; then
        echo -e "${YELLOW}[FOUND]${NC} Other Python path: $PathItem ⚠"
        ((OtherPythonPathsFound++))
    fi
done

# ===================================================================
# CHECK VIRTUAL ENVIRONMENTS
# ===================================================================
log_info "Checking for virtual environments..."

# Check VIRTUAL_ENV
if [ -n "$VIRTUAL_ENV" ]; then
    echo -e "${CYAN}[INFO]${NC} VIRTUAL_ENV is set:"
    echo -e "${GRAY}  $VIRTUAL_ENV${NC}"
    
    # Check if the virtual environment uses Python 3.11
    if [ -f "$VIRTUAL_ENV/bin/python" ]; then
        version=$("$VIRTUAL_ENV/bin/python" --version 2>/dev/null || echo "Unable to determine")
        if echo "$version" | grep -qi "3\.11"; then
            echo -e "${GREEN}  Virtual environment uses Python 3.11 ✓${NC}"
        elif echo "$version" | grep -qi "3\.13"; then
            echo -e "${RED}  Virtual environment uses Python 3.13 ✗${NC}"
        else
            echo -e "${YELLOW}  Virtual environment uses $version ⚠${NC}"
        fi
    else
        echo -e "${YELLOW}  Cannot find python in virtual environment ⚠${NC}"
    fi
else
    echo -e "${CYAN}[INFO]${NC} VIRTUAL_ENV is not set (no active virtual environment)"
fi

# ===================================================================
# CHECK CONDA ENVIRONMENTS
# ===================================================================
log_info "Checking for Conda environments..."

if [ -n "$CONDA_DEFAULT_ENV" ]; then
    echo -e "${CYAN}[INFO]${NC} CONDA_DEFAULT_ENV is set:"
    echo -e "${GRAY}  $CONDA_DEFAULT_ENV${NC}"
    
    # Check if conda is available
    if command -v conda >/dev/null 2>&1; then
        echo -e "${GRAY}  Conda environments available:${NC}"
        conda info --envs 2>/dev/null | while read -r line; do
            echo -e "${GRAY}    $line${NC}"
        done
    else
        echo -e "${YELLOW}  Cannot determine Conda environments ⚠${NC}"
    fi
else
    echo -e "${CYAN}[INFO]${NC} CONDA_DEFAULT_ENV is not set (no active Conda environment)"
fi

# ===================================================================
# SUMMARY
# ===================================================================
echo -e "${GREEN}[VERIFY]${NC} Verification Summary:"
echo ""

if [ "$PythonFound" = true ]; then
    if [ "$Python311Found" = true ]; then
        echo -e "${GREEN}[RESULT]${NC} Python 3.11 executables found ✓"
    else
        echo -e "${RED}[RESULT]${NC} Python 3.11 executables NOT found ✗"
    fi
    
    if [ "$Python313Found" = true ]; then
        echo -e "${RED}[RESULT]${NC} Python 3.13 executables found ✗"
    else
        echo -e "${GREEN}[RESULT]${NC} No Python 3.13 executables found ✓"
    fi
    
    if [ "$OtherPythonFound" = true ]; then
        echo -e "${YELLOW}[RESULT]${NC} Other Python versions found ⚠"
    else
        echo -e "${GREEN}[RESULT]${NC} No other Python versions found ✓"
    fi
else
    echo -e "${RED}[RESULT]${NC} No Python executables found in PATH ✗"
fi

echo -e "${CYAN}[RESULT]${NC} Python 3.11 paths in PATH: $Python311PathsFound"
echo -e "${CYAN}[RESULT]${NC} Python 3.13 paths in PATH: $Python313PathsFound"
echo -e "${CYAN}[RESULT]${NC} Other Python paths in PATH: $OtherPythonPathsFound"

echo ""
if [ "$Python311Found" = true ]; then
    if [ "$Python313Found" = false ]; then
        if [ "$OtherPythonFound" = false ]; then
            log_success "All Python environment variables point to Python 3.11 ✓"
        else
            echo -e "${YELLOW}[WARNING]${NC} Python 3.11 found but other Python versions also present ⚠"
        fi
    else
        log_error "Python 3.13 found in environment ✗"
    fi
else
    log_error "Python 3.11 not found in environment ✗"
fi

echo ""
log_info "Verification completed."


