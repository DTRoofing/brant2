# Fix Google Cloud Artifact Registry Permissions

## 🚨 **PROBLEM**
Cloud Build is failing with the error:
```
DENIED: Permission "artifactregistry.repositories.uploadArtifacts" denied on resource "projects/brant-roofing-system-2025/locations/us-central1/repositories/brant-repo"
```

## 🔧 **SOLUTION**

### **Method 1: Using Google Cloud Console (Recommended)**

1. **Open Google Cloud Console**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Select project: `brant-roofing-system-2025`

2. **Navigate to IAM & Admin**
   - Go to **IAM & Admin** → **IAM**
   - Find the Cloud Build service account: `[PROJECT_NUMBER]@cloudbuild.gserviceaccount.com`

3. **Add Required Roles**
   Click **Edit** (pencil icon) next to the Cloud Build service account and add these roles:
   - `Artifact Registry Writer`
   - `Artifact Registry Reader`
   - `Storage Admin`
   - `Cloud Build Editor`
   - `Service Account User`
   - `Cloud SQL Client`
   - `Secret Manager Secret Accessor`

4. **Save Changes**
   - Click **Save**

### **Method 2: Using gcloud CLI**

Run this command in your terminal:

```bash
# Get project number
PROJECT_NUMBER=$(gcloud projects describe brant-roofing-system-2025 --format="value(projectNumber)")

# Grant Artifact Registry permissions
gcloud projects add-iam-policy-binding brant-roofing-system-2025 \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding brant-roofing-system-2025 \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/artifactregistry.reader"

gcloud projects add-iam-policy-binding brant-roofing-system-2025 \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding brant-roofing-system-2025 \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/cloudbuild.builds.editor"

gcloud projects add-iam-policy-binding brant-roofing-system-2025 \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding brant-roofing-system-2025 \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding brant-roofing-system-2025 \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### **Method 3: Using the Provided Scripts**

**For Linux/Mac:**
```bash
chmod +x fix-artifact-registry-permissions.sh
./fix-artifact-registry-permissions.sh
```

**For Windows PowerShell:**
```powershell
.\fix-artifact-registry-permissions.ps1
```

## 🔍 **VERIFY THE FIX**

After applying the permissions, verify they're working:

1. **Check IAM Policy**
   ```bash
   gcloud projects get-iam-policy brant-roofing-system-2025 \
       --flatten="bindings[].members" \
       --format="table(bindings.role)" \
       --filter="bindings.members:[PROJECT_NUMBER]@cloudbuild.gserviceaccount.com"
   ```

2. **Test Artifact Registry Access**
   ```bash
   gcloud artifacts repositories list --location=us-central1
   ```

3. **Retry Cloud Build**
   - Go to Cloud Build → History
   - Click **Retry** on the failed build

## 📋 **REQUIRED ROLES EXPLANATION**

| Role | Purpose |
|------|---------|
| `Artifact Registry Writer` | Push Docker images to Artifact Registry |
| `Artifact Registry Reader` | Pull Docker images from Artifact Registry |
| `Storage Admin` | Access Google Cloud Storage for build artifacts |
| `Cloud Build Editor` | Execute Cloud Build operations |
| `Service Account User` | Use other service accounts during build |
| `Cloud SQL Client` | Connect to Cloud SQL database |
| `Secret Manager Secret Accessor` | Access secrets during build |

## 🚀 **NEXT STEPS**

1. Apply the permission fix using one of the methods above
2. Wait 2-3 minutes for permissions to propagate
3. Retry the Cloud Build trigger
4. Monitor the build logs for success

## ⚠️ **TROUBLESHOOTING**

If the issue persists:

1. **Check Project Number**: Ensure you're using the correct project number
2. **Wait for Propagation**: IAM changes can take up to 7 minutes to propagate
3. **Verify Repository**: Ensure the Artifact Registry repository exists
4. **Check Service Account**: Verify the Cloud Build service account exists

## 📞 **SUPPORT**

If you continue to have issues:
1. Check the [Google Cloud IAM documentation](https://cloud.google.com/iam/docs)
2. Review the [Artifact Registry permissions guide](https://cloud.google.com/artifact-registry/docs/access-control)
3. Contact Google Cloud Support if needed
