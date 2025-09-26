# Google Cloud SDK Installation and Configuration Script
# This script will install gcloud CLI if not present and configure it

Write-Host "🔧 Google Cloud SDK Installation and Configuration" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

# Check if gcloud is already installed
$gcloudPath = Get-Command gcloud -ErrorAction SilentlyContinue
if ($gcloudPath) {
    Write-Host "✅ gcloud CLI is already installed at: $($gcloudPath.Source)" -ForegroundColor Green
    Write-Host "Version: $((gcloud version --format='value(Google Cloud SDK)') 2>$null)" -ForegroundColor Cyan
} else {
    Write-Host "❌ gcloud CLI not found. Installing..." -ForegroundColor Red
    
    # Check if Google Cloud SDK is installed but not in PATH
    $possiblePaths = @(
        "C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd",
        "C:\Program Files\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd",
        "$env:USERPROFILE\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
    )
    
    $found = $false
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            Write-Host "✅ Found gcloud at: $path" -ForegroundColor Green
            Write-Host "Adding to PATH..." -ForegroundColor Yellow
            
            # Add to current session PATH
            $env:PATH += ";$(Split-Path $path -Parent)"
            
            # Add to user PATH permanently
            $userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
            if ($userPath -notlike "*$(Split-Path $path -Parent)*") {
                [Environment]::SetEnvironmentVariable("PATH", "$userPath;$(Split-Path $path -Parent)", "User")
                Write-Host "✅ Added to user PATH" -ForegroundColor Green
            }
            
            $found = $true
            break
        }
    }
    
    if (-not $found) {
        Write-Host "❌ Google Cloud SDK not found. Please install it first:" -ForegroundColor Red
        Write-Host "1. Download from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
        Write-Host "2. Or run: winget install Google.CloudSDK" -ForegroundColor Yellow
        Write-Host "3. Or run: choco install gcloudsdk" -ForegroundColor Yellow
        exit 1
    }
}

# Verify gcloud is now available
try {
    $gcloudVersion = gcloud version --format="value(Google Cloud SDK)" 2>$null
    if ($gcloudVersion) {
        Write-Host "✅ gcloud CLI is working! Version: $gcloudVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ gcloud CLI found but not working properly" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error running gcloud: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Check if authenticated
Write-Host ""
Write-Host "🔐 Checking authentication status..." -ForegroundColor Yellow
try {
    $authStatus = gcloud auth list --filter="status:ACTIVE" --format="value(account)" 2>$null
    if ($authStatus) {
        Write-Host "✅ Authenticated as: $authStatus" -ForegroundColor Green
    } else {
        Write-Host "❌ Not authenticated. Please run: gcloud auth login" -ForegroundColor Red
        Write-Host "Or run: gcloud auth activate-service-account --key-file=path/to/key.json" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Error checking authentication: $($_.Exception.Message)" -ForegroundColor Red
}

# Check if project is set
Write-Host ""
Write-Host "🏗️ Checking project configuration..." -ForegroundColor Yellow
try {
    $project = gcloud config get-value project 2>$null
    if ($project) {
        Write-Host "✅ Project set to: $project" -ForegroundColor Green
    } else {
        Write-Host "❌ No project set. Please run: gcloud config set project brant-roofing-system-2025" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error checking project: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎯 Next steps:" -ForegroundColor Cyan
Write-Host "1. If not authenticated: gcloud auth login" -ForegroundColor White
Write-Host "2. Set project: gcloud config set project brant-roofing-system-2025" -ForegroundColor White
Write-Host "3. Run verification: .\verify-permissions.ps1" -ForegroundColor White
