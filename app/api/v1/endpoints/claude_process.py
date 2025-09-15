"""
Claude AI Processing Endpoint
Direct processing of documents with Claude AI
"""

import logging
import base64
from datetime import datetime
from pathlib import Path
import uuid
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.models.results import ProcessingResults
from app.core.database import get_db
from app.models.core import Document, ProcessingStatus
from app.services.claude_service import claude_service
from app.services.google_services import google_service

logger = logging.getLogger(__name__)

router = APIRouter()


class ClaudeProcessRequest(BaseModel):
    document_id: str
    prompt: Optional[str] = None  # Prompt is now optional and will be ignored


def _get_base_prompt():
    """Loads the master prompt from the filesystem."""
    try:
        prompt_path = Path(__file__).parent.parent.parent.parent / "prompts" / "roofing_estimation_prompt.txt"
        with open(prompt_path, "r") as f:
            return f.read()
    except Exception as e:
        logger.warning(f"Could not load prompt file: {e}. Using fallback prompt.")
        return "You are an expert roofing estimator. Analyze the document and extract key information for a cost estimate."


async def _extract_text_from_document(file_path: str) -> str:
    """Extracts text using Google Document AI with a PyPDF2 fallback."""
    try:
        if google_service.document_ai_client:
            result = await google_service.process_document_with_ai(file_path)
            if result and result.get('text'):
                logger.info("Extracted text using Google Document AI.")
                return result['text']
    except Exception as e:
        logger.warning(f"Google Document AI failed: {e}. Falling back to PyPDF2.")

    try:
        import PyPDF2
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += (page.extract_text() or "") + "\n"
        logger.info("Extracted text using PyPDF2 fallback.")
        return text
    except Exception as e:
        logger.error(f"PyPDF2 text extraction also failed: {e}")
        return ""


class ClaudeProcessResponse(BaseModel):
    document_id: str
    status: str
    claude_response: Dict[str, Any]
    extracted_data: Dict[str, Any]


@router.post("/process-with-claude", response_model=ClaudeProcessResponse)
async def process_with_claude(
    request: ClaudeProcessRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Process a document directly with Claude AI

    This endpoint:
    1. Retrieves the uploaded document
    2. Extracts text using Google Document AI
    3. Sends the text to Claude with the custom prompt
    4. Returns the structured response
    """
    try:
        logger.info(f"Processing document {request.document_id} with Claude")

        # Get the document from database
        doc_uuid = uuid.UUID(request.document_id)
        document = await db.get(Document, doc_uuid)

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Read the PDF file and encode it as base64
        logger.info(f"Reading and encoding PDF file: {document.file_path}")
        try:
            with open(document.file_path, "rb") as pdf_file:
                pdf_base64 = base64.b64encode(pdf_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to read or encode PDF file: {e}")
            raise HTTPException(status_code=500, detail="Could not read the PDF file for processing.")
        
        logger.info(f"PDF encoded to base64 string of length {len(pdf_base64)}")

        # Prepare the full prompt for Claude
        base_prompt = _get_base_prompt()
        final_instruction = f"""
        Please provide a structured JSON response with the following fields:
        {{
            "total_area_sqft": <number>,
            "roof_type": "<string>",
            "materials": ["<list of materials>"],
            "special_requirements": ["<list of requirements>"],
            "complexity": "<low|medium|high>",
            "measurements": [
                {{"description": "<string>", "value": <number>, "unit": "<string>"}}
            ],
            "key_findings": ["<list of important findings>"],
            "estimated_cost_range": {{"min": <number>, "max": <number>}},
            "confidence_score": <0.0-1.0>
        }}
        """
        
        # Construct the multimodal message for Claude
        message_content = [
            {
                "type": "document",
                "source": {
                    "type": "base64",
                    "media_type": "application/pdf",
                    "data": pdf_base64,
                },
            },
            {"type": "text", "text": base_prompt},
            {"type": "text", "text": final_instruction},
        ]

        # Send to Claude for analysis
        logger.info("Sending to Claude for analysis")

        if not claude_service.client:
            raise HTTPException(
                status_code=500,
                detail="Claude API not configured"
            )

        response = claude_service.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": message_content
            }]
        )

        # Parse Claude's response
        claude_text = response.content[0].text
        logger.info(f"Received response from Claude: {len(claude_text)} characters")

        # Try to extract JSON from the response
        import json
        import re

        try:
            # Look for JSON in the response
            json_match = re.search(r'\{[\s\S]*\}', claude_text)
            if json_match:
                extracted_data = json.loads(json_match.group())
            else:
                # Fallback: create structured data from text response
                extracted_data = {
                    "raw_response": claude_text,
                    "total_area_sqft": 0,
                    "confidence_score": 0.5,
                    "key_findings": [claude_text[:500]]
                }
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from Claude response")
            extracted_data = {
                "raw_response": claude_text,
                "parsing_error": "Could not extract structured data"
            }

        # Create and save the results to the database so the estimate page can load them
        new_results = ProcessingResults(
            id=uuid.uuid4(),
            document_id=doc_uuid,
            roof_area_sqft=extracted_data.get("total_area_sqft"),
            estimated_cost=extracted_data.get("estimated_cost_range", {}).get("max"),
            confidence_score=extracted_data.get("confidence_score"),
            materials=extracted_data.get("materials"),
            roof_features=extracted_data.get("special_requirements"),
            complexity_factors=[extracted_data.get("complexity")] if extracted_data.get("complexity") else [],
            processing_time_seconds=(datetime.utcnow() - document.created_at).total_seconds(),
            stages_completed=["claude_direct_process"],
            extraction_method="google_document_ai",
            ai_interpretation=claude_text,
            recommendations=extracted_data.get("key_findings"),
            warnings=[],
            errors=[]
        )
        db.add(new_results)

        # Update document status
        document.processing_status = ProcessingStatus.COMPLETED
        document.processing_metadata = {
            "claude_processed": True,
            "extraction_method": "claude_direct_pdf",
            "prompt_used": base_prompt[:200]
        }

        await db.commit()

        # Prepare response
        return ClaudeProcessResponse(
            document_id=request.document_id,
            status="success",
            claude_response={
                "model": "claude-3-5-sonnet-20241022",
                "response_length": len(claude_text),
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            },
            extracted_data=extracted_data
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing document with Claude: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {str(e)}"
        )


@router.get("/claude-status")
async def get_claude_status():
    """Check if Claude API is configured and working"""
    try:
        is_configured = claude_service.client is not None

        if is_configured:
            # Try a simple test message
            test_response = claude_service.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=50,
                messages=[{
                    "role": "user",
                    "content": "Reply with 'OK' if you're working"
                }]
            )
            is_working = 'OK' in test_response.content[0].text
        else:
            is_working = False

        return {
            "configured": is_configured,
            "working": is_working,
            "model": "claude-3-5-sonnet-20241022"
        }
    except Exception as e:
        return {
            "configured": False,
            "working": False,
            "error": str(e)
        }