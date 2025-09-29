# ===================================================================
# REMOVE PYTHON 3.13 PATHS FROM ENVIRONMENT VARIABLES
# ===================================================================
# This PowerShell script removes Python 3.13 paths from PATH and other 
# environment variables to prevent conflicts with other Python versions.

param(
    [switch]$WhatIf = $false,
    [switch]$Verbose = $false
)

# Enable verbose output if requested
if ($Verbose) {
    $VerbosePreference = "Continue"
}

Write-Host "[INFO] Starting Python 3.13 path removal process..." -ForegroundColor Green

# ===================================================================
# BACKUP CURRENT ENVIRONMENT
# ===================================================================
Write-Host "[INFO] Creating backup of current environment variables..." -ForegroundColor Yellow

$BackupDate = Get-Date -Format "yyyyMMdd_HHmmss"
Write-Host "[INFO] Backup timestamp: $BackupDate" -ForegroundColor Cyan

# Backup PATH
$CurrentPath = $env:PATH
$CurrentPath | Out-File -FilePath "env_backup_${BackupDate}_PATH.txt" -Encoding UTF8
Write-Host "[INFO] PATH backed up to: env_backup_${BackupDate}_PATH.txt" -ForegroundColor Cyan

# Backup PYTHONPATH if it exists
if ($env:PYTHONPATH) {
    $env:PYTHONPATH | Out-File -FilePath "env_backup_${BackupDate}_PYTHONPATH.txt" -Encoding UTF8
    Write-Host "[INFO] PYTHONPATH backed up to: env_backup_${BackupDate}_PYTHONPATH.txt" -ForegroundColor Cyan
}

# ===================================================================
# REMOVE PYTHON 3.13 PATHS FROM PATH
# ===================================================================
Write-Host "[INFO] Removing Python 3.13 paths from PATH..." -ForegroundColor Yellow

# Split PATH into array and filter out Python 3.13 paths
$PathArray = $env:PATH -split ';'
$CleanedPathArray = @()

foreach ($PathItem in $PathArray) {
    if ($PathItem -match 'python.*3\.13' -or $PathItem -match 'Python.*3\.13') {
        Write-Host "[REMOVED] Python 3.13 path: $PathItem" -ForegroundColor Red
    } else {
        $CleanedPathArray += $PathItem
        if ($Verbose) {
            Write-Host "[KEPT] $PathItem" -ForegroundColor Gray
        }
    }
}

# Rebuild PATH
$NewPath = $CleanedPathArray -join ';'

# ===================================================================
# REMOVE PYTHON 3.13 PATHS FROM PYTHONPATH
# ===================================================================
$NewPythonPath = $null
if ($env:PYTHONPATH) {
    Write-Host "[INFO] Removing Python 3.13 paths from PYTHONPATH..." -ForegroundColor Yellow
    
    $PythonPathArray = $env:PYTHONPATH -split ';'
    $CleanedPythonPathArray = @()
    
    foreach ($PathItem in $PythonPathArray) {
        if ($PathItem -match 'python.*3\.13' -or $PathItem -match 'Python.*3\.13') {
            Write-Host "[REMOVED] Python 3.13 PYTHONPATH: $PathItem" -ForegroundColor Red
        } else {
            $CleanedPythonPathArray += $PathItem
            if ($Verbose) {
                Write-Host "[KEPT PYTHONPATH] $PathItem" -ForegroundColor Gray
            }
        }
    }
    
    $NewPythonPath = $CleanedPythonPathArray -join ';'
}

# ===================================================================
# REMOVE OTHER PYTHON 3.13 RELATED ENVIRONMENT VARIABLES
# ===================================================================
Write-Host "[INFO] Checking for other Python 3.13 related environment variables..." -ForegroundColor Yellow

$PythonEnvVars = @('PYTHON_HOME', 'PYTHON_ROOT', 'PYTHON_INSTALL_DIR', 'PYTHON_EXECUTABLE')

foreach ($EnvVar in $PythonEnvVars) {
    $Value = [Environment]::GetEnvironmentVariable($EnvVar)
    if ($Value -and ($Value -match 'python.*3\.13' -or $Value -match 'Python.*3\.13')) {
        Write-Host "[REMOVED] Python 3.13 environment variable $EnvVar : $Value" -ForegroundColor Red
        if (-not $WhatIf) {
            [Environment]::SetEnvironmentVariable($EnvVar, $null, 'User')
        }
    }
}

# ===================================================================
# APPLY CHANGES
# ===================================================================
if ($WhatIf) {
    Write-Host "[WHAT-IF] Would apply the following changes:" -ForegroundColor Yellow
    Write-Host "  - New PATH length: $($NewPath.Length) characters" -ForegroundColor Cyan
    if ($NewPythonPath) {
        Write-Host "  - New PYTHONPATH length: $($NewPythonPath.Length) characters" -ForegroundColor Cyan
    }
    Write-Host "[WHAT-IF] Use -WhatIf:$false to apply changes" -ForegroundColor Yellow
} else {
    Write-Host "[INFO] Applying cleaned environment variables..." -ForegroundColor Yellow
    
    # Update PATH for current session
    $env:PATH = $NewPath
    
    # Update PYTHONPATH for current session if it was modified
    if ($NewPythonPath) {
        $env:PYTHONPATH = $NewPythonPath
    }
    
    # Update environment variables permanently
    [Environment]::SetEnvironmentVariable('PATH', $NewPath, 'User')
    if ($NewPythonPath) {
        [Environment]::SetEnvironmentVariable('PYTHONPATH', $NewPythonPath, 'User')
    }
}

# ===================================================================
# VERIFY CHANGES
# ===================================================================
Write-Host "[INFO] Verifying changes..." -ForegroundColor Yellow

# Check if any Python 3.13 paths remain in PATH
$RemainingPython313Paths = $env:PATH | Select-String -Pattern 'python.*3\.13' -AllMatches
if ($RemainingPython313Paths) {
    Write-Host "[WARNING] Some Python 3.13 paths may still exist in PATH:" -ForegroundColor Yellow
    $RemainingPython313Paths.Matches | ForEach-Object { Write-Host "  - $($_.Value)" -ForegroundColor Red }
} else {
    Write-Host "[SUCCESS] No Python 3.13 paths found in PATH" -ForegroundColor Green
}

# Check if any Python 3.13 paths remain in PYTHONPATH
if ($env:PYTHONPATH) {
    $RemainingPython313PythonPath = $env:PYTHONPATH | Select-String -Pattern 'python.*3\.13' -AllMatches
    if ($RemainingPython313PythonPath) {
        Write-Host "[WARNING] Some Python 3.13 paths may still exist in PYTHONPATH:" -ForegroundColor Yellow
        $RemainingPython313PythonPath.Matches | ForEach-Object { Write-Host "  - $($_.Value)" -ForegroundColor Red }
    } else {
        Write-Host "[SUCCESS] No Python 3.13 paths found in PYTHONPATH" -ForegroundColor Green
    }
}

# ===================================================================
# DISPLAY CURRENT PYTHON VERSIONS
# ===================================================================
Write-Host "[INFO] Current Python installations in PATH:" -ForegroundColor Yellow

try {
    $PythonCommands = @('python', 'python3')
    foreach ($Cmd in $PythonCommands) {
        $PythonPaths = Get-Command $Cmd -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
        if ($PythonPaths) {
            foreach ($Path in $PythonPaths) {
                Write-Host "  - $Path" -ForegroundColor Cyan
                try {
                    $Version = & $Path --version 2>$null
                    Write-Host "    Version: $Version" -ForegroundColor Gray
                } catch {
                    Write-Host "    Version: Unable to determine" -ForegroundColor Gray
                }
            }
        }
    }
} catch {
    Write-Host "  - No Python found in PATH" -ForegroundColor Gray
}

# ===================================================================
# SUMMARY
# ===================================================================
Write-Host ""
Write-Host "[SUMMARY] Python 3.13 path removal completed" -ForegroundColor Green
Write-Host "[INFO] Backup files created with timestamp: $BackupDate" -ForegroundColor Cyan
Write-Host "[INFO] Current PATH length: $($env:PATH.Length) characters" -ForegroundColor Cyan
if ($env:PYTHONPATH) {
    Write-Host "[INFO] Current PYTHONPATH length: $($env:PYTHONPATH.Length) characters" -ForegroundColor Cyan
}
Write-Host ""
Write-Host "[NOTE] Changes have been applied to both current session and user environment" -ForegroundColor Yellow
Write-Host "[NOTE] You may need to restart your terminal or system for all changes to take effect" -ForegroundColor Yellow
Write-Host ""

if (-not $WhatIf) {
    Write-Host "Press any key to continue..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

