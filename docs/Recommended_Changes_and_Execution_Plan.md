## Recommended Changes and Execution Plan

### Scope
This document consolidates stability fixes, recommended improvements, and an actionable plan to make the Brant Roofing System production‑ready on Google Cloud with high reliability, observability, and maintainability.

### Completed fixes (in this iteration)
- **Cloud Build hardening**
  - Adjusted quality gate to install dev deps, run unit tests, and fail only on CRITICAL vulnerabilities (stores `pip_audit.json`).
  - Fixed `DATABASE_URL` secret mapping to `brant-database-url:latest` (matches Terraform).
  - Made domain mapping idempotent (describe-or-create) to avoid flakiness.
- **Migrations stability**
  - Ensured Alembic uses `settings.DATABASE_URL` in online mode.
- **Processing consistency**
  - Standardized worker and endpoints to use `gcs_object_name` and the new `process_pdf_with_pipeline` task.

### Remaining recommended changes and fixes

1) Data model and API contract unification
- **Issue**: Mixed usage of `file_path`, `gcs_object_name`; local FS paths exist in some code paths.
- **Fix**: Standardize on `gcs_uri` (`gs://bucket/object`), make local writes dev-only and disabled in prod.
- **Actions**:
  - Add/rename column to `gcs_uri` (or keep `gcs_object_name` + bucket), make `file_path` nullable, backfill values from existing data.
  - Update Pydantic schemas and endpoints to return `gcs_uri` consistently; deprecate direct upload endpoint in prod.
  - Add Alembic migration with backfill and non-breaking defaults.
- **Acceptance**: All writes/reads use GCS; no references to local FS in prod; API returns `gcs_uri` consistently.

2) Queueing/orchestration: move to Pub/Sub (serverless‑native)
- **Issue**: Celery+Redis on Cloud Run increases operational complexity and connection handling.
- **Fix**: Introduce Pub/Sub topic `document-processing` with push subscription to the Worker service, then deprecate Celery.
- **Actions**:
  - Terraform: Pub/Sub topic/subscription with DLQ; IAM for service accounts; Eventarc optional.
  - Worker: add Pub/Sub handler (HTTP push) that validates JWT auth header, idempotent by `document_id`.
  - API: publish message with attributes (`document_id`, `gcs_uri`, `mode`). Dual-run (feature flag) before cutover.
  - Remove Redis/Celery after soak.
- **Acceptance**: Throughput parity, no backlog growth; DLQ empty; Celery infra disabled.

3) GCS-only processing and selective extraction
- **Issue**: Some paths assume local files; selective extraction creates temp local files.
- **Fix**: Ensure all processing reads from GCS and writes intermediate results to `extracted/` with lifecycle policies.
- **Actions**:
  - Confirm `download_gcs_to_temp` + `upload_temp_to_gcs` are used only for transient local processing; ensure cleanup on success/failure.
  - Add guardrails to skip local FS in prod (feature flag `ALLOW_LOCAL_FS=false`).
- **Acceptance**: No local FS dependencies at runtime on Cloud Run; temp artifacts are auto-cleaned.

4) Observability and cost controls
- **Issue**: Limited tracing/structured logs; no SLOs, limited alerts.
- **Fix**: Structured JSON logs with correlation IDs; Cloud Trace, Error Reporting; dashboards; alerts.
- **Actions**:
  - Inject `X-Request-ID`/correlation id through API → Pub/Sub attr → Worker logs.
  - Enable Cloud Trace in API/Worker; add Error Reporting.
  - Create Monitoring dashboards: throughput, failure rate, latency, DLQ depth, backlog age, cost per doc.
  - Alerts on DLQ growth, error spikes, Document AI quota, backlog age.
- **Acceptance**: Dashboards live; alerts firing on simulated faults; traces show end-to-end spans.

5) Security and networking
- **Issue**: Need explicit hardening of IAM, egress, and optional compliance.
- **Fix**: Least-privilege IAM; VPC connector egress; Cloud Armor WAF policies; optional VPC‑SC, CMEK.
- **Actions**:
  - Verify service account roles: `secretAccessor`, `run.invoker`, `run.admin` (build deployer), `pubsub.*`, `cloudsql.client`, `storage.object*`, `documentai.apiUser`.
  - Finalize Cloud Armor rules (rate limits, owasp rules) and attach to LB.
  - Consider VPC‑SC perimeter for GCS/Document AI/Secret Manager; evaluate CMEK for SQL/GCS if required.
- **Acceptance**: All services run with minimal IAM; WAF blocks synthetic attacks; pen-test checklist passes.

6) Cloud Run Job for migrations (resilience)
- **Issue**: Migrations can fail if env not fully resolved; logs insufficient.
- **Fix**: Explicit migration entrypoint that resolves `DATABASE_URL` and logs SQLAlchemy connection.
- **Actions**:
  - Update Job template command to `/bin/sh -c "alembic upgrade head"` with `GCP_PROJECT` set.
  - Optionally add a pre-check script to fetch secrets (if not auto-loaded) and verify DB connectivity.
- **Acceptance**: Job succeeds repeatedly; failures produce actionable logs; no partial state.

7) Frontend and domains
- **Issue**: Ensure `NEXT_PUBLIC_API_URL` points to external HTTPS LB; mapping is stable.
- **Fix**: Keep domain mapping steps idempotent; confirm managed cert provisioning; configure Cloud CDN for frontend.
- **Actions**:
  - Validate LB/SSL status; update DNS A/AAAA and CNAMEs as needed.
  - Confirm CORS and auth flows with the LB hostname.
- **Acceptance**: Frontend loads via custom domain with valid cert; API reachable via LB URL.

8) Tests and CI/CD
- **Issue**: Legacy e2e tests expect outdated endpoints/status shapes.
- **Fix**: Update e2e/integration tests to the unified API; keep unit tests fast.
- **Actions**:
  - Modernize e2e paths (`/documents/signed-url`, `/documents`, `/pipeline/process`, `/pipeline/results`).
  - Add smoke tests post‑deploy in Cloud Build.
- **Acceptance**: CI green; post‑deploy smoke passes; rollbacks exercised in rehearsal.

### Execution plan (phased)

Phase 0: Stabilization (done)
- Cloud Build hardening, Alembic online URL, endpoint/worker alignment on GCS.

Phase 1: Contract and schema
- Alembic migration to add `gcs_uri` (or finalize around `gcs_object_name`+bucket) and make `file_path` nullable; code updates; backfill.
- Update OpenAPI schemas/docs; update tests.

Phase 2: Pub/Sub orchestration
- Terraform: topic/subscription (with DLQ) and IAM.
- Worker push endpoint; API publisher; dual-run behind a flag; soak; remove Celery/Redis.

Phase 3: Observability and security
- Structured logging, Trace/Error Reporting; dashboards and alerts.
- WAF rules finalize; egress policy via VPC connector; optional VPC‑SC/CMEK.

Phase 4: LB/CDN and frontend
- Confirm LB/CDN/SSL and domain mapping; set `NEXT_PUBLIC_API_URL` to LB; CORS verification.

Phase 5: Cleanup and documentation
- Remove deprecated endpoints, Celery code and Redis infra; finalize runbooks and on-call docs.

### Rollback strategy
- Keep Celery path disabled but available until Pub/Sub soak is successful.
- Use Cloud Run traffic splitting for gradual rollouts; maintain previous image digests.
- Database migrations are backward-compatible; use additive changes and feature flags.

### Prerequisites and permissions checklist
- Service accounts:
  - Cloud Build SA: deploy permissions (`run.admin`, `artifactregistry.writer`), read secrets.
  - Runtime SA: `secretmanager.secretAccessor`, `cloudsql.client`, `documentai.apiUser`, `storage.objectViewer`, `pubsub.subscriber/publisher` as needed.
- Secrets:
  - `brant-database-url` up-to-date; other app secrets populated; rotation policy set.

### Acceptance and sign‑off
- Cloud Build: green consistently; migrations reliable; zero manual interventions.
- Processing: end-to-end success rate and latency within SLO; no DLQ growth.
- Security: IAM least-privilege validated; WAF effective; optional compliance controls reviewed.


