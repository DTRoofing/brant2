#!/usr/bin/env python3
"""
Simple test server to verify API connectivity
"""

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Brant Roofing API Test")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Brant Roofing API Test Server", "status": "running"}

@app.get("/api/v1/health")
async def health():
    return {"status": "healthy", "message": "API is running"}

@app.post("/api/v1/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Mock document upload endpoint"""
    return {
        "message": "Document uploaded successfully",
        "document_id": "test-doc-123",
        "filename": file.filename,
        "size": file.size,
        "status": "uploaded"
    }

@app.post("/api/v1/pipeline/process/{document_id}")
async def start_pipeline_processing(document_id: str):
    """Mock pipeline processing endpoint"""
    return {
        "message": "Pipeline processing started",
        "document_id": document_id,
        "task_id": "task-123",
        "status": "processing"
    }

@app.get("/api/v1/pipeline/status/{document_id}")
async def get_pipeline_status(document_id: str):
    """Mock pipeline status endpoint"""
    return {
        "document_id": document_id,
        "status": "completed",
        "error": None,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }

@app.get("/api/v1/pipeline/results/{document_id}")
async def get_pipeline_results(document_id: str):
    """Mock pipeline results endpoint"""
    return {
        "document_id": document_id,
        "status": "completed",
        "message": "Processing completed successfully",
        "file_path": f"/uploads/{document_id}.pdf",
        "processed_at": "2024-01-01T00:00:00Z",
        "results": {
            "roof_area_sqft": 2500,
            "materials": ["membrane", "insulation"],
            "estimated_cost": 15000,
            "confidence": 0.85,
            "roof_features": [
                {
                    "type": "exhaust_port",
                    "count": 2,
                    "impact": "medium",
                    "description": "Exhaust ports require careful sealing and flashing"
                },
                {
                    "type": "walkway",
                    "count": 1,
                    "impact": "low",
                    "description": "Walkways provide access but may require additional materials"
                }
            ],
            "complexity_factors": [
                "Multiple exhaust ports require specialized flashing",
                "Walkway access affects material delivery"
            ],
            "verification": {
                "ocr_total": 2400,
                "blueprint_total": 2500,
                "difference_percent": 4.2,
                "recommendation": "use_blueprint"
            }
        }
    }

if __name__ == "__main__":
    print("🚀 Starting Brant Roofing API Test Server...")
    print("📍 URL: http://localhost:3001")
    print("📚 API Docs: http://localhost:3001/docs")
    uvicorn.run(app, host="0.0.0.0", port=3001)
