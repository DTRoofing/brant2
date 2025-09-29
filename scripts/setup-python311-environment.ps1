# ===================================================================
# SETUP PYTHON 3.11 ENVIRONMENT
# ===================================================================
# This PowerShell script helps you set up Python 3.11 as your primary 
# Python environment by downloading, installing, and configuring Python 3.11.

param(
    [switch]$Force = $false,
    [switch]$Verbose = $false
)

# Enable verbose output if requested
if ($Verbose) {
    $VerbosePreference = "Continue"
}

Write-Host '[SETUP] Starting Python 3.11 environment setup...' -ForegroundColor Green

# ===================================================================
# CHECK CURRENT PYTHON INSTALLATIONS
# ===================================================================
Write-Host '[SETUP] Checking current Python installations...' -ForegroundColor Yellow

$Python311Found = $false
$Python313Found = $false
$OtherPythonFound = $false

# Check for existing Python installations
try {
    $PythonCommands = Get-Command python -ErrorAction SilentlyContinue
    if ($PythonCommands) {
        Write-Host '[INFO] Found existing Python installations:' -ForegroundColor Cyan
        foreach ($cmd in $PythonCommands) {
            Write-Host "  - $($cmd.Source)" -ForegroundColor Gray
            try {
                $version = & $cmd.Source --version 2>$null
                if ($version -match "3\.11") {
                    Write-Host "    Version: Python 3.11 ✓" -ForegroundColor Green
                    $Python311Found = $true
                } elseif ($version -match "3\.13") {
                    Write-Host "    Version: Python 3.13 ✗" -ForegroundColor Red
                    $Python313Found = $true
                } else {
                    Write-Host "    Version: $version ⚠" -ForegroundColor Yellow
                    $OtherPythonFound = $true
                }
            } catch {
                Write-Host "    Version: Unable to determine ⚠" -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host '[INFO] No existing Python installations found' -ForegroundColor Cyan
    }
} catch {
    Write-Host '[ERROR] An unexpected error occurred while checking Python installations: ' + $($_.Exception.Message) -ForegroundColor Red
}

# ===================================================================
# DOWNLOAD AND INSTALL PYTHON 3.11
# ===================================================================
if (-not $Python311Found -or $Force) {
    Write-Host '[SETUP] Python 3.11 not found or force mode enabled. Downloading and installing...' -ForegroundColor Yellow
    
    # Create temporary directory for download
    $TempDir = Join-Path $env:TEMP "python311_setup"
    if (-not (Test-Path $TempDir)) {
        New-Item -ItemType Directory -Path $TempDir -Force | Out-Null
    }
    
    # Download Python 3.11 installer
    $InstallerPath = Join-Path $TempDir "python-3.11.9-amd64.exe"
    $DownloadUrl = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
    
    Write-Host '[SETUP] Downloading Python 3.11 installer...' -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Uri $DownloadUrl -OutFile $InstallerPath -UseBasicParsing
        Write-Host '[SUCCESS] Download completed' -ForegroundColor Green
    } catch {
        Write-Host '[ERROR] Failed to download Python 3.11 installer: ' + $($_.Exception.Message) -ForegroundColor Red
        Write-Host '[INFO] Please download Python 3.11 manually from https://www.python.org/downloads/' -ForegroundColor Yellow
        exit 1
    }
    
    if (Test-Path $InstallerPath) {
        Write-Host '[SETUP] Installing Python 3.11...' -ForegroundColor Yellow
        Write-Host '[INFO] This will install Python 3.11 with the following options:' -ForegroundColor Cyan
        Write-Host '  - Add Python to PATH' -ForegroundColor Gray
        Write-Host '  - Install for all users' -ForegroundColor Gray
        Write-Host '  - Install pip and other tools' -ForegroundColor Gray
        Write-Host ""
        
        # Run the installer silently
        $InstallArgs = @(
            "/quiet",
            "InstallAllUsers=1",
            "PrependPath=1",
            "Include_pip=1",
            "Include_test=0",
            "Include_doc=0",
            "Include_tcltk=1"
        )
        
        try {
            Start-Process -FilePath $InstallerPath -ArgumentList $InstallArgs -Wait
            Write-Host '[SUCCESS] Python 3.11 installation completed' -ForegroundColor Green
        } catch {
            Write-Host '[ERROR] Failed to install Python 3.11: ' + $($_.Exception.Message) -ForegroundColor Red
            exit 1
        }
        
        # Clean up
        Remove-Item $InstallerPath -Force
        Remove-Item $TempDir -Force
    } else {
        Write-Host '[ERROR] Installer file not found' -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host '[SETUP] Python 3.11 already installed ✓' -ForegroundColor Green
}

# ===================================================================
# CONFIGURE PYTHON 3.11 AS PRIMARY
# ===================================================================
Write-Host '[SETUP] Configuring Python 3.11 as primary Python...' -ForegroundColor Yellow

# Find Python 3.11 installation
$Python311Path = $null
try {
    $PythonCommands = Get-Command python -ErrorAction SilentlyContinue
    foreach ($cmd in $PythonCommands) {
        try {
            $version = & $cmd.Source --version 2>$null
            if ($version -match "3\.11") {
                $Python311Path = $cmd.Source
                break
            }
        } catch {
            # Continue to next command
        }
    }
} catch {
    Write-Host '[ERROR] Could not find Python 3.11 installation' -ForegroundColor Red
    exit 1
}

if ($Python311Path) {
    Write-Host '[INFO] Found Python 3.11 at: ' + $Python311Path -ForegroundColor Cyan
    
    # Get the directory containing python.exe
    $Python311Dir = Split-Path $Python311Path -Parent
    $Python311Scripts = Join-Path $Python311Dir "Scripts"
    $Python311Lib = Join-Path $Python311Dir "Lib"
    
    Write-Host '[INFO] Python 3.11 directory: ' + $Python311Dir -ForegroundColor Cyan
    
    # Update environment variables
    Write-Host '[SETUP] Updating environment variables...' -ForegroundColor Yellow
    
    # Set PYTHON_HOME
    [Environment]::SetEnvironmentVariable("PYTHON_HOME", $Python311Dir, "Machine")
    Write-Host '[INFO] Set PYTHON_HOME to: ' + $Python311Dir -ForegroundColor Cyan
    
    # Set PYTHON_EXECUTABLE
    [Environment]::SetEnvironmentVariable("PYTHON_EXECUTABLE", $Python311Path, "Machine")
    Write-Host '[INFO] Set PYTHON_EXECUTABLE to: ' + $Python311Path -ForegroundColor Cyan
    
    # Update PATH to prioritize Python 3.11
    Write-Host '[SETUP] Updating PATH to prioritize Python 3.11...' -ForegroundColor Yellow
    
    # Get current PATH
    $CurrentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
    
    # Remove Python 3.13 paths from PATH
    $PathArray = $CurrentPath -split ';'
    $CleanedPathArray = @()
    
    foreach ($PathItem in $PathArray) {
        if ($PathItem -notmatch "python.*3\.13") {
            $CleanedPathArray += $PathItem
        } else {
            Write-Host '[REMOVED] Python 3.13 path: ' + $PathItem -ForegroundColor Red
        }
    }
    
    # Add Python 3.11 paths to the beginning of PATH
    $Python311Paths = @($Python311Dir, $Python311Scripts)
    
    # Check if Python 3.11 paths are already in PATH
    $Python311InPath = $false
    foreach ($PathItem in $CleanedPathArray) {
        if ($PathItem -eq $Python311Dir -or $PathItem -eq $Python311Scripts) {
            $Python311InPath = $true
            break
        }
    }
    
    if (-not $Python311InPath) {
        $CleanedPathArray = $Python311Paths + $CleanedPathArray
        Write-Host '[ADDED] Python 3.11 paths to PATH' -ForegroundColor Green
    } else {
        Write-Host '[INFO] Python 3.11 paths already in PATH' -ForegroundColor Cyan
    }
    
    # Update PATH in registry
    $NewPath = $CleanedPathArray -join ';'
    [Environment]::SetEnvironmentVariable("PATH", $NewPath, "Machine")
    Write-Host '[INFO] Updated system PATH' -ForegroundColor Cyan
    
    # Update current session PATH
    $env:PATH = ($Python311Paths + $env:PATH -split ';') -join ';'
    Write-Host '[INFO] Updated current session PATH' -ForegroundColor Cyan
    
} else {
    Write-Host '[ERROR] Could not find Python 3.11 installation' -ForegroundColor Red
    Write-Host '[INFO] Please ensure Python 3.11 is installed and in PATH' -ForegroundColor Yellow
    exit 1
}

# ===================================================================
# VERIFY PYTHON 3.11 SETUP
# ===================================================================
Write-Host '[SETUP] Verifying Python 3.11 setup...' -ForegroundColor Yellow

# Check Python version
try {
    $PythonVersion = & python --version 2>$null
    Write-Host '[SUCCESS] Python command working: ' + $PythonVersion -ForegroundColor Green
} catch {
    Write-Host '[WARNING] Python command not working in current session' -ForegroundColor Yellow
}

# Check Python3 version
try {
    $Python3Version = & python3 --version 2>$null
    Write-Host '[SUCCESS] Python3 command working: ' + $Python3Version -ForegroundColor Green
} catch {
    Write-Host '[WARNING] Python3 command not working in current session' -ForegroundColor Yellow
}

# Check pip
try {
    $PipVersion = & pip --version 2>$null
    Write-Host '[SUCCESS] pip working: ' + $PipVersion -ForegroundColor Green
} catch {
    Write-Host '[WARNING] pip not working in current session' -ForegroundColor Yellow
}

# ===================================================================
# INSTALL ESSENTIAL PACKAGES
# ===================================================================
Write-Host '[SETUP] Installing essential Python packages...' -ForegroundColor Yellow

# Upgrade pip
Write-Host '[INFO] Upgrading pip...' -ForegroundColor Cyan
try {
    & python -m pip install --upgrade pip
    Write-Host '[SUCCESS] pip upgraded' -ForegroundColor Green
} catch {
    Write-Host '[WARNING] Failed to upgrade pip: ' + $($_.Exception.Message) -ForegroundColor Yellow
}

# Install essential packages
Write-Host '[INFO] Installing essential packages...' -ForegroundColor Cyan
try {
    & python -m pip install setuptools wheel
    Write-Host '[SUCCESS] Essential packages installed' -ForegroundColor Green
} catch {
    Write-Host '[WARNING] Failed to install essential packages: ' + $($_.Exception.Message) -ForegroundColor Yellow
}

# Install project dependencies if requirements.txt exists
if (Test-Path "requirements.txt") {
    Write-Host '[INFO] Installing project dependencies from requirements.txt...' -ForegroundColor Cyan
    try {
        & python -m pip install -r requirements.txt
        Write-Host '[SUCCESS] Project dependencies installed' -ForegroundColor Green
    } catch {
        Write-Host '[WARNING] Failed to install project dependencies: ' + $($_.Exception.Message) -ForegroundColor Yellow
    }
} else {
    Write-Host '[INFO] No requirements.txt found, skipping project dependencies' -ForegroundColor Cyan
}

# ===================================================================
# CREATE VIRTUAL ENVIRONMENT
# ===================================================================
Write-Host '[SETUP] Creating Python 3.11 virtual environment...' -ForegroundColor Yellow

if (-not (Test-Path "venv")) {
    try {
        & python -m venv venv
        Write-Host '[SUCCESS] Created virtual environment: venv' -ForegroundColor Green
    } catch {
        Write-Host '[WARNING] Failed to create virtual environment: ' + $($_.Exception.Message) -ForegroundColor Yellow
    }
} else {
    Write-Host '[INFO] Virtual environment already exists: venv' -ForegroundColor Cyan
}

# ===================================================================
# FINAL VERIFICATION
# ===================================================================
Write-Host '[SETUP] Final verification...' -ForegroundColor Yellow

# Run the verification script
$VerificationScript = Join-Path $PSScriptRoot "verify-python311-env.ps1"
if (Test-Path $VerificationScript) {
    Write-Host '[INFO] Running Python 3.11 verification...' -ForegroundColor Cyan
    try {
        & $VerificationScript
    } catch {
        Write-Host '[WARNING] Verification script failed: ' + $($_.Exception.Message) -ForegroundColor Yellow
    }
} else {
    Write-Host '[WARNING] Verification script not found' -ForegroundColor Yellow
}

# ===================================================================
# SUMMARY
# ===================================================================
Write-Host '[SETUP] Python 3.11 environment setup completed!' -ForegroundColor Green
Write-Host ""
Write-Host '[SUMMARY] What was done:' -ForegroundColor Cyan
Write-Host '  - Checked for existing Python installations' -ForegroundColor Gray
Write-Host '  - Downloaded and installed Python 3.11 (if needed)' -ForegroundColor Gray
Write-Host '  - Configured Python 3.11 as primary Python' -ForegroundColor Gray
Write-Host '  - Updated environment variables (PYTHON_HOME, PYTHON_EXECUTABLE)' -ForegroundColor Gray
Write-Host '  - Updated PATH to prioritize Python 3.11' -ForegroundColor Gray
Write-Host '  - Removed Python 3.13 paths from PATH' -ForegroundColor Gray
Write-Host '  - Installed essential Python packages' -ForegroundColor Gray
Write-Host '  - Created virtual environment' -ForegroundColor Gray
Write-Host '  - Verified the setup' -ForegroundColor Gray
Write-Host ""
Write-Host '[IMPORTANT] You may need to restart your terminal or system for all changes to take effect.' -ForegroundColor Yellow
Write-Host '[INFO] To activate the virtual environment, run: .\venv\Scripts\Activate.ps1' -ForegroundColor Cyan
Write-Host '[INFO] To verify the setup, run: .\scripts\verify-python311-env.ps1' -ForegroundColor Cyan
Write-Host ""

if (-not $Force) {
    Write-Host 'Press any key to continue...' -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
