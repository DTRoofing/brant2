# How to Retrigger Cloud Build

## Quick Retrigger Methods

### Method 1: Push Empty Commit (Recommended)
```bash
# Create an empty commit to retrigger the build
git commit --allow-empty -m "retrigger: Force Cloud Build to run again"

# Push to trigger the build
git push origin main
```

### Method 2: Manual Trigger via gcloud CLI
```bash
# Trigger build manually
gcloud builds submit --config=cloudbuild.yaml .

# Or trigger with specific substitutions
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions=_REGION=us-central1,_GCR_HOSTNAME=us-central1-docker.pkg.dev .
```

### Method 3: GitHub Web Interface
1. Go to https://github.com/DTRoofing/brant2
2. Click **Actions** tab
3. Find the latest workflow run
4. Click **Re-run jobs** or **Re-run all jobs**

### Method 4: Google Cloud Console
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **Cloud Build** → **Triggers**
3. Find your trigger and click **Run**

## Automated Retrigger Script

### Windows (PowerShell/CMD)
```bash
# Navigate to project directory
cd "C:\Development\Final Build\brant"

# Create empty commit and push
git commit --allow-empty -m "retrigger: Force Cloud Build to run again"
git push origin main

# Monitor the build
gcloud builds list --limit=1
```

### Linux/Mac (Terminal)
```bash
# Navigate to project directory
cd "/c/Development/Final Build/brant"

# Create empty commit and push
git commit --allow-empty -m "retrigger: Force Cloud Build to run again"
git push origin main

# Monitor the build
gcloud builds list --limit=1
```

## Expected Results

After retriggering:
- ✅ **New Build Starts**: Fresh Cloud Build instance
- ✅ **Latest Configuration**: Uses all the fixes we applied
- ✅ **No Volume Errors**: Should start successfully
- ✅ **Complete Pipeline**: Quality gates → Build → Deploy

## Monitor the Retriggered Build

```bash
# Check if new build started
gcloud builds list --limit=2

# Stream logs of latest build
gcloud builds log --stream $(gcloud builds list --limit=1 --format="value(id)")

# Or use monitoring script
monitor-build.bat  # Windows
./monitor-build.sh  # Linux/Mac
```

## Troubleshooting

### If Build Still Fails
1. **Check logs**: `gcloud builds log $(gcloud builds list --limit=1 --format="value(id)")`
2. **Verify configuration**: Ensure all fixes are applied
3. **Check permissions**: Ensure service account has required roles
4. **Review substitutions**: Verify all variables are set correctly

### If No Build Starts
1. **Check trigger**: Ensure Cloud Build trigger is active
2. **Check branch**: Ensure trigger is set for `main` branch
3. **Check permissions**: Ensure repository has proper access
4. **Check quotas**: Ensure Cloud Build quotas are not exceeded

---

**Ready to retrigger!** 🚀 Choose your preferred method above.
