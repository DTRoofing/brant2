# BRANT Roofing System - Google Cloud Deployment Guide

This guide details the process for deploying the Brant Roofing System to Google Cloud using the automated CI/CD pipeline defined in `cloudbuild.yaml`. This approach uses serverless technologies (Cloud Run, Cloud SQL, etc.) for a scalable and maintainable production environment.

## 🚀 Deployment Architecture

The system is deployed as three distinct services on Cloud Run:

1. **`brant-frontend`**: The public-facing Next.js user interface.
2. **`brant-api`**: The internal FastAPI backend, handling business logic and API requests.
3. **`brant-worker`**: A background Celery worker for processing large PDF files asynchronously.

These services connect to managed databases (Cloud SQL for PostgreSQL, Memorystore for Redis) via a VPC Connector for security and performance.

---

## 📋 Step 1: Infrastructure Prerequisites

Before your first deployment, ensure the following resources are created in your Google Cloud project. These are a one-time setup.

1. **Enable APIs**: Make sure the following APIs are enabled:
    - Cloud Build API
    - Cloud Run Admin API
    - Artifact Registry API
    - Secret Manager API
    - Cloud SQL Admin API
    - Document AI API

2. **Create a Service Account**:
    - Create a new service account (e.g., `brant-app-sa`).
    - Grant it the IAM roles listed in the `_SERVICE_ACCOUNT` comment in `cloudbuild.yaml`. This includes roles for Cloud Run, Secret Manager, Cloud SQL, Document AI, and Storage.

3. **Create Cloud SQL (PostgreSQL) Instance**:
    - Provision a new Cloud SQL for PostgreSQL instance.
    - **Important**: Enable the "Private IP" option.
    - Create a database and a user. Note the connection details (private IP, user, password, db name).

4. **Create Memorystore (Redis) Instance**:
    - Provision a new Memorystore for Redis instance.
    - **Important**: Note its private IP address.

5. **Create a VPC Connector**:
    - Create a Serverless VPC Access connector in the same region as your services. This allows Cloud Run to communicate with Cloud SQL and Memorystore over their private IPs.

6. **Create an Artifact Registry Repository**:
    - Create a new Docker repository in Artifact Registry (e.g., `brant-repo`) in the same region as your services.

7. **Configure Secrets**:
    - Follow the guide in `SECRETS.md` to create all required secrets in Google Secret Manager. Use the private IPs from the database and Redis instances you just created.

---

## 📦 Step 2: Configure the Cloud Build Trigger

The recommended way to deploy is by connecting Cloud Build to your Git repository (e.g., on GitHub or Cloud Source Repositories).

1. **Navigate to Cloud Build > Triggers** in the GCP Console.
2. **Create a new trigger**.
3. **Connect your Git repository**.
4. **Configure the trigger settings**:
    - **Name**: e.g., "Deploy to Production"
    - **Event**: Push to a branch (e.g., `main` or `master`)
    - **Build Configuration**: Cloud Build configuration file (YAML)
    - **Location**: `/cloudbuild.yaml`
5. **Add Substitution Variables**:
    - The `cloudbuild.yaml` file defines several substitution variables (`_REGION`, `_SERVICE_ACCOUNT`, etc.). You can override them here if needed.
    - **Crucially, you must set `_API_URL`**. Follow the instructions in the `cloudbuild.yaml` comments:
        - For the very first run, you can leave it as a placeholder or use the anticipated Cloud Run service URL for the API.
        - After the first deployment, you will set up a Load Balancer and update this variable with the permanent URL.

---

## 🚀 Step 3: Deploy

With the trigger configured, deployment is automatic:

1. **Push your code** to the branch configured in the trigger (e.g., `git push origin main`).
2. **Monitor the build** in the Cloud Build history page. The pipeline will:
    - Run tests and vulnerability scans.
    - Build the three service images.
    - Push the images to Artifact Registry.
    - Deploy the services to Cloud Run.

### Manual Deployment

You can also trigger a build manually from your local machine (if you have `gcloud` configured):

```bash
gcloud builds submit --config cloudbuild.yaml .
```

---

## 🌐 Step 4: Automated & Post-Deployment Configuration

1. **Database Migrations (Automated)**:
    - The CI/CD pipeline automatically runs database migrations after the `brant-api` service is successfully deployed.
    - This is handled by a dedicated Cloud Run Job (`brant-db-migrations`) that uses the newly built API image and runs the `alembic upgrade head` command.
    - This ensures that the database schema is always in sync with the application code before the worker service starts processing tasks, removing the need for manual intervention.

2. **Set up a Global External HTTPS Load Balancer (One-Time Setup)**:
    - Create a Load Balancer to provide a single, stable, and secure (`https://`) endpoint for your API.
    - Create a "Serverless NEG" (Network Endpoint Group) as the backend, pointing to your `brant-api` Cloud Run service.
    - Configure a frontend with a static IP and a Google-managed SSL certificate.

3. **Update the `_API_URL` (One-Time Update)**:
    - Once the Load Balancer is active, copy its public URL.
    - Go back to your Cloud Build trigger settings and update the `_API_URL` substitution variable to this permanent URL.

All subsequent builds will now correctly wire the frontend to the production API endpoint.

---

## 🔍 Monitoring

- **Logs**: View aggregated logs for all services in Google Cloud's Log Explorer.
- **Metrics**: Monitor performance, instance counts, and error rates in the Cloud Run dashboard.
- **Errors**: Use Google Cloud Error Reporting to automatically capture and alert on application exceptions.
