# Debugging FastAPI Routing Issues

This guide explains common causes for `404 Not Found` errors in a layered FastAPI application, using the `/api/v1/documents/upload` endpoint as a case study.

## The Anatomy of a FastAPI Route

In this project, a URL is constructed from three parts, defined in three different files:

1. **Main App Prefix (`app/main.py`)**: This sets the base for the entire API version.
2. **Resource Prefix (`app/api/v1/router.py`)**: This groups all endpoints for a specific resource (e.g., "documents").
3. **Endpoint Path (`app/api/v1/endpoints/documents.py`)**: This defines the final path for the specific action (e.g., "upload").

Let's see how they work together to form the correct URL.

### Correct Configuration Example

This is how the files should be structured to correctly create the `/api/v1/documents/upload` endpoint.

**1. `app/main.py`**

This file includes the main `api_router` and gives it a prefix of `/api/v1`.

```python
from app.api.v1.router import api_router
# ...
app.include_router(api_router, prefix="/api/v1")
```

**2. `app/api/v1/router.py` (The Aggregator)**

This file imports the specific router for documents and gives it a prefix of `/documents`.

```python
from fastapi import APIRouter
from .endpoints import documents

api_router = APIRouter()
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
```

**3. `app/api/v1/endpoints/documents.py` (The Endpoint)**

This file defines the final part of the path, `/upload`.

```python
from fastapi import APIRouter

router = APIRouter()

@router.post("/upload")
def upload_document():
    # ... function logic ...
    return {"message": "File uploaded successfully"}
```

**Result:** `/api/v1` + `/documents` + `/upload` = `/api/v1/documents/upload` ✅

---

## Common Misconfigurations Causing 404 Errors

Based on the test failures and your `CHANGELOG.md`, the following was the most likely cause of the `404 Not Found` error.

### Scenario 1: Incorrect Prefix in the Aggregator Router (Most Likely Cause)

If the aggregator router uses the wrong prefix, the final URL will be incorrect. Your `CHANGELOG.md` notes this exact fix was made.

**File:** `app/api/v1/router.py`

```python
# INCORRECT CONFIGURATION
from fastapi import APIRouter
from .endpoints import documents

api_router = APIRouter()
# The prefix is "/uploads" instead of "/documents"
api_router.include_router(documents.router, prefix="/uploads", tags=["documents"])
```

* **Resulting URL**: `/api/v1/uploads/upload`
* **Symptom**: Any request to `/api/v1/documents/upload` will result in a `404 Not Found`, exactly as reported in your tests.

### Scenario 2: Router Not Included at All

A simple but common mistake is forgetting to include the endpoint router in the aggregator.

**File:** `app/api/v1/router.py`

```python
# INCORRECT CONFIGURATION
from fastapi import APIRouter
# from .endpoints import documents # <-- Line is commented out or missing

api_router = APIRouter()
# The include_router line is missing entirely
# api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
```

* **Symptom**: The `/api/v1/documents/upload` endpoint simply won't exist, causing a `404 Not Found`.
