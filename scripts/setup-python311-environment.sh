#!/bin/bash
# ===================================================================
# SETUP PYTHON 3.11 ENVIRONMENT
# ===================================================================
# This shell script helps you set up Python 3.11 as your primary 
# Python environment by downloading, installing, and configuring Python 3.11.

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Default values
FORCE=false
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --force)
            FORCE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--force] [--verbose]"
            echo "  --force     Force installation even if Python 3.11 exists"
            echo "  --verbose   Show detailed output"
            echo "  -h, --help  Show this help message"
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
    echo -e "${GREEN}[SETUP]${NC} $1"
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

log_info "Starting Python 3.11 environment setup..."

# ===================================================================
# CHECK CURRENT PYTHON INSTALLATIONS
# ===================================================================
log_info "Checking current Python installations..."

Python311Found=false
Python313Found=false
OtherPythonFound=false

# Check for existing Python installations
if command -v python >/dev/null 2>&1; then
    echo -e "${CYAN}[INFO]${NC} Found existing Python installations:"
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
    echo -e "${CYAN}[INFO]${NC} No existing Python installations found"
fi

# ===================================================================
# DETECT OPERATING SYSTEM
# ===================================================================
log_info "Detecting operating system..."

OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OS="windows"
fi

log_info "Detected OS: $OS"

# ===================================================================
# DOWNLOAD AND INSTALL PYTHON 3.11
# ===================================================================
if [ "$Python311Found" = false ] || [ "$FORCE" = true ]; then
    log_info "Python 3.11 not found or force mode enabled. Installing Python 3.11..."
    
    case $OS in
        "linux")
            log_info "Installing Python 3.11 on Linux..."
            
            # Check if we have package manager
            if command -v apt-get >/dev/null 2>&1; then
                # Ubuntu/Debian
                log_info "Using apt-get to install Python 3.11..."
                sudo apt-get update
                sudo apt-get install -y software-properties-common
                sudo add-apt-repository -y ppa:deadsnakes/ppa
                sudo apt-get update
                sudo apt-get install -y python3.11 python3.11-venv python3.11-pip
                sudo apt-get install -y python3.11-dev python3.11-distutils
                
                # Create symlinks
                sudo ln -sf /usr/bin/python3.11 /usr/bin/python
                sudo ln -sf /usr/bin/python3.11 /usr/bin/python3
                
            elif command -v yum >/dev/null 2>&1; then
                # CentOS/RHEL
                log_info "Using yum to install Python 3.11..."
                sudo yum install -y python3.11 python3.11-pip python3.11-venv
                sudo yum install -y python3.11-devel
                
                # Create symlinks
                sudo ln -sf /usr/bin/python3.11 /usr/bin/python
                sudo ln -sf /usr/bin/python3.11 /usr/bin/python3
                
            elif command -v dnf >/dev/null 2>&1; then
                # Fedora
                log_info "Using dnf to install Python 3.11..."
                sudo dnf install -y python3.11 python3.11-pip python3.11-venv
                sudo dnf install -y python3.11-devel
                
                # Create symlinks
                sudo ln -sf /usr/bin/python3.11 /usr/bin/python
                sudo ln -sf /usr/bin/python3.11 /usr/bin/python3
                
            else
                log_error "Unsupported Linux distribution. Please install Python 3.11 manually."
                exit 1
            fi
            ;;
            
        "macos")
            log_info "Installing Python 3.11 on macOS..."
            
            # Check if Homebrew is installed
            if command -v brew >/dev/null 2>&1; then
                log_info "Using Homebrew to install Python 3.11..."
                brew install python@3.11
                
                # Add to PATH
                echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
                echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.bash_profile
                
            else
                log_error "Homebrew not found. Please install Homebrew first or install Python 3.11 manually."
                exit 1
            fi
            ;;
            
        "windows")
            log_info "Installing Python 3.11 on Windows..."
            log_error "Windows installation not supported in this shell script."
            log_info "Please use the PowerShell script: .\scripts\setup-python311-environment.ps1"
            exit 1
            ;;
            
        *)
            log_error "Unsupported operating system: $OS"
            exit 1
            ;;
    esac
    
    log_success "Python 3.11 installation completed"
else
    log_success "Python 3.11 already installed ✓"
fi

# ===================================================================
# CONFIGURE PYTHON 3.11 AS PRIMARY
# ===================================================================
log_info "Configuring Python 3.11 as primary Python..."

# Find Python 3.11 installation
Python311Path=$(which python 2>/dev/null | grep -v "python3.13" | head -1)
if [ -z "$Python311Path" ]; then
    Python311Path=$(which python3 2>/dev/null | grep -v "python3.13" | head -1)
fi

if [ -n "$Python311Path" ]; then
    log_info "Found Python 3.11 at: $Python311Path"
    
    # Get the directory containing python
    Python311Dir=$(dirname "$Python311Path")
    Python311Scripts="$Python311Dir"
    
    log_info "Python 3.11 directory: $Python311Dir"
    
    # Update environment variables
    log_info "Updating environment variables..."
    
    # Set PYTHON_HOME
    export PYTHON_HOME="$Python311Dir"
    echo "export PYTHON_HOME=\"$Python311Dir\"" >> ~/.bashrc
    echo "export PYTHON_HOME=\"$Python311Dir\"" >> ~/.zshrc
    log_info "Set PYTHON_HOME to: $Python311Dir"
    
    # Set PYTHON_EXECUTABLE
    export PYTHON_EXECUTABLE="$Python311Path"
    echo "export PYTHON_EXECUTABLE=\"$Python311Path\"" >> ~/.bashrc
    echo "export PYTHON_EXECUTABLE=\"$Python311Path\"" >> ~/.zshrc
    log_info "Set PYTHON_EXECUTABLE to: $Python311Path"
    
    # Update PATH to prioritize Python 3.11
    log_info "Updating PATH to prioritize Python 3.11..."
    
    # Remove Python 3.13 paths from PATH
    NewPath=""
    IFS=':' read -ra PATH_ARRAY <<< "$PATH"
    for PathItem in "${PATH_ARRAY[@]}"; do
        if ! echo "$PathItem" | grep -qi "python.*3\.13"; then
            if [ -n "$NewPath" ]; then
                NewPath="$NewPath:$PathItem"
            else
                NewPath="$PathItem"
            fi
        else
            log_warning "Removed Python 3.13 path: $PathItem"
        fi
    done
    
    # Add Python 3.11 paths to the beginning of PATH
    if ! echo "$NewPath" | grep -qi "$Python311Dir"; then
        NewPath="$Python311Dir:$NewPath"
        log_info "Added Python 3.11 paths to PATH"
    else
        log_info "Python 3.11 paths already in PATH"
    fi
    
    # Update PATH
    export PATH="$NewPath"
    echo "export PATH=\"$NewPath\"" >> ~/.bashrc
    echo "export PATH=\"$NewPath\"" >> ~/.zshrc
    log_info "Updated PATH"
    
else
    log_error "Could not find Python 3.11 installation"
    log_info "Please ensure Python 3.11 is installed and in PATH"
    exit 1
fi

# ===================================================================
# VERIFY PYTHON 3.11 SETUP
# ===================================================================
log_info "Verifying Python 3.11 setup..."

# Check Python version
if command -v python >/dev/null 2>&1; then
    PythonVersion=$(python --version 2>/dev/null)
    log_success "Python command working: $PythonVersion"
else
    log_warning "Python command not working in current session"
fi

# Check Python3 version
if command -v python3 >/dev/null 2>&1; then
    Python3Version=$(python3 --version 2>/dev/null)
    log_success "Python3 command working: $Python3Version"
else
    log_warning "Python3 command not working in current session"
fi

# Check pip
if command -v pip >/dev/null 2>&1; then
    PipVersion=$(pip --version 2>/dev/null)
    log_success "pip working: $PipVersion"
else
    log_warning "pip not working in current session"
fi

# ===================================================================
# INSTALL ESSENTIAL PACKAGES
# ===================================================================
log_info "Installing essential Python packages..."

# Upgrade pip
log_info "Upgrading pip..."
if command -v python >/dev/null 2>&1; then
    python -m pip install --upgrade pip
    log_success "pip upgraded"
else
    log_warning "Cannot upgrade pip - Python not found"
fi

# Install essential packages
log_info "Installing essential packages..."
if command -v python >/dev/null 2>&1; then
    python -m pip install setuptools wheel
    log_success "Essential packages installed"
else
    log_warning "Cannot install essential packages - Python not found"
fi

# Install project dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    log_info "Installing project dependencies from requirements.txt..."
    if command -v python >/dev/null 2>&1; then
        python -m pip install -r requirements.txt
        log_success "Project dependencies installed"
    else
        log_warning "Cannot install project dependencies - Python not found"
    fi
else
    log_info "No requirements.txt found, skipping project dependencies"
fi

# ===================================================================
# CREATE VIRTUAL ENVIRONMENT
# ===================================================================
log_info "Creating Python 3.11 virtual environment..."

if [ ! -d "venv" ]; then
    if command -v python >/dev/null 2>&1; then
        python -m venv venv
        log_success "Created virtual environment: venv"
    else
        log_warning "Cannot create virtual environment - Python not found"
    fi
else
    log_info "Virtual environment already exists: venv"
fi

# ===================================================================
# FINAL VERIFICATION
# ===================================================================
log_info "Final verification..."

# Run the verification script
VerificationScript="$(dirname "$0")/verify-python311-env.sh"
if [ -f "$VerificationScript" ]; then
    log_info "Running Python 3.11 verification..."
    bash "$VerificationScript"
else
    log_warning "Verification script not found"
fi

# ===================================================================
# SUMMARY
# ===================================================================
log_success "Python 3.11 environment setup completed!"
echo ""
echo -e "${CYAN}[SUMMARY]${NC} What was done:"
echo -e "${GRAY}  - Checked for existing Python installations${NC}"
echo -e "${GRAY}  - Installed Python 3.11 (if needed)${NC}"
echo -e "${GRAY}  - Configured Python 3.11 as primary Python${NC}"
echo -e "${GRAY}  - Updated environment variables (PYTHON_HOME, PYTHON_EXECUTABLE)${NC}"
echo -e "${GRAY}  - Updated PATH to prioritize Python 3.11${NC}"
echo -e "${GRAY}  - Removed Python 3.13 paths from PATH${NC}"
echo -e "${GRAY}  - Installed essential Python packages${NC}"
echo -e "${GRAY}  - Created virtual environment${NC}"
echo -e "${GRAY}  - Verified the setup${NC}"
echo ""
log_warning "You may need to restart your terminal or run 'source ~/.bashrc' for all changes to take effect."
log_info "To activate the virtual environment, run: source venv/bin/activate"
log_info "To verify the setup, run: ./scripts/verify-python311-env.sh"
echo ""


