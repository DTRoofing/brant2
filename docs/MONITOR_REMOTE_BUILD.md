# How to Monitor Remote Cloud Build

## Quick Monitoring Commands

### 1. Check Build Status via gcloud CLI
```bash
# List recent builds
gcloud builds list --limit=5

# Get details of the latest build
gcloud builds describe $(gcloud builds list --limit=1 --format="value(id)")

# Stream logs of the latest build
gcloud builds log --stream $(gcloud builds list --limit=1 --format="value(id)")

# Monitor builds in real-time
gcloud builds list --ongoing
```

### 2. Check Build Status via GitHub
1. Go to your repository: https://github.com/DTRoofing/brant2
2. Click on the **Actions** tab
3. Look for the latest workflow run
4. Click on the build to see detailed logs

### 3. Google Cloud Console (Web Interface)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **Cloud Build** → **History**
3. Find your latest build (should show "In Progress" or "Success/Failed")
4. Click on the build to see detailed logs and steps

## Detailed Monitoring Steps

### Step 1: Check if Build is Running
```bash
# Check current builds
gcloud builds list --ongoing

# Expected output if build is running:
# ID                                    STATUS    CREATE_TIME                DURATION
# 12345678-1234-1234-1234-123456789abc  WORKING   2024-01-01T12:00:00Z      00:05:23
```

### Step 2: Monitor Build Progress
```bash
# Get the build ID
BUILD_ID=$(gcloud builds list --limit=1 --format="value(id)")

# Stream live logs
gcloud builds log --stream $BUILD_ID

# Or monitor specific build
gcloud builds log --stream 12345678-1234-1234-1234-123456789abc
```

### Step 3: Check Build Steps
```bash
# Get detailed build information
gcloud builds describe $BUILD_ID

# Check specific step status
gcloud builds describe $BUILD_ID --format="value(steps[].status)"
```

## Expected Build Steps

Your build should follow these steps:

### 1. Quality Gates
```
Step 1: Run unit tests and vulnerability scan
- Install dependencies
- Run pytest (unit tests only)
- Run pip-audit (security scan)
```

### 2. Build Services
```
Step 2: Build API service
Step 3: Build Worker service  
Step 4: Build Frontend service
```

### 3. Deploy Services
```
Step 5: Deploy API to Cloud Run
Step 6: Run database migrations
Step 7: Deploy Worker to Cloud Run
Step 8: Deploy Frontend to Cloud Run
```

## Monitoring Commands by Platform

### Windows (PowerShell)
```powershell
# Check builds
gcloud builds list --limit=5

# Stream logs
gcloud builds log --stream (gcloud builds list --limit=1 --format="value(id)")

# Monitor ongoing builds
gcloud builds list --ongoing
```

### Linux/Mac (Terminal)
```bash
# Check builds
gcloud builds list --limit=5

# Stream logs
gcloud builds log --stream $(gcloud builds list --limit=1 --format="value(id)")

# Monitor ongoing builds
gcloud builds list --ongoing
```

## Troubleshooting Build Issues

### If Build Fails
```bash
# Get detailed error information
gcloud builds describe $BUILD_ID

# Check specific step logs
gcloud builds log $BUILD_ID --step=1  # Quality gates
gcloud builds log $BUILD_ID --step=2  # API build
gcloud builds log $BUILD_ID --step=3  # Worker build
gcloud builds log $BUILD_ID --step=4  # Frontend build
```

### Common Build Issues
1. **Quality Gates Fail**: Unit tests or security scan failed
2. **Build Fails**: Docker build issues or missing dependencies
3. **Deploy Fails**: Cloud Run deployment issues
4. **Migration Fails**: Database migration errors

## Build Status Indicators

### Status Meanings
- **WORKING**: Build is currently running
- **SUCCESS**: Build completed successfully
- **FAILURE**: Build failed with errors
- **TIMEOUT**: Build exceeded time limit
- **CANCELLED**: Build was manually cancelled

### Expected Timeline
- **Quality Gates**: 2-5 minutes
- **Build Services**: 5-10 minutes
- **Deploy Services**: 3-5 minutes
- **Total Time**: 10-20 minutes

## Real-time Monitoring Script

Create a monitoring script:

```bash
#!/bin/bash
# monitor-build.sh

echo "🔍 Monitoring Cloud Build..."
echo "=========================="

# Get latest build ID
BUILD_ID=$(gcloud builds list --limit=1 --format="value(id)")
echo "Latest Build ID: $BUILD_ID"

# Check status
STATUS=$(gcloud builds describe $BUILD_ID --format="value(status)")
echo "Status: $STATUS"

if [ "$STATUS" = "WORKING" ]; then
    echo "📊 Build is running... Streaming logs:"
    gcloud builds log --stream $BUILD_ID
elif [ "$STATUS" = "SUCCESS" ]; then
    echo "✅ Build completed successfully!"
    echo "🚀 Services should be deployed to Cloud Run"
elif [ "$STATUS" = "FAILURE" ]; then
    echo "❌ Build failed. Check logs:"
    gcloud builds log $BUILD_ID
else
    echo "📋 Build status: $STATUS"
fi
```

## Quick Status Check

```bash
# One-liner to check latest build status
gcloud builds list --limit=1 --format="table(id,status,createTime,duration)"
```

---

**Ready to monitor!** 🚀 Use any of these methods to track your remote build progress.
