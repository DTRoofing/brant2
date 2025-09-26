# Comprehensive Service Account Permissions Verification Script
# This script checks all service accounts and their roles for the Brant Roofing System

[CmdletBinding()]
param (
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,
    [string]$Region = "us-central1"
)

Write-Host "🔍 COMPREHENSIVE PERMISSIONS VERIFICATION" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Project: $ProjectId" -ForegroundColor Cyan
Write-Host "Date: $(Get-Date)" -ForegroundColor Cyan
Write-Host ""

# Fetch the entire IAM policy once for efficiency
Write-Host "Fetching IAM policy for project $ProjectId..." -ForegroundColor Yellow
try {
    $iamPolicy = gcloud projects get-iam-policy $ProjectId --format=json | ConvertFrom-Json
    Write-Host "✅ Successfully fetched IAM policy." -ForegroundColor Green
}
catch {
    Write-Host "❌ CRITICAL: Failed to fetch IAM policy for project $ProjectId. Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Function to check a service account against the pre-fetched IAM policy
function Check-ServiceAccount {
    param(
        [Parameter(Mandatory = $true)]
        [psobject]$SaObject,
        [Parameter(Mandatory = $true)]
        [psobject]$IamPolicy,
        [string]$SaEmail,
        [string]$SaName,
        [string]$ExpectedRoles
    )
    
    Write-Host "📋 Checking: $SaName" -ForegroundColor Yellow
    Write-Host "   Email: $SaEmail" -ForegroundColor White
    
    # Check if service account exists
    if ($SaObject) {
        Write-Host "   ✅ Service account exists" -ForegroundColor Green
    }
    else {
        Write-Host "   ❌ Service account does not exist in project IAM bindings" -ForegroundColor Red
        return
    }

    # Get current roles from the pre-fetched policy
    Write-Host "   📝 Current roles:" -ForegroundColor Cyan
    $memberIdentifier = "serviceAccount:$SaEmail"
    $roles = $IamPolicy.bindings | Where-Object { $_.members -contains $memberIdentifier } | Select-Object -ExpandProperty role
    
    if ($roles) {
        $roles | ForEach-Object { Write-Host "      - $_" -ForegroundColor White }
    }
    else {
        Write-Host "      - No project-level roles assigned." -ForegroundColor White
    }

    # Check for security issues
    Write-Host "   🔒 Security analysis:" -ForegroundColor Cyan
    
    $hasCriticalIssues = $false
    # Check for overly broad roles
    $broadRoles = @("roles/editor", "roles/owner", "roles/compute.admin")
    foreach ($broadRole in $broadRoles) {
        if ($roles -contains $broadRole) {
            Write-Host "      ⚠️  WARNING: Has overly broad role: $broadRole" -ForegroundColor Red
            $hasCriticalIssues = $true
        }
    }
    
    if (-not $hasCriticalIssues) {
        Write-Host "      ✅ No critical security issues found" -ForegroundColor Green
    }
    
    Write-Host ""
}

# Function to check project-level permissions
function Check-ProjectPermissions {
    Write-Host "🏗️  PROJECT-LEVEL PERMISSIONS" -ForegroundColor Green
    Write-Host "==============================" -ForegroundColor Green
    
    # Check if Artifact Registry repository exists
    Write-Host "📦 Artifact Registry Repository:" -ForegroundColor Yellow
    try {
        $repo = gcloud artifacts repositories describe brant-repo --location=$Region --project=$ProjectId --format="value(name)" 2>$null
        if ($repo) {
            Write-Host "   ✅ Repository 'brant-repo' exists" -ForegroundColor Green
        } else {
            Write-Host "   ❌ Repository 'brant-repo' not found" -ForegroundColor Red
        }
    } catch {
        Write-Host "   ❌ Error checking repository: $_" -ForegroundColor Red
    }
    
    # Check Cloud Build permissions
    Write-Host ""
    Write-Host "🔨 Cloud Build Configuration:" -ForegroundColor Yellow
    try {
        $cloudBuildMember = $iamPolicy.bindings | Where-Object { $_.role -eq 'roles/cloudbuild.builds.builder' } | Select-Object -ExpandProperty members -First 1
        if ($cloudBuildMember -and $cloudBuildMember -like "serviceAccount:*") {
            Write-Host "   ✅ Default Cloud Build SA found: $cloudBuildMember" -ForegroundColor Green
        } else {
            Write-Host "   ❌ No Cloud Build service account found with 'roles/cloudbuild.builds.builder'" -ForegroundColor Red
        }

        # Verify roles for the specific service account used by Cloud Run services
        $runServiceAccountEmail = "brant-cloudbuild@brant-roofing-system-2025.iam.gserviceaccount.com"
        $runServiceAccountMember = "serviceAccount:$runServiceAccountEmail"
        Write-Host "   ℹ️  Verifying roles for Cloud Run Service Account: $runServiceAccountEmail" -ForegroundColor Cyan

        $runServiceAccountRoles = $iamPolicy.bindings | Where-Object { $_.members -contains $runServiceAccountMember } | Select-Object -ExpandProperty role

        # Check for Cloud Run Admin role (needed for domain mapping)
        if ($runServiceAccountRoles -contains 'roles/run.admin') {
            Write-Host "      ✅ Has 'roles/run.admin' for domain mapping." -ForegroundColor Green
        }
        else {
            Write-Host "      ⚠️  WARNING: Missing 'roles/run.admin'. Domain mapping step may fail." -ForegroundColor Red
        }

        # Check for Secret Manager Secret Accessor role (needed for runtime secrets)
        if ($runServiceAccountRoles -contains 'roles/secretmanager.secretAccessor') {
            Write-Host "      ✅ Has 'roles/secretmanager.secretAccessor' for runtime secrets." -ForegroundColor Green
        }
        else {
            Write-Host "      ❌ CRITICAL: Missing 'roles/secretmanager.secretAccessor'. API service will fail to start." -ForegroundColor Red
        }

    } catch {
        Write-Host "   ❌ Error checking Cloud Build permissions: $_" -ForegroundColor Red
    }
    
    Write-Host ""
}

# Function to check if necessary APIs are enabled
function Check-EnabledApis {
    Write-Host "🔌 CHECKING ENABLED APIS" -ForegroundColor Green
    Write-Host "=========================" -ForegroundColor Green
    
    $requiredApis = @(
        "run.googleapis.com",
        "iam.googleapis.com",
        "cloudbuild.googleapis.com",
        "artifactregistry.googleapis.com",
        "sqladmin.googleapis.com",
        "documentai.googleapis.com",
        "secretmanager.googleapis.com",
        "vision.googleapis.com"
    )

    Write-Host "Fetching enabled APIs for project $ProjectId..." -ForegroundColor Yellow
    $enabledApis = gcloud services list --project=$ProjectId --enabled --format="value(config.name)"
    Write-Host ""

    foreach ($api in $requiredApis) {
        if ($enabledApis -contains $api) {
            Write-Host "   ✅ $api is enabled" -ForegroundColor Green
        } else {
            Write-Host "   ❌ WARNING: $api is NOT enabled. This could cause runtime errors." -ForegroundColor Red
        }
    }
    Write-Host ""
}

# Function to check for security best practices
function Check-SecurityBestPractices {
    param(
        [Parameter(Mandatory = $true)]
        [psobject]$IamPolicy
    )
    Write-Host "🛡️  SECURITY BEST PRACTICES CHECK" -ForegroundColor Green
    Write-Host "==================================" -ForegroundColor Green
    
    # Check for service accounts with too many roles
    Write-Host "📊 Service accounts with many roles:" -ForegroundColor Yellow
    $roleCounts = $IamPolicy.bindings |
        Select-Object -ExpandProperty members |
        Where-Object { $_ -like "serviceAccount:*" } |
        Group-Object |
        Select-Object @{Name = "ServiceAccount"; Expression = { $_.Name } }, Count |
        Sort-Object Count -Descending

    $highRoleCountAccounts = $roleCounts | Where-Object { $_.Count -gt 5 }
    if ($highRoleCountAccounts) {
        foreach ($account in $highRoleCountAccounts) {
            Write-Host "   ⚠️  $($account.ServiceAccount) has $($account.Count) roles (consider reviewing)" -ForegroundColor Red
        }
    } else {
        Write-Host "   ✅ No service accounts with an excessive number of roles found." -ForegroundColor Green
    }
    Write-Host ""
}

# Main verification
Write-Host "🚀 Starting comprehensive permissions verification..." -ForegroundColor Green
Write-Host ""
Write-Host "Discovering all service accounts in project $ProjectId..." -ForegroundColor Yellow
try {
    $allServiceAccounts = gcloud iam service-accounts list --project=$ProjectId --format=json | ConvertFrom-Json
    Write-Host "✅ Found $($allServiceAccounts.Count) service accounts." -ForegroundColor Green
}
catch {
    Write-Host "❌ CRITICAL: Failed to list service accounts. Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Check each discovered service account
foreach ($sa in $allServiceAccounts) {
    Check-ServiceAccount -SaObject $sa -IamPolicy $iamPolicy -SaEmail $sa.email -SaName $sa.displayName
}

# Check if required APIs are enabled
Check-EnabledApis

# Check project-level permissions
Check-ProjectPermissions -IamPolicy $iamPolicy

# Check security best practices
Check-SecurityBestPractices -IamPolicy $iamPolicy

Write-Host "✅ PERMISSIONS VERIFICATION COMPLETE" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 SUMMARY:" -ForegroundColor Cyan
Write-Host "   - All service accounts verified" -ForegroundColor White
Write-Host "   - Security best practices checked" -ForegroundColor White
Write-Host "   - Project-level permissions verified" -ForegroundColor White
Write-Host ""
Write-Host "🎯 NEXT STEPS:" -ForegroundColor Cyan
Write-Host "   1. Review any warnings above" -ForegroundColor White
Write-Host "   2. Remove unused roles if found" -ForegroundColor White
Write-Host "   3. Test Cloud Build deployment" -ForegroundColor White
Write-Host ""
Write-Host "🔗 USEFUL COMMANDS:" -ForegroundColor Cyan
Write-Host "   - View all IAM policies: gcloud projects get-iam-policy $ProjectId" -ForegroundColor White
Write-Host "   - List service accounts: gcloud iam service-accounts list --project=$ProjectId" -ForegroundColor White
Write-Host "   - Test Cloud Build: gcloud builds triggers list --project=$ProjectId" -ForegroundColor White
