import anthropic
import logging
import json
from app.core.config import settings

logger = logging.getLogger(__name__)

class ClaudeService:
    """A service for interacting with the Anthropic Claude API."""

    def __init__(self):
        if not settings.ANTHROPIC_API_KEY or "your-anthropic-api-key" in settings.ANTHROPIC_API_KEY:
            logger.warning("ANTHROPIC_API_KEY is not set or is a placeholder.")
            self.client = None
        else:
            self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    def analyze_text_for_estimate(self, text: str) -> dict:
        """Analyzes extracted text to find roofing measurements and details."""
        if not self.client:
            raise ConnectionError("Claude client is not initialized. Check ANTHROPIC_API_KEY.")

        logger.info("Sending text to Claude for analysis...")
        prompt = f"""
Human: You are an expert in analyzing construction blueprints for roofing estimates. From the following text extracted from a blueprint, identify and extract key information for a roofing estimate. Provide the output in a structured JSON format.

The JSON should include keys for: 'total_roof_area_sqft', 'roof_pitch', 'materials', 'measurements' (a list of objects with 'label' and 'value'), and 'summary'. If any information is not found, use a value of null.

Here is the text (first 10,000 characters):
---
{text[:10000]}
---

Assistant:
"""
        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = message.content[0].text
            try:
                analysis_result = json.loads(response_text)
                logger.info("Successfully received and parsed analysis from Claude.")
                return analysis_result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from Claude response. Error: {e}. Response: '{response_text}'")
                raise ValueError("Received invalid JSON from AI service") from e
        except Exception as e:
            logger.error(f"Error calling or parsing from Claude API: {e}", exc_info=True)
            raise

claude_service = ClaudeService()