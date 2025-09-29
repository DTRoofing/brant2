#!/bin/bash
# ===================================================================
# REMOVE PYTHON 3.13 PATHS FROM ENVIRONMENT VARIABLES
# ===================================================================
# This shell script removes Python 3.13 paths from PATH and other 
# environment variables to prevent conflicts with other Python versions.

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Default values
WHAT_IF=false
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --what-if)
            WHAT_IF=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--what-if] [--verbose]"
            echo "  --what-if    Show what would be changed without making changes"
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
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_removed() {
    echo -e "${RED}[REMOVED]${NC} $1"
}

log_verbose() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${GRAY}[VERBOSE]${NC} $1"
    fi
}

log_info "Starting Python 3.13 path removal process..."

# ===================================================================
# BACKUP CURRENT ENVIRONMENT
# ===================================================================
log_info "Creating backup of current environment variables..."

BACKUP_DATE=$(date +"%Y%m%d_%H%M%S")
log_info "Backup timestamp: $BACKUP_DATE"

# Backup PATH
echo "$PATH" > "env_backup_${BACKUP_DATE}_PATH.txt"
log_info "PATH backed up to: env_backup_${BACKUP_DATE}_PATH.txt"

# Backup PYTHONPATH if it exists
if [ -n "$PYTHONPATH" ]; then
    echo "$PYTHONPATH" > "env_backup_${BACKUP_DATE}_PYTHONPATH.txt"
    log_info "PYTHONPATH backed up to: env_backup_${BACKUP_DATE}_PYTHONPATH.txt"
fi

# ===================================================================
# REMOVE PYTHON 3.13 PATHS FROM PATH
# ===================================================================
log_info "Removing Python 3.13 paths from PATH..."

# Create temporary file for cleaned PATH
TEMP_PATH_FILE=$(mktemp)

# Process each path in PATH
IFS=':' read -ra PATH_ARRAY <<< "$PATH"
for path_item in "${PATH_ARRAY[@]}"; do
    # Check if the path contains Python 3.13 references
    if echo "$path_item" | grep -qi "python.*3\.13"; then
        log_removed "Python 3.13 path: $path_item"
    else
        echo "$path_item" >> "$TEMP_PATH_FILE"
        log_verbose "Kept: $path_item"
    fi
done

# Rebuild PATH from cleaned paths
NEW_PATH=$(cat "$TEMP_PATH_FILE" | tr '\n' ':' | sed 's/:$//')
rm "$TEMP_PATH_FILE"

# ===================================================================
# REMOVE PYTHON 3.13 PATHS FROM PYTHONPATH
# ===================================================================
NEW_PYTHONPATH=""
if [ -n "$PYTHONPATH" ]; then
    log_info "Removing Python 3.13 paths from PYTHONPATH..."
    
    # Create temporary file for cleaned PYTHONPATH
    TEMP_PYTHONPATH_FILE=$(mktemp)
    
    IFS=':' read -ra PYTHONPATH_ARRAY <<< "$PYTHONPATH"
    for path_item in "${PYTHONPATH_ARRAY[@]}"; do
        if echo "$path_item" | grep -qi "python.*3\.13"; then
            log_removed "Python 3.13 PYTHONPATH: $path_item"
        else
            echo "$path_item" >> "$TEMP_PYTHONPATH_FILE"
            log_verbose "Kept PYTHONPATH: $path_item"
        fi
    done
    
    # Rebuild PYTHONPATH from cleaned paths
    NEW_PYTHONPATH=$(cat "$TEMP_PYTHONPATH_FILE" | tr '\n' ':' | sed 's/:$//')
    rm "$TEMP_PYTHONPATH_FILE"
fi

# ===================================================================
# REMOVE OTHER PYTHON 3.13 RELATED ENVIRONMENT VARIABLES
# ===================================================================
log_info "Checking for other Python 3.13 related environment variables..."

PYTHON_ENV_VARS=("PYTHON_HOME" "PYTHON_ROOT" "PYTHON_INSTALL_DIR" "PYTHON_EXECUTABLE")

for env_var in "${PYTHON_ENV_VARS[@]}"; do
    value=$(eval echo \$$env_var)
    if [ -n "$value" ] && echo "$value" | grep -qi "python.*3\.13"; then
        log_removed "Python 3.13 environment variable $env_var: $value"
        if [ "$WHAT_IF" = false ]; then
            unset "$env_var"
        fi
    fi
done

# ===================================================================
# APPLY CHANGES
# ===================================================================
if [ "$WHAT_IF" = true ]; then
    log_warning "WHAT-IF mode: Would apply the following changes:"
    echo -e "${CYAN}  - New PATH length: ${#NEW_PATH} characters${NC}"
    if [ -n "$NEW_PYTHONPATH" ]; then
        echo -e "${CYAN}  - New PYTHONPATH length: ${#NEW_PYTHONPATH} characters${NC}"
    fi
    log_warning "Use without --what-if to apply changes"
else
    log_info "Applying cleaned environment variables..."
    
    # Update PATH for current session
    export PATH="$NEW_PATH"
    
    # Update PYTHONPATH for current session if it was modified
    if [ -n "$NEW_PYTHONPATH" ]; then
        export PYTHONPATH="$NEW_PYTHONPATH"
    fi
    
    # Update shell profile files
    SHELL_PROFILES=("$HOME/.bashrc" "$HOME/.bash_profile" "$HOME/.zshrc" "$HOME/.profile")
    
    for profile in "${SHELL_PROFILES[@]}"; do
        if [ -f "$profile" ]; then
            log_verbose "Updating shell profile: $profile"
            # Add export statements if they don't exist
            if ! grep -q "export PATH=" "$profile"; then
                echo "export PATH=\"$NEW_PATH\"" >> "$profile"
            else
                # Replace existing PATH export
                sed -i.bak "s|export PATH=.*|export PATH=\"$NEW_PATH\"|g" "$profile"
            fi
            
            if [ -n "$NEW_PYTHONPATH" ]; then
                if ! grep -q "export PYTHONPATH=" "$profile"; then
                    echo "export PYTHONPATH=\"$NEW_PYTHONPATH\"" >> "$profile"
                else
                    # Replace existing PYTHONPATH export
                    sed -i.bak "s|export PYTHONPATH=.*|export PYTHONPATH=\"$NEW_PYTHONPATH\"|g" "$profile"
                fi
            fi
        fi
    done
fi

# ===================================================================
# VERIFY CHANGES
# ===================================================================
log_info "Verifying changes..."

# Check if any Python 3.13 paths remain in PATH
if echo "$PATH" | grep -qi "python.*3\.13"; then
    log_warning "Some Python 3.13 paths may still exist in PATH:"
    echo "$PATH" | grep -i "python.*3\.13" | while read -r line; do
        echo -e "${RED}  - $line${NC}"
    done
else
    log_success "No Python 3.13 paths found in PATH"
fi

# Check if any Python 3.13 paths remain in PYTHONPATH
if [ -n "$PYTHONPATH" ] && echo "$PYTHONPATH" | grep -qi "python.*3\.13"; then
    log_warning "Some Python 3.13 paths may still exist in PYTHONPATH:"
    echo "$PYTHONPATH" | grep -i "python.*3\.13" | while read -r line; do
        echo -e "${RED}  - $line${NC}"
    done
else
    log_success "No Python 3.13 paths found in PYTHONPATH"
fi

# ===================================================================
# DISPLAY CURRENT PYTHON VERSIONS
# ===================================================================
log_info "Current Python installations in PATH:"

PYTHON_COMMANDS=("python" "python3")
for cmd in "${PYTHON_COMMANDS[@]}"; do
    if command -v "$cmd" >/dev/null 2>&1; then
        python_path=$(command -v "$cmd")
        echo -e "${CYAN}  - $python_path${NC}"
        version=$($cmd --version 2>/dev/null || echo "Unable to determine")
        echo -e "${GRAY}    Version: $version${NC}"
    fi
done

if ! command -v python >/dev/null 2>&1 && ! command -v python3 >/dev/null 2>&1; then
    echo -e "${GRAY}  - No Python found in PATH${NC}"
fi

# ===================================================================
# SUMMARY
# ===================================================================
echo ""
log_success "Python 3.13 path removal completed"
log_info "Backup files created with timestamp: $BACKUP_DATE"
log_info "Current PATH length: ${#PATH} characters"
if [ -n "$PYTHONPATH" ]; then
    log_info "Current PYTHONPATH length: ${#PYTHONPATH} characters"
fi
echo ""
log_info "Changes have been applied to current session and shell profiles"
log_info "You may need to restart your terminal or run 'source ~/.bashrc' for changes to take effect"
echo ""

