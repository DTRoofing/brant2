# Integration Testing Strategy

This document outlines the strategy for integration testing the Brant Roofing System. While unit tests verify individual components in isolation, integration tests ensure that these components work together correctly in a realistic environment.

## 🎯 Objectives

- **Verify Data Flow:** Ensure data moves correctly from API -> Database -> Message Queue -> Worker -> External Services -> Database.
- **Test Component Boundaries:** Validate the contracts and communication between the `api` service, `worker` service, databases, and mocked external APIs.
- **Simulate Real-World Scenarios:** Test the full document processing pipeline from file upload to result retrieval.
- **Validate Error Handling:** Ensure the system behaves gracefully when a component (like an external AI service) fails.

## 🛠️ Tooling and Environment

We leverage the existing `pytest` framework and enhance it with tools to create a realistic, containerized testing environment.

- **Test Runner:** `pytest`
- **HTTP Client:** `httpx.AsyncClient` for making async requests to the FastAPI application.
- **Containerization:** `docker-compose` to orchestrate the test environment.
- **Test Environment (`docker-compose.test.yml`):**
  - `test-db`: A dedicated PostgreSQL container for test data.
  - `test-redis`: A dedicated Redis container for Celery tasks during tests.
  - `test-api`: The FastAPI application, configured to use the test database and Redis.
  - `test-worker`: The Celery worker, also connected to the test environment.
- **Mocking:** `pytest-mock` (`mocker`) is used to replace external service calls (Claude, Google AI) with predictable mock objects. This makes tests fast, reliable, and free.
- **Celery Testing:** The `celery` library's testing features are used to execute tasks synchronously within the test run, allowing us to verify worker behavior.

## 🧪 Test Scenarios

The primary integration test file is `tests/integration/test_full_workflow.py`. It covers the following key scenarios:

1. **Happy Path (Successful Workflow):**
    - A user uploads a valid PDF.
    - The API service creates a `Document` record in the database with `PENDING` status.
    - A Celery task is enqueued for the worker.
    - The worker picks up the task, updates the status to `PROCESSING`.
    - The worker calls the (mocked) external AI services.
    - The worker saves the final `ProcessingResults` to the database and sets the document status to `COMPLETED`.
    - The user can retrieve the final, correct results from the API.

2. **Failure Path (AI Service Fails):**
    - A user uploads a valid PDF, and the process begins as normal.
    - During processing, the mocked Claude AI service is configured to raise an exception.
    - The worker catches the exception.
    - The worker updates the document status to `FAILED` in the database.
    - The Celery task is marked as failed.
    - The user sees the `FAILED` status when querying the API.

## ⚙️ Running the Integration Tests

A `Makefile` command simplifies the process.

```bash
# This command will:
# 1. Start the test environment using docker-compose.test.yml
# 2. Run the pytest suite against the running test-api container.
# 3. Shut down and clean up the test environment.
make test-integration
```

### Manual Steps

1. **Start the test environment:**

    ```bash
    docker-compose -f docker-compose.test.yml up -d --build
    ```

2. **Run the tests:**

    ```bash
    docker-compose -f docker-compose.test.yml exec test-api pytest tests/integration/
    ```

3. **Tear down the environment:**

    ```bash
    docker-compose -f docker-compose.test.yml down
    ```

## 📂 New & Modified Files

- **`INTEGRATION_TESTING_STRATEGY.md`**: This file.
- **`docker-compose.test.yml`**: A new Docker Compose file defining the isolated test environment.
- **`tests/integration/test_full_workflow.py`**: The new test suite containing the end-to-end workflow tests.
- **`tests/conftest.py`**: Updated with new fixtures to mock Google AI services.
- **`Makefile`**: Updated with a new `test-integration` command.

This strategy ensures that we have high confidence in the interactions between our services before deploying to production.
