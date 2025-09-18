from pydantic import BaseModel, Field

class GenerateUploadUrlRequest(BaseModel):
    filename: str = Field(..., description="The name of the file to be uploaded.")
    content_type: str = Field(..., description="The MIME type of the file.")

class GenerateUploadUrlResponse(BaseModel):
    upload_url: str = Field(..., description="The v4 signed URL for the PUT request.")
    gcs_object_name: str = Field(..., description="The full path of the object in GCS.")

class StartProcessingRequest(BaseModel):
    gcs_object_name: str = Field(..., description="The GCS object name of the uploaded file.")
    original_filename: str = Field(..., description="The original name of the uploaded file.")
    document_type: str = Field(..., description="The type of document being processed (e.g., 'standard').")
