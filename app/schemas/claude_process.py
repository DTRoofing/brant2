from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class ClaudeProcessRequest(BaseModel):
    """
    Request schema for Claude processing endpoint.
    """
    document_id: UUID = Field(..., description="The ID of the document to process")
    processing_options: Optional[dict] = Field(default=None, description="Optional processing configuration")
    
    class Config:
        from_attributes = True

class TaskResponse(BaseModel):
    """
    Response schema for task submission endpoints.
    """
    task_id: str = Field(..., description="The unique identifier for the submitted task")
    status: str = Field(..., description="The current status of the task")
    message: Optional[str] = Field(default=None, description="Additional information about the task")
    
    class Config:
        from_attributes = True

class ClaudeProcessStatus(BaseModel):
    """
    Status schema for Claude processing tasks.
    """
    task_id: str = Field(..., description="The unique identifier for the task")
    status: str = Field(..., description="The current status (pending, processing, completed, failed)")
    progress: Optional[int] = Field(default=None, description="Progress percentage (0-100)")
    result: Optional[dict] = Field(default=None, description="The processing result if completed")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    created_at: Optional[str] = Field(default=None, description="Task creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp")
    
    class Config:
        from_attributes = True
