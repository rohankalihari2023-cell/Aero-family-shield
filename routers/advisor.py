"""
advisor.py
Generative AI clinical advisor and environmental copilot endpoint.
"""

from typing import Dict, Any

from fastapi import APIRouter

from models.schemas import ChatRequestSchema
from services.ai_engine import generate_ai_response
from services.smog_service import get_city_data
from services.security import sanitize_string

router = APIRouter(tags=["AI Advisor"])


@router.post(
    "/api/advisor/chat",
    summary="Consult GenAI Clinical Environmental Advisor",
    description="Synthesizes actionable clinical and behavioral advice grounded in real-time smog data and household vulnerabilities."
)
def chat_with_advisor(req: ChatRequestSchema) -> Dict[str, Any]:
    """Generates context-aware clinical air quality recommendations using Gemini 1.5 Flash or clinical fallback.

    Args:
        req (ChatRequestSchema): Validated user inquiry, city key, household vulnerability profile, and optional API key.

    Returns:
        Dict[str, Any]: Structured response containing markdown advisory content, source model attribution, and city context.

    Examples:
        >>> req = ChatRequestSchema(message="Is it safe for asthmatic child to walk outside?")
        >>> res = chat_with_advisor(req)
        >>> "response" in res
        True
    """
    city_data = get_city_data(req.cityKey) or get_city_data("delhi") or {}
    prof_dict = req.familyProfile.to_dict() if req.familyProfile else None
    clean_message = sanitize_string(req.message, max_len=3000)

    return generate_ai_response(
        message=clean_message,
        city=city_data,
        profile=prof_dict,
        api_key=req.apiKey,
    )
