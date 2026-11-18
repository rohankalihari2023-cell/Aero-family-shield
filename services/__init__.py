"""
AeroFamily Services Package
Domain-specific modules for atmospheric modeling, GenAI advisory, IAQ engineering,
exposure calculation, input security, and community incident reporting.
"""

from .smog_service import (
    CITIES_REGISTRY,
    WHO_GUIDELINES,
    calculate_diurnal_curve,
    get_city_data,
    register_custom_city,
    process_current_location_weather,
)
from .ai_engine import (
    generate_ai_response,
    generate_offline_reasoning,
    build_vulnerability_summary,
    query_gemini_api,
)
from .routine_service import generate_daily_routine
from .iaq_service import calculate_cadr_requirements, evaluate_humidifier_safety
from .impact_service import simulate_lifestyle_impact
from .security import (
    SECURITY_HEADERS,
    sanitize_string,
    validate_numeric_bounds,
    sanitize_profile_dict,
)
from .community_service import get_community_feed, create_incident_report

__all__ = [
    "CITIES_REGISTRY",
    "WHO_GUIDELINES",
    "calculate_diurnal_curve",
    "get_city_data",
    "register_custom_city",
    "process_current_location_weather",
    "generate_ai_response",
    "generate_offline_reasoning",
    "build_vulnerability_summary",
    "query_gemini_api",
    "generate_daily_routine",
    "calculate_cadr_requirements",
    "evaluate_humidifier_safety",
    "simulate_lifestyle_impact",
    "SECURITY_HEADERS",
    "sanitize_string",
    "validate_numeric_bounds",
    "sanitize_profile_dict",
    "get_community_feed",
    "create_incident_report",
]
