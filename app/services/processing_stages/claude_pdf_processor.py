import logging
from typing import Dict, Any, List
import PyPDF2
import json
import re
import base64
from pathlib import Path

from app.services.claude_service import claude_service, async_claude_client
from app.models.processing import AIInterpretation
from app.services.pdf_splitter import pdf_splitter

logger = logging.getLogger(__name__)

class ClaudePDFProcessor:
    """
    A processor that sends the entire PDF content to Claude for direct,
    single-shot analysis and interpretation.
    """

    def __init__(self):
        # This service might be called from a sync (Celery) or async (API) context.
        # We will use the appropriate client.
        self.sync_claude_client = claude_service.client
        self.async_claude_client = async_claude_client

    async def process_pdf_direct(self, file_path: str) -> AIInterpretation:
        """
        Processes a PDF by splitting it into chunks and sending each to Claude for analysis.
        This method is designed to handle large files without causing memory exhaustion.

        Args:
            file_path: The local path to the PDF file.

        Returns:
            A merged AIInterpretation object from all processed chunks.
        """
        logger.info(f"Starting direct-to-Claude processing for: {file_path}")

        try:
            # 1. Use the PDF splitter to handle large files safely.
            chunks = pdf_splitter.split_pdf(file_path)
            all_chunk_responses = []

            final_instruction = self._get_final_instruction_prompt()

            for chunk in chunks:
                logger.info(f"Processing chunk {chunk['chunk_index'] + 1}/{len(chunks)} for {file_path}")
                # Use the async client since this method is async
                chunk_response = await self._process_chunk_with_claude(chunk['file_path'], final_instruction, use_async=True)
                all_chunk_responses.append(chunk_response)

            # 2. Merge the results from all chunks
            merged_data = self._merge_claude_responses(all_chunk_responses)
            
            # 3. Clean up temporary chunk files
            pdf_splitter.cleanup_chunks(chunks)

            # 4. Return as a single AIInterpretation object
            return AIInterpretation.model_validate(merged_data)

        except Exception as e:
            logger.exception(f"Direct-to-Claude processing failed for {file_path}")
            raise

    def _get_base_prompt(self) -> str:
        """Loads the master prompt from the filesystem."""
        try:
            prompt_path = Path(__file__).parent.parent.parent / "prompts" / "roofing_estimation_prompt.txt"
            with open(prompt_path, "r") as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Could not load prompt file: {e}. Using fallback prompt.")
            return "You are an expert roofing estimator. Analyze the document and extract key information for a cost estimate."

    def _get_final_instruction_prompt(self) -> str:
        """Returns the final JSON structure instruction for the prompt."""
        return """
        Please provide a structured JSON response with the following fields:
        {{
            "roof_area_sqft": <number>,
            "roof_pitch": "<string>",
            "materials": [{{"type": "<string>", "quantity": <number>, "condition": "<string>"}}],
            "measurements": [{{"label": "<string>", "value": <number>, "unit": "<string>"}}],
            "damage_assessment": {{"severity": "<low|medium|high>", "damage_types": ["<string>"]}},
            "special_requirements": ["<string>"],
            "roof_features": [{{"type": "<string>", "count": <number>, "impact": "<string>"}}],
            "complexity_factors": ["<string: e.g., 'steep_pitch', 'multiple_levels'>"],
            "confidence": <number between 0.0 and 1.0>
        }}
        """

    async def _process_chunk_with_claude(self, file_path: str, instruction: str, use_async: bool = False) -> Dict[str, Any]:
        """Sends a single PDF chunk to Claude for analysis."""
        base_prompt = self._get_base_prompt()
        try:
            with open(file_path, "rb") as pdf_file:
                pdf_base64 = base64.b64encode(pdf_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to read or encode PDF chunk {file_path}: {e}")
            return {"raw_response": f"Error reading chunk: {e}", "parsing_error": "File read error"}

        message_content = [
            {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_base64}},
            {"type": "text", "text": base_prompt},
            {"type": "text", "text": instruction},
        ]

        client = self.async_claude_client if use_async else self.sync_claude_client
        if not client:
            raise ConnectionError("Claude API client not configured")

        if use_async:
            response = await client.messages.create(model="claude-3-5-sonnet-20241022", max_tokens=2000, messages=[{"role": "user", "content": message_content}])
        else:
            response = client.messages.create(model="claude-3-5-sonnet-20241022", max_tokens=2000, messages=[{"role": "user", "content": message_content}])

        claude_text = response.content[0].text
        try:
            json_match = re.search(r'\{[\s\S]*\}', claude_text)
            if json_match:
                extracted_data = json.loads(json_match.group())
            else:
                extracted_data = {"raw_response": claude_text}
        except json.JSONDecodeError:
            extracted_data = {"raw_response": claude_text, "parsing_error": "Could not extract JSON"}

        extracted_data["usage"] = {"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens}
        return extracted_data

    def _merge_claude_responses(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merges structured data from multiple Claude responses."""
        if not responses: return {}
        merged = {"total_area_sqft": 0, "roof_type": "", "materials": [], "special_requirements": [], "complexity": "low", "measurements": [], "key_findings": [], "estimated_cost_range": {"min": 0, "max": 0}, "confidence_score": 0}
        if not responses:
            return {}

        # This structure must match the AIInterpretation model
        merged = {
            "roof_area_sqft": 0,
            "roof_pitch": None,
            "materials": [],
            "measurements": [],
            "damage_assessment": None,
            "special_requirements": [],
            "roof_features": [],
            "complexity_factors": [],
            "confidence": 0.0,
            "interpretation_method": "claude_direct_pdf",
            "metadata": {}
        }

        all_confidences = []
        material_types_seen = set()

        for resp in responses:
            merged["total_area_sqft"] += resp.get("total_area_sqft", 0)
            if resp.get("roof_type") and not merged["roof_type"]: merged["roof_type"] = resp["roof_type"]
            merged["materials"].extend(resp.get("materials", []))
            if resp.get("roof_pitch") and not merged["roof_pitch"]:
                merged["roof_pitch"] = resp.get("roof_pitch")
            
            # Correctly deduplicate list of dictionaries
            for material in resp.get("materials", []):
                if material.get("type") not in material_types_seen:
                    merged["materials"].append(material)
                    material_types_seen.add(material.get("type"))

            merged["special_requirements"].extend(resp.get("special_requirements", []))
            merged["measurements"].extend(resp.get("measurements", []))
            merged["key_findings"].extend(resp.get("key_findings", []))
            if resp.get("confidence_score"): all_confidences.append(resp["confidence_score"])
        merged["materials"] = list(set(merged["materials"]))
            if resp.get("confidence"):
                all_confidences.append(resp["confidence"])
        
        merged["special_requirements"] = list(set(merged["special_requirements"]))
        if all_confidences: merged["confidence_score"] = sum(all_confidences) / len(all_confidences)
        if all_confidences:
            merged["confidence"] = sum(all_confidences) / len(all_confidences)

        return merged

claude_pdf_processor = ClaudePDFProcessor()